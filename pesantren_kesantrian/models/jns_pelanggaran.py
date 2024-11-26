from odoo import api, fields, models


class Jns_Pelanggaran(models.Model):
    _name = 'cdn.jns_pelanggaran'
    _description = 'Master referensi jenis pelanggaran'

    name = fields.Char(string='Jenis Pelanggaran', required=True)
    active = fields.Boolean(string='Active', default=True)
    keterangan = fields.Char(string='Keterangan')
    pelanggaran_ids = fields.One2many(comodel_name='cdn.data_pelanggaran', inverse_name='jns_pelanggaran_id', string='Nama Pelanggaran', readonly=True)
    
    

