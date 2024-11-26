from odoo import api, fields, models


class ResPartnerChangePin(models.TransientModel):
    _name = 'res.partner.change.pin'

    wallet_pin = fields.Char(string='PIN Dompet')

    def _get_partner_id(self):
        context = self._context
        active_id = context.get('active_id')
        model = context.get('active_model')

        partner_id = active_id
        if model == 'cdn.siswa':
            Siswa = self.env['cdn.siswa'].browse(active_id)
            partner_id = Siswa.partner_id.id
        return partner_id
    def change_pin(self):
        Partner = self.env['res.partner'].browse(self._get_partner_id())
        Partner.write({
            'wallet_pin':self.wallet_pin
        })

