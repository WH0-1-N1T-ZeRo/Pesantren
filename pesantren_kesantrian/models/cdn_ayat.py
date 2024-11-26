from odoo import api, fields, models

class Ayah(models.Model):
  _name = 'cdn.ayat'
  _description = 'Data Ayat Al-Quran'

  name = fields.Integer(string='Ayat ke')
  juz = fields.Integer(string='Juz')
  manzil = fields.Integer(string='Manzil')
  ruku = fields.Integer(string='Ruku')
  hizb = fields.Integer(string='Hizb')
  page = fields.Integer(string='Halaman')
  sajda = fields.Boolean(string='Sajda')
  ayat_sajda = fields.Selection([
    ('y', 'Iya'),
    ('n', 'Tidak')
  ], string='Ayat Sajdah', compute='_compute_ayat_sajda')
  surah_id = fields.Many2one('cdn.surah', string='Surah')
  ayat = fields.Char(string='Ayat')
  text = fields.Html(string='Text')
  id_translation = fields.Char(string='Arti')

  @api.depends('sajda')
  def _compute_ayat_sajda(self):
    for record in self:
      if record.sajda:
        record.ayat_sajda = 'y'
      else:
        record.ayat_sajda = 'n'
