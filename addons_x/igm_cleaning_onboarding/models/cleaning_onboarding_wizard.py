from odoo import fields, models, _


class CleaningOnboardingWizard(models.TransientModel):
    _name = 'igm.cleaning.onboarding.wizard'
    _description = 'Create Cleaning-Service User'

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    email = fields.Char(string="Email", required=True)
    phone = fields.Char(string="Mobile")
    job_title = fields.Char()
    department_id = fields.Many2one('hr.department', string="Department")
    lang = fields.Selection(
        selection=lambda self: self.env['res.lang'].get_installed(),
        string="Language",
        default=lambda self: self.env.lang,
    )
    password = fields.Char(string="Initial Password")
    create_contract = fields.Boolean(string="Create employment contract")
    wage = fields.Float(string="Monthly Wage")
    contract_date_start = fields.Date(string="Contract Start", default=fields.Date.context_today)

    def action_create_cleaner(self):
        self.ensure_one()
        payload = {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone or False,
            'job_title': self.job_title or False,
            'department': self.department_id.name or False,
            'lang': self.lang or False,
            'password': self.password or False,
        }
        if self.create_contract:
            payload['contract'] = {
                'wage': self.wage,
                'date_start': self.contract_date_start and fields.Date.to_string(self.contract_date_start),
                'state': 'draft',
            }
        result = self.env['res.users'].create_user_for_cleaning_service(payload)
        return {
            'type': 'ir.actions.act_window',
            'name': _("Cleaner"),
            'res_model': 'res.users',
            'res_id': result['user_id'],
            'view_mode': 'form',
            'target': 'current',
        }
