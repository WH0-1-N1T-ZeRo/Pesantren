from email.policy import default
from odoo import api, fields, models


class TahfidzHadits(models.Model):
    _name = 'cdn.tahfidz_hadits'
    _description = 'Tabel Tahfid AL Hadits'

    name = fields.Char(string='No Referensi', readonly=True)
    siswa_id = fields.Many2one(comodel_name='cdn.siswa', string='Siswa', required=True) 
    kelas_id = fields.Many2one(comodel_name='cdn.ruang_kelas', string='Kelas', readonly=True, related='siswa_id.ruang_kelas_id')
    
    tanggal = fields.Date(string='Tgl Tahfidz', default=fields.Date.context_today, required=True)
    guru_id = fields.Many2one(comodel_name='hr.employee', string='Guru', required=True, domain=[('jns_pegawai','in',['guru','musyrif','ustadz'])])
    hadits_id = fields.Many2one(comodel_name='cdn.hadits', string='Hadits', required=True)
    nilai_id = fields.Many2one(comodel_name='cdn.nilai_tahfidz', string='Nilai')
    nilai = fields.Integer(string='Nilai', default="0")
    keterangan = fields.Char(string='Keterangan')
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('proses', 'Proses'),
        ('done', 'Selesai')
    ], default='draft')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cdn.tahfidz_hadits')
        return super(TahfidzHadits, self).create(vals)

    def action_proses(self):
        self.state = 'proses'

    def action_selesai(self):
        self.state = 'done'

    # @api.onchange('')
    # def _onchange_(self):
    #     pass
    
    
    
    
    
