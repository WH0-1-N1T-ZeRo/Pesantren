#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class biaya_daftarulang(models.Model):

    _name               = "ubig.biaya_daftarulang"
    _description        = "Tabel Biaya Tahun Ajaran"

    name                = fields.Many2one(comodel_name="ubig.komponen_biaya", string="Komponen Biaya", required=True, ondelete="cascade")
    nominal             = fields.Integer( string="Nominal",  help="")
    daftarulang_id      = fields.Many2one(comodel_name="ubig.pendidikan",  string="Jenjang Pendidikan",  help="")