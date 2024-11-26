from odoo import api, fields, models


class TindakanHukuman(models.Model):
    _name = 'cdn.tindakan_hukuman'
    _description = 'Tabel Tindakan Hukuman'

    name = fields.Char(string='Nama', required=True)
    level_pelanggaran = fields.Selection(string='Level Pelanggaran', selection=[
        ('Ringan', 'Ringan'), 
        ('Sedang', 'Sedang'), 
        ('Berat', 'Berat'), 
        ('Dikeluarkan', 'Sangat Berat')
    ])
    deskripsi = fields.Text(string='Deskripsi')
    