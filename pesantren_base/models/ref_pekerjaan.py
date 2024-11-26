#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ref_pekerjaan(models.Model):

    _name               = "cdn.ref_pekerjaan"
    _description        = "Tabel Referensi Pekerjaan"

    name                = fields.Char( required=True, string="Nama Pekerjaan",  help="")
    keterangan          = fields.Char( string="Keterangan",  help="")
    active              = fields.Boolean( string="Active", default=True, help="")


