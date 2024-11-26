from odoo import api, fields, models

class MobileFasilitas(models.Model):
    _name           = 'cdn.mobile.fasilitas'
    _description    = 'Data Widget Fasilitas'

    name            = fields.Char(string='Nama')
    icon            = fields.Binary(string='Icon')
    image           = fields.Binary(string='Image')
    description     = fields.Text(string='Description')