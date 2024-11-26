from odoo import api, fields, models


class Ekstrakulikuler(models.Model):
    _name           = 'cdn.ekstrakulikuler'
    _description    = 'Data Ekstrakulikuler'

    name            = fields.Char(string='Nama', required=True)
    is_wajib        = fields.Boolean(string='Ekstra Wajib', required=True)
    tingkat_ids     = fields.Many2many(comodel_name="cdn.tingkat",  string="Tingkat",required=True)
