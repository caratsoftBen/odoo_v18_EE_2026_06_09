from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _compute_display_sign_report_buttons(self):
        super()._compute_display_sign_report_buttons()
        if self.env.user.has_group('igm_fsm.group_fsm_cleaner'):
            for task in self:
                task.display_sign_report_primary = False
                task.display_sign_report_secondary = False

    def _compute_display_send_report_buttons(self):
        super()._compute_display_send_report_buttons()
        if self.env.user.has_group('igm_fsm.group_fsm_cleaner'):
            for task in self:
                task.display_send_report_primary = False
                task.display_send_report_secondary = False

    def action_igm_cleaner_done(self):
        self.ensure_one()
        if self.timer_start:
            self.action_timer_stop()
        if self.allow_timesheets and not self.total_hours_spent and self.allocated_hours:
            self.env['account.analytic.line'].create({
                'task_id': self.id,
                'project_id': self.project_id.id,
                'name': self.name or '/',
                'unit_amount': self.allocated_hours,
                'date': fields.Date.context_today(self),
            })
        return self.action_fsm_validate()
