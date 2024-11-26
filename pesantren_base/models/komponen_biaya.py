#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class komponen_biaya(models.Model):

    _name               = "cdn.komponen_biaya"
    _description        = "Tabel Komponen Biaya"

    name                = fields.Char( required=True, string="Nama",  help="")
    tipe_bayar          = fields.Selection(selection=[('cicil','Cicilan'),('tunai','Tunai')],  string="Tipe bayar", required=True, default='tunai', help="")
    product_id          = fields.Many2one(comodel_name="product.product", string='Produk', required=True)
    biaya_tahunan       = fields.One2many(comodel_name='cdn.biaya_tahunajaran', inverse_name='name', string='Biaya Per Tahun Ajaran')
    active              = fields.Boolean(string='Active', default=True)
    
