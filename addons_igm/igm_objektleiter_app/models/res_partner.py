from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    igm_is_cleaning_site = fields.Boolean(
        string="Reinigungsobjekt",
        help="Diese Adresse ist ein zu reinigendes Objekt (Schule, Bürogebäude, ...).",
    )
    igm_coordinator_id = fields.Many2one(
        'res.users',
        string="Objektleiter",
        help="Verantwortlicher Objektleiter, der die Einsätze an diesem Reinigungsobjekt koordiniert.",
    )

    def _igm_ol_address(self):
        self.ensure_one()
        parts = [
            self.street,
            self.street2,
            ('%s %s' % (self.zip or '', self.city or '')).strip(),
        ]
        return ', '.join(p.strip() for p in parts if p and p.strip())
