import logging
from datetime import datetime, time, timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Guard against a runaway loop (e.g. a daily cadence with a long horizon).
_MAX_PER_RECURRENCE = 366


class ProjectTaskRecurrence(models.Model):
    _inherit = 'project.task.recurrence'

    igm_forecast_until = fields.Date(
        string="Forecast Generated Until",
        help="High-water mark: the forecast has authoritatively planned this "
             "series through this date. The standard on-completion recurrence "
             "defers to the forecast up to here and falls back to native "
             "behaviour beyond it.")

    def _create_next_occurrence(self, occurrence_from):
        """Defer to the forecast when it already owns the next interval.

        The forecast cron is the source of truth up to ``igm_forecast_until``;
        within that window generation is left to it (which is off-day aware).
        Beyond it -- forecast off, behind, or never run for this series -- the
        native mechanism takes over as a safety net.
        """
        if self.igm_forecast_until and occurrence_from.date_deadline:
            next_date = (occurrence_from.date_deadline + self._get_recurrence_delta()).date()
            if next_date <= self.igm_forecast_until:
                return
        return super()._create_next_occurrence(occurrence_from)

    @api.model
    def _cron_generate_forecast(self):
        """Scheduled entry point: extend every recurrence up to the horizon."""
        company = self.env.company
        if not company.igm_forecast_enabled:
            return False

        today = fields.Date.context_today(self)
        horizon = today + timedelta(days=company.igm_forecast_horizon_days or 30)
        off_dates = set()
        if company.igm_forecast_skip_holidays:
            off_dates = self._igm_get_off_dates(today, horizon, company)

        for recurrence in self.search([]):
            try:
                with self.env.cr.savepoint():
                    recurrence._igm_extend_to_horizon(today, horizon, off_dates)
            except Exception:
                _logger.exception("Task forecast: recurrence %s failed", recurrence.id)
        return True

    def _igm_extend_to_horizon(self, today, horizon, off_dates):
        """Create the missing active occurrences of this series up to ``horizon``.

        No task is created on an off-day; the gap is intentional and its reason
        lives in the off-day source record. ``igm_forecast_until`` is advanced to
        the horizon so the standard mechanism knows this window is covered.
        """
        self.ensure_one()
        tasks = self.task_ids
        if not tasks:
            return
        template = max(tasks, key=lambda t: t._igm_service_dt() or datetime.min)
        has_begin = 'planned_date_begin' in template._fields
        begin = template.planned_date_begin if has_begin else False
        deadline = template.date_deadline
        if not (begin or deadline):
            return

        delta = self._get_recurrence_delta()
        existing = {t._igm_service_dt().date() for t in tasks if t._igm_service_dt()}
        for n in range(1, _MAX_PER_RECURRENCE + 1):
            shift = delta * n
            cand_begin = begin + shift if begin else False
            cand_deadline = deadline + shift if deadline else False
            day = (cand_begin or cand_deadline).date()
            if day > horizon:
                break
            if day < today or day in existing or day in off_dates:
                continue
            template._igm_create_occurrence(cand_begin, cand_deadline, self)
            existing.add(day)

        if not self.igm_forecast_until or self.igm_forecast_until < horizon:
            self.igm_forecast_until = horizon

    @api.model
    def _igm_get_off_dates(self, start, end, company):
        """Set of non-service dates in [start, end].

        Currently the company's public holidays and closures, stored as
        ``resource.calendar.leaves`` with no resource (``resource_id = False``).
        Customer-specific service exceptions are merged in here once modelled.
        """
        domain = [
            ('resource_id', '=', False),
            ('date_from', '<=', datetime.combine(end, time.max)),
            ('date_to', '>=', datetime.combine(start, time.min)),
            '|', ('company_id', '=', company.id), ('company_id', '=', False),
        ]
        dates = set()
        for leave in self.env['resource.calendar.leaves'].search(domain):
            day = leave.date_from.date()
            last_day = leave.date_to.date()
            while day <= last_day:
                dates.add(day)
                day += timedelta(days=1)
        return dates
