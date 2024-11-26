from odoo import api, fields, models


class Quran(models.Model):
  _name = 'cdn.quran'
  _description = 'Data for Quran'

  name = fields.Char(string='Nama Surah')
  jml_ayat = fields.Integer(string='Jumlah Ayat')
  juz = fields.Integer(string='Juz')
  surah_ke = fields.Integer(string='Surah Ke')
  terjemah = fields.Char(string='Arti')
