from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    x_forecast_enabled = fields.Boolean(
        related='company_id.x_forecast_enabled', readonly=False)
    x_forecast_horizon_days = fields.Integer(
        related='company_id.x_forecast_horizon_days', readonly=False)
    x_forecast_skip_holidays = fields.Boolean(
        related='company_id.x_forecast_skip_holidays', readonly=False)
