from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    x_footer_enabled = fields.Boolean(
        string='Enable UHG Document Footer',
        help='Show the custom legal footer (logos + company details) on this '
             'company\'s PDF documents.',
    )
    x_footer_manager = fields.Char(string='Managing Director')
    x_footer_phone = fields.Char(string='Footer Phone')
    x_footer_fax = fields.Char(string='Footer Fax')
    x_footer_email = fields.Char(string='Footer Email')
    x_footer_seat = fields.Char(string='Registered Seat')
    x_footer_register_court = fields.Char(string='Register Court')
    x_footer_registry = fields.Char(string='Registration Number')
    x_footer_tax_number = fields.Char(string='Tax Number')
    x_footer_vat = fields.Char(string='VAT / USt-ID')
    x_footer_bank_name = fields.Char(string='Bank Name')
    x_footer_iban = fields.Char(string='IBAN')
    x_footer_bic = fields.Char(string='BIC')
