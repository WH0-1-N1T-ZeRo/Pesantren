from odoo import api, fields, models


class level_tahsin(models.Model):
    _name = 'cdn.level_tahsin'
    _description = 'Tabel Level Tahsin'

    name = fields.Char(string='Level tahsin', required=True)
    keterangan = fields.Char(string='Keterangan')
    
