from odoo import api, fields, models

class Surah(models.Model):
  _name = 'cdn.surah'
  _description = 'Data Surah Al-Quran'

  id_name = fields.Char(string='Nama Surah')
  number = fields.Integer(string='Nomor Surah')
  name = fields.Char(string='Surah in ID')
  id_translation = fields.Char(string='Arti')
  revelation_type = fields.Char(string='Tempat Turun')
  ayat_ids = fields.One2many('cdn.ayat', 'surah_id', string='Ayat')
  jml_ayat = fields.Integer(string='Jumlah Ayat', compute='_compute_jml_ayat', readonly=True, store=True)

  @api.depends('ayat_ids')
  def _compute_jml_ayat(self):
    for surah in self:
      surah.jml_ayat = len(surah.ayat_ids)

  # modify get name method
  def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.id_name))
        return result
