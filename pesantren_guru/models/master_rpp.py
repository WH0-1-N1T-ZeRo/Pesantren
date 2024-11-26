from odoo import api, fields, models

class MasterRPP(models.Model):
  _name         = 'cdn.master_rpp'
  _description  = 'Data Rencana Pelaksanaan Pembelajaran'

  name = fields.Char(string='Materi', required=True)
  jenjang = fields.Selection([
    ('sd', 'SD/MI'),
    ('smp', 'SMP/MTS'),
    ('sma', 'SMA/MA'),
  ], string='Jenjang')
  matpel_id = fields.Many2one('cdn.mata_pelajaran', string='Mata Pelajaran')
  tingkat_id = fields.Many2one('cdn.tingkat', string='Kelas')
  jurusan_id = fields.Many2one('cdn.master_jurusan', string='Jurusan')
  waktu = fields.Char(string='Alokasi Waktu')
  kd = fields.Char(string='Kompentensi Dasar')
  dokumen = fields.Binary(string='Dokumen RPP')
  tujuan = fields.Text(string='Tujuan')

  @api.constrains('dokumen')
  def _check_dokumen(self):
    for record in self:
      if record.dokumen:
        header_byte = record.dokumen[:4]
        if header_byte.hex() != '4a564245':
          raise models.ValidationError('Dokumen harus berformat PDF')

