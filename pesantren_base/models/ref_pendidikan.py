#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ref_pendidikan(models.Model):

    _name               = "cdn.ref_pendidikan"
    _description        = "Tabel Referensi Data Pendidikan"

    name                = fields.Char( required=True, string="Nama",  help="")
    keterangan          = fields.Char( string="Keterangan",  help="")
    active              = fields.Boolean( string="Active", default=True, help="")


