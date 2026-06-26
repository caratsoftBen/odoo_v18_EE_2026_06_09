from datetime import datetime, time

from odoo import models, fields, api


class XEmployeeDashboard(models.TransientModel):
    _name = 'x.employee.dashboard'
    _description = 'Employee Workspace Engine'

    name = fields.Char(default="My Center")
    x_field_service_count = fields.Integer(compute='_compute_field_service_tasks', string="Active Field Tasks")

    def _get_field_service_domain(self):
        today = fields.Date.context_today(self)
        today_start = datetime.combine(today, time.min)
        today_end = datetime.combine(today, time.max)
        return [
            ('is_fsm', '=', True),
            ('project_id', '!=', False),
            ('display_in_project', '=', True),
            ('user_ids', 'in', self.env.user.id),
            '|',
                '&',
                    ('planned_date_begin', '<=', today_end),
                    ('date_deadline', '>=', today_start),
                ('planned_date_begin', '>=', today_start),
        ]

    @api.depends_context('uid')
    def _compute_field_service_tasks(self):
        count = self.env['project.task'].search_count(self._get_field_service_domain())
        for rec in self:
            rec.x_field_service_count = count

    def action_open_field_service(self):
        return self.env['ir.actions.actions']._for_xml_id('industry_fsm.project_task_action_fsm')
