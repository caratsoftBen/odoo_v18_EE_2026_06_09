from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    igm_forecast_enabled = fields.Boolean(
        string='Generate Recurring Task Forecast', default=True,
        help='When enabled, the scheduled action populates open recurring tasks '
             'up to the forecast horizon.')
    igm_forecast_horizon_days = fields.Integer(
        string='Forecast Horizon (days)', default=30,
        help='Tasks are generated up to today + this many days.')
    igm_forecast_skip_holidays = fields.Boolean(
        string='Skip Public Holidays', default=True,
        help='Do not create occurrences that fall on a public holiday '
             '(Time Off → Public Holidays).')
