from odoo import models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    def _igm_service_dt(self):
        self.ensure_one()
        if 'planned_date_begin' in self._fields and self.planned_date_begin:
            return self.planned_date_begin
        return self.date_deadline or False

    def _igm_create_occurrence(self, begin, deadline, recurrence):
        self.ensure_one()
        values = {'priority': '0', 'recurrence_id': recurrence.id}
        if 'fsm_done' in self._fields:
            values['fsm_done'] = False
        if self.project_id.type_ids:
            values['stage_id'] = self.project_id.type_ids[0].id
        if begin and 'planned_date_begin' in self._fields:
            values['planned_date_begin'] = begin
        if deadline:
            values['date_deadline'] = deadline
        self.with_context(
            copy_project=True,
            mail_create_nolog=True,
            tracking_disable=True,
            mail_auto_subscribe_no_notify=True,
        ).copy(values)
