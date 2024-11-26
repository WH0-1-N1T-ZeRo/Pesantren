from odoo import api, fields, models


class Jns_prestasi(models.Model):
    _name = 'cdn.jns_prestasi'
    _description = 'Jenis Prestasi'

    name = fields.Char(string='Nama prestasi', required=True)
    prestasi_siswa_ids = fields.One2many(comodel_name='cdn.prestasi_siswa', inverse_name='jns_prestasi_id', string='Siswa', readonly=True)
    keterangan = fields.Char(string='keterangan')
    
    
