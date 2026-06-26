from odoo import api, models, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def create_user_for_cleaning_service(self, payload):
        """Provision an internal user for the cleaning field-service GUI.

        Stable, RPC-callable façade: callers send their own vocabulary and never
        Odoo ids. Creates partner + user + employee, grants the Cleaner group,
        and optionally an hr.contract. Idempotent on ``email`` (= login).

        payload keys:
          email      (str, required) -> login + work_email
          name       (str)           -> full name; or first_name/last_name
          first_name (str)
          last_name  (str)
          password   (str)           -> initial login password (optional)
          phone      (str)           -> mobile
          job_title  (str)
          department (str)           -> resolved by name; ignored if unknown
          lang       (str)           -> e.g. 'de_DE'
          tz         (str)           -> e.g. 'Europe/Berlin'
          contract   (dict)          -> {wage (required), date_start, reference, state}

        returns: {status, login, user_id, partner_id, employee_id, contract_id}
        """
        email = (payload.get('email') or '').strip()
        if not email:
            raise UserError(_("'email' is required to create a cleaning-service user."))

        name = (payload.get('name') or '').strip()
        if not name:
            name = ' '.join(
                part for part in (payload.get('first_name'), payload.get('last_name')) if part
            ).strip()
        if not name:
            raise UserError(_("A name is required: provide 'name', or 'first_name'/'last_name'."))

        existing = self.sudo().search([('login', '=', email)], limit=1)
        if existing:
            employee = self.env['hr.employee'].sudo().search([('user_id', '=', existing.id)], limit=1)
            return {
                'status': 'existing',
                'login': existing.login,
                'user_id': existing.id,
                'partner_id': existing.partner_id.id,
                'employee_id': employee.id or False,
                'contract_id': False,
            }

        company = self.env.company
        cleaner_group = self.env.ref('igm_fsm.group_fsm_cleaner')
        internal_group = self.env.ref('base.group_user')

        user_vals = {
            'name': name,
            'login': email,
            'email': email,
            'company_id': company.id,
            'company_ids': [(6, 0, company.ids)],
        }
        for key in ('lang', 'tz', 'password'):
            if payload.get(key):
                user_vals[key] = payload[key]
        user = self.create(user_vals)
        user.write({'groups_id': [(6, 0, [internal_group.id, cleaner_group.id])]})

        employee_vals = {
            'name': name,
            'user_id': user.id,
            'company_id': company.id,
            'work_email': email,
        }
        if payload.get('phone'):
            employee_vals['mobile_phone'] = payload['phone']
        if payload.get('job_title'):
            employee_vals['job_title'] = payload['job_title']
        if payload.get('department'):
            department = self.env['hr.department'].search(
                [('name', '=', payload['department']), ('company_id', 'in', (company.id, False))],
                limit=1,
            )
            if department:
                employee_vals['department_id'] = department.id
        employee = self.env['hr.employee'].create(employee_vals)

        contract_id = False
        contract = payload.get('contract')
        if contract:
            if not contract.get('wage'):
                raise UserError(_("'contract.wage' is required when a contract is provided."))
            contract_vals = {
                'name': contract.get('reference') or _("%s – Reinigung", name),
                'employee_id': employee.id,
                'wage': contract['wage'],
                'company_id': company.id,
                'state': contract.get('state', 'draft'),
            }
            if contract.get('date_start'):
                contract_vals['date_start'] = contract['date_start']
            contract_id = self.env['hr.contract'].create(contract_vals).id

        return {
            'status': 'created',
            'login': user.login,
            'user_id': user.id,
            'partner_id': user.partner_id.id,
            'employee_id': employee.id,
            'contract_id': contract_id,
        }
