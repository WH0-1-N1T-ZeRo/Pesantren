from odoo import api, fields, models


class PenilaianAkhirGuru(models.Model):
    _name           = 'cdn.penilaian_akhir_guru'
    _description    = 'Penilaian Akhir Guru'
    _rec_name       = 'guru_id'
    _sql_constraints=[('penilaian_akhir_guru_uniq', 'unique(tahunajaran_id,semester,kelas_id,mapel_id)', 'Penilaian Akhir Guru sudah ada!')]

    # default
    def _get_default_guru(self):
        if self.env.user.has_group('pesantren_guru.group_guru_staff'):
            return self.env['hr.employee'].search([('user_id','=',self.env.uid)]).id
    def _get_default_semester(self):
        tahun_ajaran = self.env.user.company_id.tahun_ajaran_aktif
        if not tahun_ajaran.term_akademik_ids:
            return False
        for term in tahun_ajaran.term_akademik_ids:
            today = fields.Date.today()
            if term.term_start_date <= today and term.term_end_date >= today:
                return term.name.split(' ')[1]
    # domain
    def _get_domain_guru(self):
        user = self.env.user
        if user.has_group('pesantren_guru.group_guru_manager'):
            return [('id','!=',False),('jns_pegawai','=','guru')]
        elif user.has_group('pesantren_guru.group_guru_staff'):
            user = self.env['hr.employee'].search([('user_id', '=', user.id)])  
            return [('id','=',user.id),('jns_pegawai','=','guru')]
        return [('id','=',False)]

    guru_id         = fields.Many2one('hr.employee', string='Guru', required=True, domain=_get_domain_guru, default=_get_default_guru)
    kelas_id        = fields.Many2one('cdn.ruang_kelas', string='Kelas', required=True)
    tahunajaran_id  = fields.Many2one('cdn.ref_tahunajaran', string='Tahun Ajaran', required=True, default=lambda self:self.env.user.company_id.tahun_ajaran_aktif.id)
    semester        = fields.Selection(string='Semester', selection=[
                    ('1', 'Semester 1'),
                    ('2', 'Semester 2'),], required=True, default=_get_default_semester)
    mapel_id        = fields.Many2one('cdn.mata_pelajaran', string='Mata Pelajaran', required=True)
    state           = fields.Selection(string='Status', selection=[
                    ('draft', 'Draft'),
                    ('confirm', 'Confirm')], default='draft')
    penilaian_ids   = fields.One2many('cdn.penilaian_akhir_lines', inverse_name='penilaianguru_id', string='Penilaian')

    # actions
    def act_confirm(self):
        self.state = 'confirm'
        for nilai in self.penilaian_ids:
            penilaianakhir_id = self.env['cdn.penilaian_akhir'].search([('siswa_id','=',nilai.siswa_id.id),('tahunajaran_id','=',self.tahunajaran_id.id),('semester','=',self.semester)])
            if penilaianakhir_id:
                nilai.penilaianakhir_id = penilaianakhir_id.id
    def act_draft(self):
        self.state = 'draft'
    # onchange
    @api.onchange('kelas_id','mapel_id','semester','tahunajaran_id')
    def _onchange_kelas(self):
        data = [(5,0,0)]
        if not self.kelas_id or not self.mapel_id:
            return {'value': {'penilaian_ids': data}}
        for rec in self.kelas_id.siswa_ids:
            data.append((0,0,{
                'siswa_id': rec.id,
                'mapel_id': self.mapel_id.id,
                'tahunajaran_id': self.tahunajaran_id.id,
                'semester': self.semester,
            }))
        return {'value': {'penilaian_ids': data}}
    #check others requirements
    @api.model
    def default_get(self, fields_tree):
        if not self.env.user.company_id.tahun_ajaran_aktif.id:
            raise models.ValidationError('Tahun ajaran belum di set')
        return super().default_get(fields_tree)
