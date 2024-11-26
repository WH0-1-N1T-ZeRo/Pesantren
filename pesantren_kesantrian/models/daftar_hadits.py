from email.policy import default
from odoo import api, fields, models


class Hadits(models.Model):
    _name = 'cdn.hadits'
    _description = 'tabel Hadits'

    name = fields.Char(string='Nama Hadits', required=True)
    kode = fields.Integer(string='Kode', default="0", required=True)
    no_hadits = fields.Char(string='No Hadits', required=True)
    keterangan = fields.Char(string='Keterangan')
    matan_hadits = fields.Text(string='Matan Hadits')
    
    
    
    
