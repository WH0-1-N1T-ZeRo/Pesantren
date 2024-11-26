from odoo import api, fields, models

class AbsenesiSiswa(models.Model):
    _name               = 'cdn.absensi_siswa'
    _description        = 'Data Absensi Siswa'

    # domain
    def _get_domain_guru(self):
        user = self.env.user
        if user.has_group('pesantren_guru.group_guru_manager'):
            return [('id','!=',False),('jns_pegawai','=','guru')]
        elif user.has_group('pesantren_guru.group_guru_staff'):
            user = self.env['hr.employee'].search([('user_id', '=', user.id)])  
            return [('id','=',user.id),('jns_pegawai','=','guru')]
        return [('id','=',False)]
    # default
    def _get_default_guru(self):
        user = self.env.user
        if user.has_group('pesantren_guru.group_guru_staff'):
            user = self.env['hr.employee'].search([('user_id', '=', user.id)])  
            return user.id
        return False



    name                = fields.Char(string='Nama', readonly=True, compute='_compute_name', store=True)
    tanggal             = fields.Date(string='Tgl Absen', required=True, default=fields.Date.today())
    hari                = fields.Selection([
                            ('1', 'Senin'),
                            ('2', 'Selasa'),
                            ('3', 'Rabu'),
                            ('4', 'Kamis'),
                            ('5', 'Jumat'),
                            ('6', 'Sabtu'),
                            ('7', 'Minggu'),
                        ], string='Hari', readonly=True, compute='_compute_hari', store=True)
    jampelajaran_id    = fields.Many2one(comodel_name='cdn.ref_jam_pelajaran', string='Jam Ke', required=True)
    start_time          = fields.Float(string='Start Time', related='jampelajaran_id.start_time', readonly=True, store=True)
    end_time            = fields.Float(string='End Time', related='jampelajaran_id.end_time', readonly=True, store=True)
    # data kelas
    kelas_id            = fields.Many2one(comodel_name='cdn.ruang_kelas', string='Kelas', required=True)
    tingkat_id             = fields.Many2one(comodel_name='cdn.tingkat', string='Tingkat', related='kelas_id.tingkat', readonly=True, store=True)
    walikelas_id        = fields.Many2one(comodel_name='hr.employee', string='Wali Kelas', related='kelas_id.walikelas_id', readonly=True, store=True)
    tahunajaran_id      = fields.Many2one(comodel_name='cdn.ref_tahunajaran', string='Tahun Ajaran', related='kelas_id.tahunajaran_id', readonly=True, store=True)
    semester            = fields.Selection(selection=[('1', 'Ganjil'), ('2', 'Genap')], string='Semester', readonly=True, store=True)
    guru_id             = fields.Many2one(comodel_name='hr.employee', string='Guru', required=True, 
                        domain=_get_domain_guru, default=_get_default_guru)
    pertemuan_ke        = fields.Integer(string='Pertemuan Ke', readonly=True, compute='_compute_pertemuan_ke', store=True)
    mapel_id            = fields.Many2one(comodel_name='cdn.mata_pelajaran', string='Mata pelajaran', required=True)
    rpp_id              = fields.Many2one(comodel_name='cdn.master_rpp', string='RPP')
    dokumen             = fields.Binary(string='Dokumen', related='rpp_id.dokumen', readonly=True, store=True)
    tema                = fields.Char(string='Tema', required=True)
    materi              = fields.Text(string='Materi', required=True)
    state               = fields.Selection(selection=[('draft', 'Draft'), ('done', 'Done')], string='State', default='draft')
    absensi_ids         = fields.One2many(comodel_name='cdn.absensi_siswa_lines', inverse_name='absensi_id', string='Absensi Siswa')

    # action
    def action_draft(self):
        self.state = 'draft'
    def action_done(self):
        self.state = 'done'
    # constraint
    @api.constrains('name')
    def _check_name(self):
        for record in self:
            if record.name:
                if self.search_count([('name','=',record.name)]) > 1:
                    raise models.ValidationError('Absensi Siswa sudah ada')
    # compute
    @api.depends('tanggal')
    def _compute_hari(self):
        for record in self:
            record.hari = str(self.tanggal.weekday() + 1)
    @api.depends('tanggal', 'jampelajaran_id')
    def _compute_name(self):
        for record in self:
            record.name = '%s/%s/%s' % (record.kelas_id.name.name,record.tanggal, record.jampelajaran_id.name)
    @api.depends('mapel_id','kelas_id')
    def _compute_pertemuan_ke(self):
        for record in self:
            if record.kelas_id and record.mapel_id:
                rid = record.id if type(record.id) == int else False
                record.pertemuan_ke = self.env['cdn.absensi_siswa'].search_count([
                    ('mapel_id','=',record.mapel_id.id),
                    ('kelas_id','=',record.kelas_id.id),
                    ('id','!=',rid),
                ]) + 1
    # onchange
    @api.onchange('guru_id')
    def _onchange_guru_id(self):
        return {'value':{
            'kelas_id': False,
            'jampelajaran_id': False,
        }}
    @api.onchange('tanggal','kelas_id','guru_id','jampelajaran_id')
    def _onchange_tanggal(self):
        if self.tanggal:
            jadwal = self.env['cdn.jadwal_pelajaran_lines'].search([('guru_id', '=', self.guru_id.id),('name','=',self.hari)])
            if jadwal:
                mapel = False
                absensi_ids = [(5,0,0)]
                if self.hari and self.kelas_id and self.guru_id and self.jampelajaran_id:
                    m = self.env['cdn.jadwal_pelajaran_lines'].search([
                        ('name','=',self.hari),
                        ('kelas_id','=',self.kelas_id.id),
                        ('guru_id','=',self.guru_id.id),
                        ('jampelajaran_id','=',self.jampelajaran_id.id)
                    ])
                    mapel = m.matapelajaran_id.id if m else False
                if self.kelas_id:
                    for siswa in self.kelas_id.siswa_ids:
                        absensi_ids.append((0,0,{
                            'siswa_id': siswa.id,
                            'kehadiran': 'Hadir',
                        }))
                return{
                    'domain':{
                        'kelas_id':[('id','in',jadwal.mapped('kelas_id').ids)],
                        'jampelajaran_id':[('id','in',jadwal.mapped('jampelajaran_id').ids)]
                    },
                    'value':{
                        'mapel_id':mapel,
                        'absensi_ids':absensi_ids,
                    }
                }
            else:
                return {}


class AbsensiSiswaLine(models.Model):
    _name           = 'cdn.absensi_siswa_lines'
    _description    = 'Data Absensi Siswa Lines'

    absensi_id      = fields.Many2one(comodel_name='cdn.absensi_siswa', string='Absensi Siswa', ondelete='cascade') 
    mapel_id        = fields.Many2one(comodel_name='cdn.mata_pelajaran', string='Mata pelajaran', related='absensi_id.mapel_id')
    tanggal         = fields.Date(string='Tgl Absen', related='absensi_id.tanggal', readonly=True, store=True)
    kelas_id        = fields.Many2one(comodel_name='cdn.ruang_kelas', string='Kelas', related='absensi_id.kelas_id', readonly=True, store=True)
    siswa_id        = fields.Many2one(comodel_name='cdn.siswa', string='Siswa', required=True)
    name            = fields.Char(string='Nama', related='siswa_id.name', readonly=True, store=True)
    nis             = fields.Char(string='NIS', related='siswa_id.nis', readonly=True, store=True)
    kehadiran       = fields.Selection([
                            ('Hadir', 'Hadir'),
                            ('Sakit', 'Sakit'),
                            ('Izin', 'Izin'),
                            ('Alpa', 'Alpa'),
                        ], string='Kehadiran', default='Hadir')