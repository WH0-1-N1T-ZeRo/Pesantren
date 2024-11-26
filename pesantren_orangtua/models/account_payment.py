from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    siswa_id = fields.Many2one('cdn.siswa', string='siswa', compute='_compute_siswa', store=True)
    is_internal_transfer = fields.Boolean(string='Internal Transfer')

    @api.depends('partner_id')
    def _compute_siswa(self):
        for x in self:
            if x.partner_id:
                Siswa = self.env['cdn.siswa'].search([('partner_id','=',x.partner_id.id)])
                if Siswa:
                    x.siswa_id = Siswa.id
                else:
                    x.siswa_id = False
            else:
                x.siswa_id = False