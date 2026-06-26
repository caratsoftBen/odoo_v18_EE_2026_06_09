from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    igm_footer_enabled = fields.Boolean(
        string='Enable UHG Document Footer',
        help='Show the custom legal footer (logos + company details) on this '
             'company\'s PDF documents.',
    )
    igm_footer_manager = fields.Char(string='Managing Director')
    igm_footer_phone = fields.Char(string='Footer Phone')
    igm_footer_fax = fields.Char(string='Footer Fax')
    igm_footer_email = fields.Char(string='Footer Email')
    igm_footer_seat = fields.Char(string='Registered Seat')
    igm_footer_register_court = fields.Char(string='Register Court')
    igm_footer_registry = fields.Char(string='Registration Number')
    igm_footer_tax_number = fields.Char(string='Tax Number')
    igm_footer_vat = fields.Char(string='VAT / USt-ID')
    igm_footer_bank_name = fields.Char(string='Bank Name')
    igm_footer_iban = fields.Char(string='IBAN')
    igm_footer_bic = fields.Char(string='BIC')
