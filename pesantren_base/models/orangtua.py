#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class OrangTua(models.Model):

    _name               = "cdn.orangtua"
    _description        = "Tabel Data Akun Orang Tua"
    _inherit            = ['mail.thread', 'mail.activity.mixin']
    _inherits           = {"res.partner": "partner_id"}

    partner_id          = fields.Many2one('res.partner', 'Partner', required=True, ondelete="cascade")

    nik                 = fields.Char( string="NIK",  help="")
    hubungan            = fields.Selection(selection=[('ayah','Ayah'),('ibu','Ibu'),('wali','Wali')],  string="Hubungan",  help="")
    # Memiliki Siswa / Anak
    siswa_ids           = fields.One2many(comodel_name="cdn.siswa",  inverse_name="orangtua_id",  string="Siswa",  help="")

    @api.model
    def default_get(self, fields):
       res = super(OrangTua,self).default_get(fields)
       res['jns_partner'] = 'ortu'
       return res
