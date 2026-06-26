from odoo import models


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
