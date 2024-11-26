from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit               = 'res.company'

    max_wallet             = fields.Float(string='Saldo Dompet Maksimal')

    