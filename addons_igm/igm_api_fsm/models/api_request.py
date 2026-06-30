from odoo import fields, models


class IgmApiFsmRequest(models.Model):
    _name = 'igm.api.fsm.request'
    _description = 'IGM FSM API Idempotency Record'
    _rec_name = 'igm_key'

    igm_key = fields.Char(string="Idempotency Key", required=True, index=True)
    igm_endpoint = fields.Char(string="Endpoint")
    igm_user_id = fields.Many2one('res.users', string="User")
    igm_result = fields.Text(string="Stored Result")

    _sql_constraints = [
        ('igm_key_uniq', 'unique(igm_key)', 'An API request with this idempotency key already exists.'),
    ]
