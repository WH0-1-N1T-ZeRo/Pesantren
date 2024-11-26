#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ref_kecamatan(models.Model):

    _name               = "cdn.ref_kecamatan"
    _description        = "Tabel Data Ref Kecamatan"

    name                = fields.Char( required=True, string="Nama Kecamatan",  help="")
    keterangan          = fields.Char( string="Keterangan",  help="")


    kota_id             = fields.Many2one(comodel_name="cdn.ref_kota",  string="Kota",  help="")
