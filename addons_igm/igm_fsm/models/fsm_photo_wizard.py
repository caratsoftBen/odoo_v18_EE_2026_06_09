import base64

from odoo import fields, models, _


class IgmFsmPhotoWizard(models.TransientModel):
    _name = 'igm.fsm.photo.wizard'
    _description = 'Add Field Service Photo'

    task_id = fields.Many2one('project.task', required=True, ondelete='cascade')
    image = fields.Image(string="Foto", required=True)
    note = fields.Char(string="Notiz")

    def action_post(self):
        self.ensure_one()
        self.task_id.message_post(
            body=self.note or _("Foto"),
            attachments=[('foto.jpg', base64.b64decode(self.image))],
        )
        return {'type': 'ir.actions.act_window_close'}
