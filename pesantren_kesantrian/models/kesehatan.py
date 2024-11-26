from email.policy import default
from odoo import api, fields, models
from datetime import date, datetime, timedelta

class Kesehatan(models.Model):
  _name = 'cdn.kesehatan'
  _description = 'Model untuk Aktivitas Kesehatan'
  _order = 'name desc'

  #draft
  name = fields.Char(string='No Referensi', readonly=True)
  tgl_diperiksa = fields.Date(string='Tgl Diperiksa', default=date.today(), required=True )
  siswa_id = fields.Many2one(comodel_name='cdn.siswa', string='Siswa', required=True)
  kelas_id = fields.Many2one(comodel_name='cdn.ruang_kelas', string='Kelas', readonly=True, related='siswa_id.ruang_kelas_id')
  keluhan = fields.Text(string='Keluhan', required=True)
  #periksa
  diperiksa_oleh = fields.Char(string='Diperiksa Oleh', readonly=False, states={'draft': [('readonly', True)]})
  diagnosa = fields.Text(string='Diagnosa', readonly=False, states={'draft': [('readonly', True)]})
  #pengobatan
  obat = fields.Text(string='Obat', readonly=False, states={'draft': [('readonly', True)]})
  catatan = fields.Text(string='Catatan', readonly=False, states={'draft': [('readonly', True)]})
  #rawat
  lokasi_rawat = fields.Selection(string='Lokasi Rawat', selection=[
    ('uks','UKS'),
    ('rumah','Pulang ke Rumah'),
    ('rumah_sakit','Rumah Sakit/Klinik')
    ], readonly=False, states={'draft': [('readonly', True)]})
  keterangan_rawat = fields.Char(string='Keterangan Rawat', readonly=False, states={'draft': [('readonly', True)]})
  #sembuh
  tgl_selesai = fields.Date(string='Tgl Selesai', readonly=False, states={'draft': [('readonly', True)]})
  
  state = fields.Selection(string='Kondisi', selection=[
    ('draft','Draft'),
    ('periksa','Periksa'),
    ('pengobatan','Pengobatan'),
    ('rawat','Rawat'),
    ('sembuh','Sembuh')
    ], default='draft')
  
  @api.model
  def create(self, vals):
    vals['name'] = self.env['ir.sequence'].next_by_code('cdn.kesehatan')
    return super(Kesehatan, self).create(vals)
  
  def action_periksa(self):
    self.state = 'periksa'
  
  def action_pengobatan(self):
    self.state = 'pengobatan'
    
  def action_rawat(self):
    self.state = 'rawat'
    
  def action_sembuh(self):
    self.tgl_selesai = date.today()
    self.state = 'sembuh' 