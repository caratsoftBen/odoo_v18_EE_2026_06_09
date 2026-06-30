import logging
from collections import defaultdict
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models

_logger = logging.getLogger(__name__)

# Guard against a runaway loop (e.g. a daily cadence with a long horizon).
_MAX_PER_SERIES = 366


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def _igm_generate_forecast(self, today, horizon, skip_dates):
        recurring = self.search([('recurring_task', '=', True)])
        series = defaultdict(lambda: self.browse())
        for task in recurring:
            key = task._igm_series_key()
            if key:
                series[key] |= task
        for key, members in series.items():
            try:
                with self.env.cr.savepoint():
                    members._igm_extend_series(today, horizon, skip_dates)
            except Exception:
                _logger.exception("Task forecast: series %s failed", key)

    def _igm_service_dt(self):
        self.ensure_one()
        if 'planned_date_begin' in self._fields and self.planned_date_begin:
            return self.planned_date_begin
        return self.date_deadline or False

    def _igm_series_key(self):
        self.ensure_one()
        service_dt = self._igm_service_dt()
        if not service_dt:
            return False
        return (self.project_id.id, self.name or '', service_dt.date().weekday())

    def _igm_repeat_delta(self):
        self.ensure_one()
        return relativedelta(**{f"{self.repeat_unit or 'week'}s": self.repeat_interval or 1})

    def _igm_extend_series(self, today, horizon, skip_dates):
        template = max(self, key=lambda t: t._igm_service_dt() or datetime.min)
        has_begin = 'planned_date_begin' in template._fields
        begin = template.planned_date_begin if has_begin else False
        deadline = template.date_deadline
        if not (begin or deadline):
            return
        delta = template._igm_repeat_delta()
        existing = {t._igm_service_dt().date() for t in self if t._igm_service_dt()}
        for n in range(1, _MAX_PER_SERIES + 1):
            shift = delta * n
            cand_begin = begin + shift if begin else False
            cand_deadline = deadline + shift if deadline else False
            day = (cand_begin or cand_deadline).date()
            if day > horizon:
                break
            if day < today or day in existing or day in skip_dates:
                continue
            template._igm_create_occurrence(cand_begin, cand_deadline)
            existing.add(day)

    def _igm_create_occurrence(self, begin, deadline):
        self.ensure_one()
        values = {'priority': '0'}
        if 'fsm_done' in self._fields:
            values['fsm_done'] = False
        if self.project_id.type_ids:
            values['stage_id'] = self.project_id.type_ids[0].id
        if begin and 'planned_date_begin' in self._fields:
            values['planned_date_begin'] = begin
        if deadline:
            values['date_deadline'] = deadline
        self.with_context(
            copy_project=True,
            mail_create_nolog=True,
            tracking_disable=True,
            mail_auto_subscribe_no_notify=True,
        ).copy(values)
