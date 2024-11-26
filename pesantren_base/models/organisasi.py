from odoo import api, fields, models


class Organisasi(models.Model):
    _name           = 'cdn.organisasi'
    _description    = 'Data Organisasi Alhmara'

    name            = fields.Char(string='Nama', required=True)
    anggota_ids     = fields.One2many(comodel_name='cdn.organisasi_structure', inverse_name='organisasi_id', string='Struktur')

class OrganisasiStructure(models.Model):
    _name           = 'cdn.organisasi_structure'

    partner_id      = fields.Many2one('res.partner','Anggota')
    organisasi_id   = fields.Many2one('cdn.organisasi','Organsasi')
    position        = fields.Char('Posisi',default='Anggota')
    

class ResPartner(models.Model):
    _inherit        = 'res.partner'

    organisasi_ids  = fields.One2many(comodel_name='cdn.organisasi_structure', inverse_name='partner_id', string='Organisasi')
    