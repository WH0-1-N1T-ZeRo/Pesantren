#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class guru(models.Model):

    _name               = "cdn.guru"
    _description        = "Tabel Data Guru/Tenaga Pengajar"
    _inherit            = ['mail.thread', 'mail.activity.mixin']
    _inherits           = {"res.partner": "partner_id"}

    partner_id          = fields.Many2one('res.partner', 'Partner', required=True, ondelete="cascade")

    nip                 = fields.Char( string="NIP", required=True, help="")
    tmp_lahir           = fields.Char( string="Tempat Lahir",  help="")
    tgl_lahir           = fields.Date( string="Tgl lahir",  help="")
    gol_darah           = fields.Selection(selection=[('A','A'),('B','B'),('AB','AB'),('O','O')],  string="Gol Darah",  help="")
    jns_kelamin         = fields.Selection(selection=[('L','Laki-laki'),('P','Perempuan')],  string="Jenis Kelamin",  help="")


    pendidikan_id       = fields.Many2one(comodel_name="cdn.ref_pendidikan",  string="Pendidikan",  help="")
    riwayat_pendidikan_ids = fields.One2many(comodel_name="cdn.riwayat_pendidikan",  inverse_name="guru_id",  string="Riwayat Pendidikan",  help="")

    _sql_constraints    = [('nip_uniq', 'unique(nip)', 'Nomor Induk Pegawai (NIP) harus unik !')]
