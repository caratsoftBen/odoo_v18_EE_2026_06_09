from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    x_footer_enabled = fields.Boolean(
        related='company_id.x_footer_enabled', readonly=False)
    x_footer_manager = fields.Char(
        related='company_id.x_footer_manager', readonly=False)
    x_footer_phone = fields.Char(
        related='company_id.x_footer_phone', readonly=False)
    x_footer_fax = fields.Char(
        related='company_id.x_footer_fax', readonly=False)
    x_footer_email = fields.Char(
        related='company_id.x_footer_email', readonly=False)
    x_footer_seat = fields.Char(
        related='company_id.x_footer_seat', readonly=False)
    x_footer_register_court = fields.Char(
        related='company_id.x_footer_register_court', readonly=False)
    x_footer_registry = fields.Char(
        related='company_id.x_footer_registry', readonly=False)
    x_footer_tax_number = fields.Char(
        related='company_id.x_footer_tax_number', readonly=False)
    x_footer_vat = fields.Char(
        related='company_id.x_footer_vat', readonly=False)
    x_footer_bank_name = fields.Char(
        related='company_id.x_footer_bank_name', readonly=False)
    x_footer_iban = fields.Char(
        related='company_id.x_footer_iban', readonly=False)
    x_footer_bic = fields.Char(
        related='company_id.x_footer_bic', readonly=False)
