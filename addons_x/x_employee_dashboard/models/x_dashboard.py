from odoo import models, fields, api

class XEmployeeDashboard(models.TransientModel):
    _name = 'x.employee.dashboard'
    _description = 'Employee Workspace Engine'

    name = fields.Char(default="My Center")
    x_field_service_count = fields.Integer(compute='_compute_field_service_tasks', string="Active Field Tasks")

    def _compute_field_service_tasks(self):
        for rec in self:
            rec.x_field_service_count = self.env['project.task'].search_count([
                ('user_ids', 'in', self.env.user.id),
                ('is_fsm', '=', True),
                ('stage_id.is_closed', '=', False)
            ]) 
            
               
