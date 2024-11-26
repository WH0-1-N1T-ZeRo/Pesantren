from odoo import api, fields, models


class sesi_tahfidz(models.Model):
    _name = 'cdn.sesi_tahfidz'
    _description = 'Tabel Sesi Tahfidz'

    name = fields.Char(string='Sesi Tahfidz', required=True)
    keterangan = fields.Char(string='Keterangan')
    
