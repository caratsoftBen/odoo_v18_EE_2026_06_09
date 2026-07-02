from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def igm_api_ol_get_dashboard(self):
        user = self.env.user
        sites = self.env['res.partner'].search(
            [
                ('igm_is_cleaning_site', '=', True),
                ('igm_coordinator_id', '=', user.id),
            ],
            order='name',
        )
        today = fields.Date.context_today(self)
        start = fields.Datetime.to_datetime(today)
        end = start + timedelta(days=7)
        tasks = self.search(
            [
                ('is_fsm', '=', True),
                ('partner_id', 'in', sites.ids),
                ('planned_date_begin', '>=', start),
                ('planned_date_begin', '<', end),
            ],
            order='planned_date_begin asc, id asc',
        )
        tasks_by_site = {}
        for task in tasks:
            tasks_by_site.setdefault(task.partner_id.id, self.browse())
            tasks_by_site[task.partner_id.id] |= task
        kpi_service = self.env['igm.kpi']
        sites_dto = []
        for site in sites:
            site_tasks = tasks_by_site.get(site.id, self.browse())
            sites_dto.append({
                'id': site.id,
                'name': site.name or '',
                'address': site._igm_ol_address(),
                'taskCount': len(site_tasks),
                'kpi': kpi_service.task_allocation(site_tasks.ids),
                'tasks': [task._igm_ol_task_dto() for task in site_tasks],
            })
        return {
            'sites': sites_dto,
            'employees': self._igm_ol_team_employees(),
        }

    def _igm_ol_task_dto(self):
        self.ensure_one()
        return {
            'id': self.id,
            'title': self.name or '',
            'plannedStart': self.planned_date_begin.isoformat() if self.planned_date_begin else None,
            'plannedEnd': self.date_deadline.isoformat() if self.date_deadline else None,
            'allocatedHours': self.allocated_hours or 0.0,
            'recurring': bool(self.recurrence_id),
            'done': self.fsm_done,
            'assignees': [{
                'userId': u.id,
                'name': u.name or '',
                'initials': self._igm_ol_initials(u.name),
            } for u in self.user_ids],
        }

    @api.model
    def _igm_ol_team_employees(self):
        user = self.env.user
        domain = [('user_id', '!=', False)]
        if user.employee_id:
            domain.append(('parent_id', '=', user.employee_id.id))
            employees = self.env['hr.employee'].search(domain, order='name')
        else:
            employees = self.env['hr.employee'].search(domain, order='name', limit=100)
        return [{
            'id': emp.id,
            'userId': emp.user_id.id,
            'name': emp.name or '',
            'initials': self._igm_ol_initials(emp.name),
        } for emp in employees]

    def _igm_ol_initials(self, name):
        parts = (name or '').split()
        return ''.join((p[0] or '').upper() for p in parts[:2])

    def igm_api_ol_assign(self, employee_id):
        self.ensure_one()
        user = self._igm_ol_employee_user(employee_id)
        self.write({'user_ids': [(4, user.id)]})
        return self.igm_api_ol_get_dashboard()

    def igm_api_ol_substitute(self, employee_id, scope):
        self.ensure_one()
        user = self._igm_ol_employee_user(employee_id)
        if scope == 'series' and self.recurrence_id:
            tasks = self.recurrence_id.task_ids.filtered(lambda t: not t.fsm_done)
        else:
            tasks = self
        tasks.write({'user_ids': [(6, 0, user.ids)]})
        return self.igm_api_ol_get_dashboard()

    def _igm_ol_employee_user(self, employee_id):
        employee = self.env['hr.employee'].browse(employee_id)
        if not employee.exists() or not employee.user_id:
            raise UserError(_(
                "Dieser Mitarbeiter hat keinen verknüpften Benutzer und kann keiner Aufgabe "
                "zugewiesen werden."
            ))
        return employee.user_id
