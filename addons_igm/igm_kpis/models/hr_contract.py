from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    igm_max_hours_per_month = fields.Float(
        string="Max Working Hours / Month",
        help="Contractual ceiling on paid working hours per calendar month "
             "(e.g. 40 h for a German Minijob). Leave at 0 to fall back to the "
             "hours implied by the working schedule.",
    )
