import logging
from datetime import datetime, time, timedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProjectTaskRecurrence(models.Model):
    _inherit = 'project.task.recurrence'

    @api.model
    def _cron_generate_forecast(self):
        """Scheduled entry point: extend every recurring task series to the horizon.

        Forecasting keys off the task's ``recurring_task`` flag and a per-series
        grouping (scope + name + weekday), not the ``recurrence_id`` link, so
        copied/standalone recurring tasks are covered too.
        """
        company = self.env.company
        if not company.igm_forecast_enabled:
            return False

        today = fields.Date.context_today(self)
        horizon = today + timedelta(days=company.igm_forecast_horizon_days or 30)
        skip_dates = set()
        if company.igm_forecast_skip_holidays:
            skip_dates = self._igm_get_holiday_dates(today, horizon, company)

        self.env['project.task']._igm_generate_forecast(today, horizon, skip_dates)
        return True

    @api.model
    def _igm_get_holiday_dates(self, start, end, company):
        """Set of public-holiday dates in [start, end].

        Public holidays are the Time Off app's public holidays, stored as
        ``resource.calendar.leaves`` with no employee (``resource_id = False``).
        Partner-specific days off can later be merged into the same skip set.
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
