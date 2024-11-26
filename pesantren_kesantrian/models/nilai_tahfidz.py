from odoo import api, fields, models


class NilaiTahfidz(models.Model):
    _name = 'cdn.nilai_tahfidz'
    _description = 'Tabel Nilai Tahfidz'

    name = fields.Char(string='Nilai Tahfidz Name', required=True)
    lulus = fields.Boolean(string='Lulus')
    

