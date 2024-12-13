from odoo import api, fields, models


class JadwalPelajaran(models.Model):
    _name               = 'cdn.jadwal_pelajaran'
    _description        = 'Data Jadwal Pelajaran'
    _sql_constraints    = [
        ('name_uniq', 'unique (name)', 'Jadwal kelas sudah ada!')
    ]

    # default value
    def _get_default_jadwal_ids(self):
        jam_pelajaran = self.env['cdn.ref_jam_pelajaran'].search([])
        res = [(5,0,0)]
        for i in range(6):
            for j in jam_pelajaran:
                res.append((0, 0, {
                    'name': str(i + 1),
                    'jampelajaran_id': j.id,
                }))
        return res

    name                = fields.Char(string='Nama', readonly=True, compute='_compute_name', store=True)
    tahunajaran_id      = fields.Many2one('cdn.ref_tahunajaran', string='Tahun Ajaran', required=True,
        default=lambda self: self.env.user.company_id.tahun_ajaran_aktif.id)
    kelas_id            = fields.Many2one('cdn.ruang_kelas', string='Kelas', required=True)
    jenjang             = fields.Selection(selection=[('paud','PAUD'),('tk','TK/RA'),('sd', 'SD/MI'), ('smp', 'SMP/MTS'), ('sma', 'SMA/MA')], string='Jenjang', related='kelas_id.jenjang', readonly=True)
    walikelas_id        = fields.Many2one('hr.employee', string='Wali Kelas', readonly=True, related='kelas_id.walikelas_id')
    semester            = fields.Selection(selection=[('1', 'Semester 1'), ('2', 'Semester 2')], string='Semester', required=True)
    jadwal_ids          = fields.One2many('cdn.jadwal_pelajaran_lines', inverse_name='jadwalpelajaran_id', string='Jadwal Pelajaran'
        , default=_get_default_jadwal_ids)

    #compute
    @api.depends('kelas_id', 'semester', 'tahunajaran_id')
    def _compute_name(self):
        for rec in self:
            if rec.kelas_id and rec.semester and rec.tahunajaran_id:
                rec.name = '%s/Semester %s.%s' % (rec.kelas_id.name.name, rec.semester, rec.tahunajaran_id.name)
            else:
                rec.name = ''
    #check others requirements
    @api.model
    def default_get(self, fields_tree):
        if not self.env.user.company_id.tahun_ajaran_aktif.id:
            raise models.ValidationError('Tahun ajaran belum di set')
        return super().default_get(fields_tree)


class JadwalPelajaranLine(models.Model):
    _name               = 'cdn.jadwal_pelajaran_lines'
    _description        = 'Data Jadwal Pelajaran Line'

    name                = fields.Selection(selection=[
        ('1', 'Senin'), 
        ('2', 'Selasa'), 
        ('3', 'Rabu'), 
        ('4', 'Kamis'), 
        ('5', 'Jumat'), 
        ('6', 'Sabtu'), 
        ('7', 'Minggu')], string='Hari', required=True)
    jadwalpelajaran_id  = fields.Many2one('cdn.jadwal_pelajaran', string='Jadwal Pelajaran', ondelete='cascade')
    kelas_id            = fields.Many2one('cdn.ruang_kelas', string='Kelas', related='jadwalpelajaran_id.kelas_id', readonly=True, store=True)
    jenjang             = fields.Selection(selection=[('paud','PAUD'),('tk','TK/RA'),('sd', 'SD/MI'), ('smp', 'SMP/MTS'), ('sma', 'SMA/MA')], string='Jenjang', related='jadwalpelajaran_id.jenjang', readonly=True)
    jampelajaran_id     = fields.Many2one('cdn.ref_jam_pelajaran', string='Jam Pelajaran', required=True)
    start_time          = fields.Float(string='Jam Mulai', related='jampelajaran_id.start_time', readonly=True , widget="float_time")
    end_time            = fields.Float(string='Jam Selesai', related='jampelajaran_id.end_time', readonly=True , widget="float_time")
    matapelajaran_id    = fields.Many2one('cdn.mata_pelajaran', string='Mata Pelajaran', required=True)
    guru_id             = fields.Many2one('hr.employee', string='Guru',  domain=[('jns_pegawai','=','guru')])

    @api.onchange('start_time', 'end_time')
    def _onchange_jam(self):
        # Validasi jam dan menit dalam batas 24-jam dan menit 59
        if self.start_time or self.end_time:
            # Memformat jam dan menit
            start_time = max(0, min(int(self.start_time), 23))
            menit_mulai = max(0, min(int((self.start_time - start_time) * 60), 59))
            end_time = max(0, min(int(self.end_time), 23))
            menit_selesai = max(0, min(int((self.end_time - end_time) * 60), 59))

            # Periksa jika jam selesai terjadi sebelum jam mulai
            mulai_total = start_time * 60 + menit_mulai
            selesai_total = end_time * 60 + menit_selesai
            if selesai_total < mulai_total:
                return {
                    'warning': {
                        'title': 'Perhatian',
                        'message': 'Jam Selesai tidak boleh lebih awal dari Jam Mulai.'
                    }
                }

            # Menyimpan nilai dalam format float yang benar
            self.start_time = round(start_time + menit_mulai / 60, 2)
            self.end_time = round(end_time + menit_selesai / 60, 2)