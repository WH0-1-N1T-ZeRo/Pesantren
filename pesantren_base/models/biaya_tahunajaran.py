#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class biaya_tahunajaran(models.Model):

    _name               = "cdn.biaya_tahunajaran"
    _description        = "Tabel Biaya Tahun Ajaran"

    name                = fields.Many2one(comodel_name="cdn.komponen_biaya", string="Komponen Biaya", required=True, ondelete="cascade")
    nominal             = fields.Float( string="Nominal",  help="")
    tahunajaran_id      = fields.Many2one(comodel_name="cdn.ref_tahunajaran",  string="Tahun Ajaran",  help="")
