from odoo import api, fields, models


class Perijinan(models.Model):
    _name = 'cdn.perijinan'
    _description = 'Data Perijinan Santri'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Nama', readonly=True)

    tgl_ijin = fields.Date(string='Tgl Ijin', required=True,
        states={
            'Draft': [('readonly', False)],
            'Check': [('readonly', True)],
            'Approved': [('readonly', True)],
            'Rejected': [('readonly', True)],
            'Permission': [('readonly', True)],
            'Return': [('readonly', True)],
        }, default=fields.Date.context_today)
    tgl_kembali = fields.Date(string='Tgl Kembali', required=True,
        states={
            'Draft': [('readonly', False)],
            'Check': [('readonly', False)],
            'Approved': [('readonly', True)],
            'Rejected': [('readonly', True)],
            'Permission': [('readonly', True)],
            'Return': [('readonly', True)],
        })
    waktu_keluar = fields.Datetime(string='Waktu Keluar', readonly=True)
    waktu_kembali = fields.Datetime(string='Waktu Kembali', readonly=True)

    penjemput = fields.Char(string='Penjemput', required=True,
        states={
            'Draft': [('readonly', False)],
            'Check': [('readonly', False)],
            'Approved': [('readonly', True)],
            'Rejected': [('readonly', True)],
            'Permission': [('readonly', True)],
            'Return': [('readonly', True)],
        })
    siswa_id = fields.Many2one('cdn.siswa', string='Siswa', required=True,
        states={
            'Draft': [('readonly', False)],
            'Check': [('readonly', True)],
            'Approved': [('readonly', True)],
            'Rejected': [('readonly', True)],
            'Permission': [('readonly', True)],
            'Return': [('readonly', True)],
        })
    kelas_id = fields.Many2one('cdn.ruang_kelas', string='Kelas',related='siswa_id.ruang_kelas_id', readonly=True)
    kamar_id = fields.Many2one('cdn.kamar_santri', string='Kamar', related='siswa_id.kamar_id', readonly=True)
    halaqoh_id = fields.Many2one('cdn.halaqoh', string='Halaqoh', related='siswa_id.halaqoh_id', readonly=True)
    musyrif_id = fields.Many2one('hr.employee', string='Musyrif', related='siswa_id.musyrif_id', readonly=True)
    
    catatan = fields.Text(string='Catatan',
        states={
            'Draft': [('readonly', False)],
            'Check': [('readonly', False)],
            'Approved': [('readonly', True)],
            'Rejected': [('readonly', True)],
            'Permission': [('readonly', True)],
            'Return': [('readonly', True)],
        })
    keperluan = fields.Text(string='Keperluan', required=True,
        states={
            'Draft': [('readonly', False)],
            'Check': [('readonly', False)],
            'Approved': [('readonly', True)],
            'Rejected': [('readonly', True)],
            'Permission': [('readonly', True)],
            'Return': [('readonly', True)],
        })
    lama_ijin = fields.Integer(string='Lama Ijin', readonly=True, compute='_compute_lama_ijin', store=True)

    jatuh_tempo = fields.Integer(string='Terlambat (hari)', readonly=True, compute='_compute_jatuh_tempo', store=True)
    cek_terlambat = fields.Boolean(string='Cek Terlambat', default=False, compute='_compute_jatuh_tempo', store=True)

    state = fields.Selection([
        ('Draft', 'Pengajuan'),
        ('Check', 'Diperiksa'),
        ('Approved', 'Disetujui'),
        ('Rejected', 'Ditolak'),
        ('Permission', 'Ijin Keluar'),
        ('Return', 'Kembali'),
    ], string='Status', default='Draft',
        track_visibility='onchange')
    musyrif_id = fields.Many2one(
    comodel_name='hr.employee', 
    string='Musyrif', 
    related='siswa_id.musyrif_id', 
    readonly=True, 
    store=True
)

    @api.depends('tgl_ijin', 'tgl_kembali')
    def _compute_lama_ijin(self):
        for record in self:
            if record.tgl_ijin and record.tgl_kembali:
                record.lama_ijin = (record.tgl_kembali - record.tgl_ijin).days

    @api.depends('waktu_kembali')
    def _compute_jatuh_tempo(self):
        print('compute jatuh tempo')
        for record in self:
            if record.waktu_kembali:
                kembali = record.waktu_kembali.date()
                print('waktu kembali')
                print(record.tgl_kembali,kembali,(kembali - record.tgl_kembali).days)
                if record.tgl_kembali < kembali:
                    record.jatuh_tempo = (kembali- record.tgl_kembali).days
                else:
                    record.jatuh_tempo = 0

                record.cek_terlambat = True if record.jatuh_tempo > 0 else False
    
    def action_checked(self):
        self.state = 'Check'
    def action_approved(self):
        self.state = 'Approved'
    def action_rejected(self):
        self.state = 'Rejected'
    def action_permission(self):
        self.state = 'Permission'
        self.waktu_keluar = fields.Datetime.now()
    def action_return(self):
        self.state = 'Return'
        self.waktu_kembali = fields.Datetime.now()


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cdn.perijinan')
        return super(Perijinan, self).create(vals)
