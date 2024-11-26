from odoo import api, fields, models


class OrganisasiPenilaianAkhir(models.Model):
    _name = 'cdn.organisasi_penilaian_akhir'
    _description = 'Data organisasi di penilaian akhir'

    penilaianakhir_id   = fields.Many2one('cdn.penilaian_akhir', string='penilaian_akhir')
    name                = fields.Char(string='Nama', required=True)
    position            = fields.Char('Posisi')

