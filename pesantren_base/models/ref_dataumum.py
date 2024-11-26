from odoo import api, fields, models


class ref_bakat(models.Model):
    _name               = 'cdn.ref_bakat'
    _description        = 'Tabel Referensi - Bakat'

    name                = fields.Char(string='Nama Bakat')
    keterangan          = fields.Char(string='Keterangan')
    active              = fields.Boolean(string='Aktif', default=True)
    
class ref_hobi(models.Model):
    _name               = 'cdn.ref_hobi'
    _description        = 'Tabel Referensi - Hobi'

    name                = fields.Char(string='Nama Hobi')
    keterangan          = fields.Char(string='Keterangan')
    active              = fields.Boolean(string='Aktif', default=True)
    
class jalur_pendaftaran(models.Model):
    _name               = 'cdn.jalur_pendaftaran'
    _description        = 'Tabel Jalur Pendaftaran'

    name                = fields.Char(string='Nama Jalur Pendaftaran')
    keterangan          = fields.Char(string='Keterangan')
    active              = fields.Boolean(string='Aktif', default=True)