import base64

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import html2plaintext


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def igm_api_fsm_get_my_tasks(self):
        tasks = self.search(
            [
                ('user_ids', 'in', self.env.uid),
                ('is_fsm', '=', True),
                ('fsm_done', '=', False),
            ],
            order='planned_date_begin asc, id asc',
        )
        return tasks.igm_api_fsm_read()

    def igm_api_fsm_read(self):
        result = []
        for task in self:
            partner = task.partner_id
            if task.fsm_done:
                status = 'done'
            elif task.timer_start:
                status = 'in_progress'
            else:
                status = 'planned'
            result.append({
                'id': task.id,
                'ref': task.project_id.name or ('#%d' % task.id),
                'title': task.name or '',
                'status': status,
                'customer': {
                    'name': partner.name or '',
                    'address': task._igm_api_fsm_address(),
                    'phone': partner.phone or partner.mobile or None,
                },
                'contact': task._igm_api_fsm_contact(),
                'plannedStart': task.planned_date_begin.isoformat() if task.planned_date_begin else None,
                'plannedEnd': task.date_deadline.isoformat() if task.date_deadline else None,
                'allocatedHours': task.allocated_hours or 0.0,
                'note': task._igm_api_fsm_note(),
                'photos': task._igm_api_fsm_photo_ids(),
                'photoCount': task._igm_api_fsm_photo_count(),
            })
        return result

    def _igm_api_fsm_address(self):
        self.ensure_one()
        partner = self.partner_id
        parts = [
            partner.street,
            partner.street2,
            ('%s %s' % (partner.zip or '', partner.city or '')).strip(),
        ]
        return ', '.join(p.strip() for p in parts if p and p.strip())

    def _igm_api_fsm_contact(self):
        self.ensure_one()
        partner = self.partner_id
        if not partner:
            return None
        contact = partner
        if partner.is_company:
            child = partner.child_ids.filtered(lambda p: p.type == 'contact' and p.name)[:1]
            contact = child or partner
        return {
            'name': contact.name or '',
            'role': contact.function or '',
            'phone': contact.phone or partner.phone or None,
            'mobile': contact.mobile or partner.mobile or None,
            'email': contact.email or partner.email or None,
        }

    def _igm_api_fsm_note(self):
        self.ensure_one()
        if not self.description:
            return None
        text = html2plaintext(self.description).strip()
        return text or None

    def _igm_api_fsm_photo_count(self):
        self.ensure_one()
        return len(self._igm_api_fsm_photo_ids())

    def _igm_api_fsm_photo_ids(self):
        self.ensure_one()
        return self.env['ir.attachment'].search([
            ('res_model', '=', 'project.task'),
            ('res_id', '=', self.id),
            ('mimetype', '=like', 'image/%'),
        ], order='id').ids

    def igm_api_fsm_mark_done(self, worked_hours=None, reason=None):
        self.ensure_one()
        if worked_hours is not None and reason:
            self._igm_api_fsm_log_time_reason(worked_hours, reason)
        if worked_hours is None:
            self.action_igm_cleaner_done()
            return True
        if self.timer_start:
            self.action_timer_stop()
        if self.allow_timesheets and worked_hours and not self.total_hours_spent:
            self.env['account.analytic.line'].create({
                'task_id': self.id,
                'project_id': self.project_id.id,
                'name': self.name or '/',
                'unit_amount': worked_hours,
                'date': fields.Date.context_today(self),
            })
        self.action_fsm_validate(stop_running_timers=True)
        return True

    def igm_api_fsm_add_photo(self, image_base64, note=None):
        self.ensure_one()
        image_data = (image_base64 or '').split(',')[-1]
        raw = base64.b64decode(image_data)
        if len(raw) > 20 * 1024 * 1024:
            raise UserError(_("Das Foto ist zu groß (max. 20 MB)."))
        message = self.message_post(
            body=note or _("Foto"),
            attachments=[('foto.jpg', raw)],
        )
        attachment = message.attachment_ids[:1]
        return attachment.id if attachment else False

    def _igm_api_fsm_supervisor_partner(self):
        self.ensure_one()
        employee = self.env.user.employee_id
        if employee and employee.parent_id and employee.parent_id.user_id:
            return employee.parent_id.user_id.partner_id
        admin = self.env.ref('base.user_admin', raise_if_not_found=False)
        return admin.partner_id if admin else self.env['res.partner']

    def _igm_api_fsm_log_time_reason(self, worked_hours, reason):
        self.ensure_one()
        supervisor = self._igm_api_fsm_supervisor_partner()
        hours = int(worked_hours)
        minutes = int(round((worked_hours - hours) * 60))
        body = _(
            "Zugewiesene Zeit angepasst auf %(h)02d:%(m)02d h.\nBegründung: %(reason)s"
        ) % {'h': hours, 'm': minutes, 'reason': reason}
        self.message_post(body=body, partner_ids=supervisor.ids)
