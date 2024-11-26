#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import re

class master_kelas(models.Model):

    _name               = "cdn.master_kelas"
    _description        = "Tabel Data Master Kelas"

    name                = fields.Char(required=True, string="Nama Kelas",  help="",  copy=False )
    jenjang             = fields.Selection(selection=[('sd','SD/MI'),('smp','SMP/MTS'),('sma','SMA/MA')],  string="Jenjang", required=True, help="")
    tingkat             = fields.Many2one(comodel_name="cdn.tingkat", string="Tingkat", required=True)
    jurusan_id          = fields.Many2one(comodel_name='cdn.master_jurusan', string='Jurusan / Peminatan')
    

    _sql_constraints = [('master_kelas_uniq', 'unique(name)', 'Master Data Kelas harus unik !')]

    def _convert_to_roman(self, number):
        roman =[(1000, 'M'),(900, 'CM'),(500, 'D'),(400, 'CD'),(100, 'C'),(90, 'XC'),(50, 'L'),(40, 'XL'),(10, 'X'),(9, 'IX'),(5, 'V'),(4, 'IV'),(1, 'I')]
        result = ''
        for value, letter in roman:
            while number >= value:
                result += letter
                number -= value
        return result

    @api.onchange('tingkat','jurusan_id')
    def onchange_tingkat(self):
        suffix = re.search(r'-[a-zA-Z]{1}$', self.name) if self.name else False
        name = ''
        if self.tingkat and self.jurusan_id:
            name = '%s-%s-' % (self._convert_to_roman(int(self.tingkat)), self.jurusan_id.name)
        elif self.tingkat:
            name = '%s-' % (self._convert_to_roman(int(self.tingkat)))
        if suffix:
            name += suffix.group(0)[1:].upper()
        return {'value': {'name': name}}
        


class master_jurusan(models.Model):
    _name               = 'cdn.master_jurusan'
    _description        = 'Tabel Master Data Jurusan SMA'

    name                = fields.Char(string='Nama Bidang/Jurusan', required=True, copy=False)
    active              = fields.Boolean(string='Aktif', default=True)
    keterangan          = fields.Char(string='Keterangan')

    _sql_constraints    = [('master_jurusan_uniq', 'unique(name)', 'Master Jurusan/Bidang Study harus unik !')]
    
    

