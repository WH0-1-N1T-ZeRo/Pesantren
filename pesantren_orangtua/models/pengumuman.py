from odoo import api, fields, models


class Pengumuman(models.Model):
    _name = 'cdn.pengumuman'
    _description = 'Tabel Pengumuman'

    name = fields.Char(string='Nama', required=True)
    deskripsi = fields.Html('Deskripsi')
