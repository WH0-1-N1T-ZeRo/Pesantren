from odoo import api, fields, models


class BiayaSekolah(models.Model):
    _name = 'cdn.biaya_sekolah'
    _description = 'Tabel Biaya skolah'

    name = fields.Char(string='Nama', required=True)
    nominal_biaya = fields.Float(string='Nominal Biaya', required=True)
    lama_tagihan = fields.Char(string='Lama Tagihan', required=True)
    keterangan = fields.Text('keterangan')
    

    
