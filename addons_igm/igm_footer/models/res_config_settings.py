from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    igm_footer_enabled = fields.Boolean(
        related='company_id.igm_footer_enabled', readonly=False)
    igm_footer_manager = fields.Char(
        related='company_id.igm_footer_manager', readonly=False)
    igm_footer_phone = fields.Char(
        related='company_id.igm_footer_phone', readonly=False)
    igm_footer_fax = fields.Char(
        related='company_id.igm_footer_fax', readonly=False)
    igm_footer_email = fields.Char(
        related='company_id.igm_footer_email', readonly=False)
    igm_footer_seat = fields.Char(
        related='company_id.igm_footer_seat', readonly=False)
    igm_footer_register_court = fields.Char(
        related='company_id.igm_footer_register_court', readonly=False)
    igm_footer_registry = fields.Char(
        related='company_id.igm_footer_registry', readonly=False)
    igm_footer_tax_number = fields.Char(
        related='company_id.igm_footer_tax_number', readonly=False)
    igm_footer_vat = fields.Char(
        related='company_id.igm_footer_vat', readonly=False)
    igm_footer_bank_name = fields.Char(
        related='company_id.igm_footer_bank_name', readonly=False)
    igm_footer_iban = fields.Char(
        related='company_id.igm_footer_iban', readonly=False)
    igm_footer_bic = fields.Char(
        related='company_id.igm_footer_bic', readonly=False)
