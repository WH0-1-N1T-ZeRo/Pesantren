from odoo import api, fields, models


class Penugasan(models.Model):
  _name          = 'cdn.penugasan'
  _description   = 'Data Penugasan'
  _rec_name      = 'tugas_ujian'

  # domain
  def _domain_guru(self):
      domain = ['&',('jns_pegawai','=','guru')]
      if self.env.user.has_group('pesantren_guru.group_guru_manager'):
          domain.append(('id','!=',False))
      elif self.env.user.has_group('pesantren_guru.group_guru_staff'):
          domain.append(('user_id','=',self.env.uid))
      else:
          domain.append(('id','=',False))
      return domain

  # name           = fields.Char(string='Nama')
  kelas_id       = fields.Many2one('cdn.ruang_kelas', string='Ruang Kelas', required=True)
  tugas_ujian    = fields.Text('Tugas / Ujian', required=True)
  tanggal        = fields.Date(string='Tgl Penugasan', default=fields.Date.today())
  deadline       = fields.Date(string='Deadline')
  state          = fields.Selection([
                    ('draft', 'Draft'),
                    ('proses', 'Ditugaskan'),
                    ('done', 'Selesai'),
                  ], default='draft', string='Status')
  tugas_line_ids = fields.One2many(comodel_name='cdn.tugas_line', inverse_name='penugasan_id', string='Tugas Line')
  tingkat_id     = fields.Many2one('cdn.tingkat', string='Kelas', related='kelas_id.tingkat')
  matpel_id      = fields.Many2one(comodel_name='cdn.mata_pelajaran', string='Mata Pelajaran', required=True)
  guru_id        = fields.Many2one(comodel_name='hr.employee', string='Guru', domain=_domain_guru)
  
  # jadwal_pelajaran_lines_ids = fields.Many2many(comodel_name='cdn.jadwal_pelajaran_lines', string='Jadwal Pelajaran Lines')
  
  def action_proses(self):
    self.state = 'proses'
  
  def action_done(self):
    self.state = 'done'

  @api.onchange('kelas_id')
  def _onchange_kelas_id(self):
    if self.kelas_id:
      kelas = self.env['cdn.ruang_kelas'].search([('id', '=', self.kelas_id.id)])
      if kelas:
        tugas_line_ids = [(5, 0, 0)]
        if self.kelas_id.siswa_ids:
          for siswa in self.kelas_id.siswa_ids:
            tugas_line_ids.append((0, 0, {
              'siswa_id': siswa.id,
              'nilai': 0,
            }))
        return {'domain': {
          'kelas_id': [('id', '=', self.kelas_id.id)],
          'tugas_line_ids': [('siswa_id', 'in', self.kelas_id.siswa_ids.ids)]
        }, 'value': {
          'tugas_line_ids': tugas_line_ids
        }
        }
      else:
        return {
        }

  
  class TugasLine(models.Model):
    _name         = 'cdn.tugas_line'
    _description  = 'Tugas Line'

    name          = fields.Char(string='Nama', related='siswa_id.name', readonly=True, store=True)
    siswa_id      = fields.Many2one('cdn.siswa', string='Nama', required=True)
    kelas_id      = fields.Many2one('cdn.ruang_kelas', string='Kelas', related='penugasan_id.kelas_id', readonly=True, store=True)
    nilai         = fields.Float(string='Nilai')
    keterangan    = fields.Char(string='Keterangan')
    penugasan_id  = fields.Many2one('cdn.penugasan', string='Penugasan', ondelete='cascade')
    state         = fields.Selection([
                      ('draft', 'Draft'),
                      ('proses', 'Ditugaskan'),
                      ('done', 'Selesai'),
                    ], default='draft', string='Status', related='penugasan_id.state', readonly=True, store=True)