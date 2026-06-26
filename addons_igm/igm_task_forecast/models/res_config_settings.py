from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    igm_forecast_enabled = fields.Boolean(
        related='company_id.igm_forecast_enabled', readonly=False)
    igm_forecast_horizon_days = fields.Integer(
        related='company_id.igm_forecast_horizon_days', readonly=False)
    igm_forecast_skip_holidays = fields.Boolean(
        related='company_id.igm_forecast_skip_holidays', readonly=False)
