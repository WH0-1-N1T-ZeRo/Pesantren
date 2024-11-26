#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ref_propinsi(models.Model):

    _name               = "cdn.ref_propinsi"
    _description        = "Tabel Referensi Data Provinsi"

    name                = fields.Char( required=True, string="Nama Provinsi",  help="")
    keterangan          = fields.Char( string="Keterangan",  help="")

    kota_ids            = fields.One2many(comodel_name="cdn.ref_kota",  inverse_name="propinsi_id",  string="Kota",  help="")
