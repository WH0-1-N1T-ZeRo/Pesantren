#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class riwayat_pendidikan(models.Model):

    _name               = "cdn.riwayat_pendidikan"
    _description        = "Tabel Riwayat Pendidikan Guru"
    name                = fields.Selection(string='Jenjang', selection=[('sd', 'SD'), ('smp', 'SMP/MTS Sederajat'),('sma', 'SMA/MA Sederajat'),('s1', 'Akademi/Sarjana S1'),('s2', 'Magister S2'), ('s3', 'Doktoral S3'),], required=True)
    nama_institusi      = fields.Char( string="Nama Institusi",  help="")
    jurusan             = fields.Char( string="Jurusan",  help="")
    keahlian            = fields.Char(string="Bidang Keahlian")
    tahun_lulus         = fields.Date( string="Tahun lulus",  help="")
    karya_tulis         = fields.Text(string="Judul Skripsi/Thesis/Disertasi")
    
    guru_id             = fields.Many2one(comodel_name="cdn.guru",  string="Guru",  help="")
    
