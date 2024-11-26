from odoo import api, fields, models

class AbsenTahfidzQuran(models.Model):
    _name           = 'cdn.absen_tahfidz_quran'
    _description    = 'Model Absen Tahfidz Quran'

    #get domain 
    def _domain_halaqoh_id(self):
        tahun_ajaran = self.env.user.company_id.tahun_ajaran_aktif.id
        if self.env.user.has_group('pesantren_kesantrian.group_kesantrian_manager'):
            return [
                ('id','!=',False),
                ('fiscalyear_id', '=', tahun_ajaran)
            ]
        return [
            '|',
                '&',
                ('penanggung_jawab_id.user_id', '=', self.env.user.id),
                ('fiscalyear_id', '=', tahun_ajaran),
                '&',
                ('pengganti_ids.user_id', '=', self.env.user.id),
                ('fiscalyear_id', '=', tahun_ajaran)
        ]

    name            = fields.Date(string='Tgl Absen', required=True, default=fields.Date.context_today, states={'Done': [('readonly', True)]})
    halaqoh_id      = fields.Many2one('cdn.halaqoh', string='Halaqoh', required=True, domain=_domain_halaqoh_id, states={'Done': [('readonly', True)]})
    ustadz_id       = fields.Many2one('hr.employee', string='Ustadz', required=True, domain=[('id','=',False)], states={'Done': [('readonly', True)]})
    fiscalyear_id   = fields.Many2one('cdn.ref_tahunajaran', string='Tahun Ajaran',readonly=True, default=lambda self:self.env.user.company_id.tahun_ajaran_aktif.id, states={'Done': [('readonly', True)]})
    sesi_id         = fields.Many2one('cdn.sesi_tahfidz', string='Sesi', required=True, states={'Done': [('readonly', True)]})
    keterangan      = fields.Text(string='Keterangan', states={'Done': [('readonly', True)]})
    absen_ids       = fields.One2many('cdn.absen_tahfidz_quran_line', 'absen_id', string='Absen', states={'Done': [('readonly', True)]})
    state           = fields.Selection([
        ('Draft', 'Draft'),
        ('Proses', 'Proses'),
        ('Done','Selesai'),
    ], default='Draft', string='Status')

    def action_proses(self):
        self.state = 'Proses'
        # create tahfidz quran
        for absen in self.absen_ids:
            if absen.kehadiran == 'Hadir':
                surah, ayat_awal = None, None
                last_tahfidz = self.env['cdn.tahfidz_quran'].search([
                    ('siswa_id', '=', absen.siswa_id.id),
                    ('state', '=', 'done'),
                ], order='id desc', limit=1)
                if last_tahfidz:
                    if not last_tahfidz.surah_id.number == 114 and last_tahfidz.ayat_akhir.name == last_tahfidz.surah_id.jml_ayat:
                        surah = self.env['cdn.surah'].search([('number', '>', last_tahfidz.surah_id.number)], limit=1).id
                        ayat_awal = self.env['cdn.ayat'].search([('surah_id', '=', last_tahfidz.surah_id.id)], limit=1).id
                    else:
                        ayat_awal = last_tahfidz.ayat_akhir.id + 1
                        surah = last_tahfidz.surah_id.id
                    
                tahfidz_quran_vals = {
                    'tanggal': self.name,
                    'siswa_id': absen.siswa_id.id,
                    'halaqoh_id': self.halaqoh_id.id,
                    'ustadz_id': self.ustadz_id.id,
                    'sesi_tahfidz_id': self.sesi_id.id,
                    'state': 'draft',
                    'surah_id': surah,
                    'ayat_awal': ayat_awal,
                }
                self.env['cdn.tahfidz_quran'].create(tahfidz_quran_vals)
    def action_confirm(self):
        self.state = 'Done'

    @api.onchange('halaqoh_id')
    def _onchange_halaqoh_id(self):
        halaqoh = self.halaqoh_id
        if halaqoh:
            absen_ids = [(5, 0, 0)]
            for siswa in halaqoh.siswa_ids:
                absen_ids.append((0, 0, {
                    'siswa_id': siswa.id,
                    'kehadiran':'Hadir'
                }))
            ustadz = halaqoh.penanggung_jawab_id + halaqoh.pengganti_ids
            if not self.env.user.has_group('pesantren_kesantrian.group_kesantrian_manager'):
                ustadz = [x for x in ustadz if x.user_id.id == self.env.user.id]
            return {
                'domain':{
                    'ustadz_id': [
                        ('id','in',[x.id for x in ustadz])
                    ]
                },
                'value': {
                    'absen_ids': absen_ids,
                    'ustadz_id': ustadz[0].id if ustadz else False
                },
            }
    #check others requirements
    @api.model
    def default_get(self, fields_tree):
        tahun_ajaran = self.env['res.company'].search([('id', '=', self.env.ref('base.main_company').id)]).tahun_ajaran_aktif.id
        if not tahun_ajaran:
            raise models.ValidationError('Tahun ajaran belum di set')
        return super().default_get(fields_tree)

 
class AbsenTahfidzQuranLine(models.Model):
    _name           = 'cdn.absen_tahfidz_quran_line'
    _description    = 'Model Absen Tahfidz Quran Line'

    name            = fields.Char(string='Nama', related='siswa_id.name', readonly=True, store=True)
    absen_id        = fields.Many2one('cdn.absen_tahfidz_quran', string='Absen', ondelete='cascade')
    tanggal         = fields.Date(string='Tgl Absen', related='absen_id.name', readonly=True, store=True)
    halaqoh_id      = fields.Many2one('cdn.halaqoh', string='Halaqoh', related='absen_id.halaqoh_id', readonly=True, store=True)
    siswa_id        = fields.Many2one('cdn.siswa', string='Siswa', required=True)
    nis             = fields.Char(string='NIS', related='siswa_id.nis', readonly=True, store=True)
    kehadiran       = fields.Selection([
        ('Hadir', 'Hadir'),
        ('Izin', 'Izin'),
        ('Sakit', 'Sakit'),
        ('Alpa', 'Alpa'),
    ], string='Kehadiran', required=True)
    
    pengganti_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Pengganti Musyrif',
        readonly=True,
        store=True
    )

    @api.depends('halaqoh_id')
    def _compute_pengganti_ids(self):
        for record in self:
            record.pengganti_ids = record.halaqoh_id.pengganti_ids if record.halaqoh_id else False