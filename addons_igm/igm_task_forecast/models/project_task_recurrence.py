import logging
from datetime import datetime, time, timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

# Hard cap on occurrences created per recurrence in a single run, as a guard
# against accidental infinite loops (e.g. a daily recurrence with a huge horizon).
_MAX_PER_RECURRENCE = 1000


class ProjectTaskRecurrence(models.Model):
    _inherit = 'project.task.recurrence'

    @api.model
    def _cron_generate_forecast(self):
        """Scheduled entry point: extend every open recurrence up to the horizon."""
        company = self.env.company
        if not company.igm_forecast_enabled:
            return False

        today = fields.Date.context_today(self)
        horizon = today + timedelta(days=company.igm_forecast_horizon_days or 30)
        holidays = set()
        if company.igm_forecast_skip_holidays:
            holidays = self._igm_get_holiday_dates(today, horizon, company)

        for recurrence in self.search([]):
            try:
                with self.env.cr.savepoint():
                    recurrence._igm_extend_to_horizon(today, horizon, holidays)
            except Exception:
                _logger.exception(
                    "Task forecast: failed to extend recurrence %s", recurrence.id)
        return True

    def _igm_extend_to_horizon(self, today, horizon, holidays):
        """Create occurrences for this recurrence up to ``horizon``.

        Relies on the native ``_create_next_occurrence`` so all field copying
        (partner, planned dates, subtasks, ...) stays consistent. Occurrences on
        public holidays are removed afterwards so the cadence is preserved.
        """
        self.ensure_one()
        if self.repeat_type == 'until' and self.repeat_until and self.repeat_until < today:
            return

        delta = self._get_recurrence_delta()
        recurrence = self.with_context(
            tracking_disable=True, mail_create_nolog=True, mail_auto_subscribe_no_notify=True)

        for _i in range(_MAX_PER_RECURRENCE):
            last = self.env['project.task'].search(
                [('recurrence_id', '=', self.id)], order='id desc', limit=1)
            if not last or not last.date_deadline:
                break
            next_deadline = last.date_deadline + delta
            if next_deadline.date() > horizon:
                break
            if self.repeat_type == 'until' and self.repeat_until and next_deadline.date() > self.repeat_until:
                break
            recurrence._create_next_occurrence(last)
            # Stop if nothing new was created (avoids an endless loop).
            new_last = self.env['project.task'].search(
                [('recurrence_id', '=', self.id)], order='id desc', limit=1)
            if new_last.id == last.id:
                break

        if holidays:
            def _is_on_holiday(task):
                day = self._igm_service_date(task)
                return bool(day) and day >= today and day in holidays

            on_holiday = self.env['project.task'].search(
                [('recurrence_id', '=', self.id)]
            ).filtered(_is_on_holiday)
            if on_holiday:
                on_holiday.with_context(tracking_disable=True).unlink()

    @api.model
    def _igm_service_date(self, task):
        """Return the date the work is scheduled on (planned start, else deadline)."""
        dt = False
        if 'planned_date_begin' in task._fields and task.planned_date_begin:
            dt = task.planned_date_begin
        elif task.date_deadline:
            dt = task.date_deadline
        return dt.date() if dt else False

    @api.model
    def _igm_get_holiday_dates(self, start, end, company):
        """Set of public-holiday dates in [start, end].

        Public holidays are the Time Off app's public holidays, stored as
        ``resource.calendar.leaves`` with no employee (``resource_id = False``).
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
