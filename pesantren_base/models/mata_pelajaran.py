from odoo import api, fields, models


class MataPelajaran(models.Model):
  _name         = 'cdn.mata_pelajaran'
  _description  = 'Daftar Mata Pelajaran'

  name          = fields.Char(string='Nama Matpel', required=True)
  urut          = fields.Integer(string='No. Urut', default=0, readonly=True)
  kode          = fields.Char(string='Kode Matpel', required=True)
  kategori      = fields.Selection([
                    ('akademik', 'Akademik'),
                    ('diniyyah', 'Diniyyah'),
                    ('tahfidz', 'Tahfidz'),
                    ('ekstrakurikuler', 'Ekstrakurikuler'),
                    ('lainnya', 'Lainnya')
                  ], string='Kategori Matpel')
  jenjang       = fields.Selection([
                    ('sd', 'SD'),
                    ('smp', 'SMP'),
                    ('sma', 'SMA'),
                  ], string='Jenjang Pendidikan', required=True)
  tingkat_id    = fields.Many2one('cdn.tingkat', string='Kelas')
  jurusan_id    = fields.Many2one(comodel_name='cdn.master_jurusan', string='Jurusan / Peminatan')
  guru_ids      = fields.Many2many(comodel_name='hr.employee', string='Guru')

  @api.model
  def create(self, vals):
    if vals.get('urut', False):
      return super(MataPelajaran, self).create(vals)
    else:
      vals['urut'] = self.env['cdn.mata_pelajaran'].search([], order='urut desc', limit=1).urut + 1
      return super(MataPelajaran, self).create(vals)