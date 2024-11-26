from odoo import api, fields, models


class Tingkat(models.Model):
    _name           = 'cdn.tingkat'
    _description    = 'Tabel Data Tingkat Pendidikan'

    name            = fields.Integer(string='Jenjang', required=True)
    jenjang         = fields.Selection(selection=[('sd','SD/MI'),('smp','SMP/MTS'),('sma','SMA/MA')], string='Jenjang', required=True)
    keterangan      = fields.Char(string='Keterangan', help='')

