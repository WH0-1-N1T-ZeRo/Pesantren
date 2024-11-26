from odoo import api, fields, models


class Pelanggaran(models.Model):
    _name = 'cdn.data_pelanggaran'
    _description = 'Master referensi pelanggaran'

    name = fields.Char(string='Nama Pelanggaran', required=True)
    jns_pelanggaran_id = fields.Many2one(comodel_name='cdn.jns_pelanggaran', string='Jenis Pelanggaran', required=True)  
    kategori = fields.Selection(string='Kategori', selection=[
        ('Ringan', 'Ringan'), ('Sedang', 'Sedang'), 
        ('Berat', 'Berat'), ('Dikeluarkan', 'Sangat Berat')
    ], required=True)
    poin = fields.Integer(string='Poin', required=True)
    
    
    

