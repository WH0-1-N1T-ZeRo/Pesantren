from email import message
from email.policy import default
from odoo import api, fields, models

class Penilaian(models.Model):
    _name               = 'cdn.penilaian'
    _description        = 'Tabel Data Penilaian Siswa'
    
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

    name                = fields.Char(string='Nama', required=True, compute='_compute_name', default=False)
    kelas_id            = fields.Many2one(comodel_name='cdn.ruang_kelas', string='Kelas', required=True)
    mapel_id            = fields.Many2one(comodel_name='cdn.mata_pelajaran', string='Mapel', required=True)
    guru_id             = fields.Many2one(comodel_name='hr.employee', string='Guru', required=True, domain=_domain_guru)
    semester            = fields.Selection(selection=[('1', 'Ganjil'), ('2', 'Genap')], string='Semester', required=True)
    tipe                = fields.Selection(string='Tipe', selection=[
                            ('Ulangan','Ulangan'), 
                            ('UTS','UTS'), 
                            ('UAS','UAS'), 
                            ('Ujian Sekolah','Ujian Sekolah'), 
                            ('Ujian Nasional','Ujian Nasional')], required=True)
    state               = fields.Selection(string='Status', selection=[('draft', 'Draft'), ('done', 'Done')], default='draft')
    penilaian_ids       = fields.One2many(comodel_name='cdn.penilaian_lines', inverse_name='penilaian_id', string='Penilaian')
    # onchange
    @api.onchange('kelas_id','tipe')
    def _onchange_kelas_id(self):
        lines = [(5, 0, 0)]
        for siswa in self.kelas_id.siswa_ids:
            lines.append((0, 0, {
                'siswa_id': siswa.id,
                'nilai': 0,
            }))
        return {
            'value': {'penilaian_ids': lines},
            'domain': {
                'penilaian_ids.siswa_id': [('id', 'in', self.kelas_id.siswa_ids.ids)]
            }
        }


    # compute
    def _compute_penialainid_id(self):
        for record in self:
            record.penialainid_id = record.id

    @api.depends('tipe')
    def _compute_name(self):
        for rec in self:
            rec.name = '%s' % (rec.tipe)

    # action buttons
    def action_draft(self):
        self.state = 'draft'
    def action_done(self):
        self.state = 'done'


class PenilaianLines(models.Model):
    _name               = 'cdn.penilaian_lines'
    _description        = 'Tabel Data Penilaian Siswa'
    _rec_name           = 'name'

    penilaian_id        = fields.Many2one(comodel_name='cdn.penilaian', string='Penilaian', required=True)
    name                = fields.Char(string='Nama', readonly=False, store=True, compute='_compute_name')
    mapel_id            = fields.Many2one(comodel_name='cdn.mata_pelajaran', string='Mapel', related='penilaian_id.mapel_id', readonly=True, store=True)
    tipe                = fields.Selection(string='Tipe', selection=[
                            ('ulangan','Ulangan'), 
                            ('uts','UTS'), 
                            ('uas','UAS'), 
                            ('ujian_sekolah','Ujian Sekolah'), 
                            ('ujian_nasional','Ujian Nasional')], related='penilaian_id.tipe', readonly=True, store=True)
    semester            = fields.Selection(selection=[('1', 'Ganjil'), ('2', 'Genap')], string='Semester', related='penilaian_id.semester', readonly=True, store=True)
    state               = fields.Selection(string='Status', selection=[('draft', 'Draft'), ('done', 'Done')], related='penilaian_id.state', readonly=True, store=True)
    siswa_id            = fields.Many2one(comodel_name='cdn.siswa', string='Siswa', required=True)
    nilai               = fields.Float(string='Nilai')
    predikat            = fields.Char(string='Predikat')
    # Field untuk domain di view penilaian
    id_kelas            = fields.Integer(string='Kelas ID', compute='_compute_id_kelas')
    id_penilaian        = fields.Integer(string='Penilaian ID', compute='_compute_id_penilaian')

    # compute

    @api.depends('penilaian_id')
    def _compute_name(self):
        for record in self:
            record.name = record.penilaian_id.name
    def _compute_id_kelas(self):
        for record in self:
            record.id_kelas = record.penilaian_id.kelas_id.id
    def _compute_id_penilaian(self):
        for record in self:
            record.id_penilaian = record.penilaian_id.id

    @api.onchange('nilai')
    def _onchange_nilai(self):
        message = {
            'title' : "Harap diperhatikan!",
            'message' : "Nilai tidak boleh kurang dari 0 atau melebihi 100"
        }
        if not self._validate_nilai(self.nilai):
            return {'warning': message, 'value':{'nilai': self._origin.nilai}}
        
        predikat = self.env['cdn.predikat'].search([('tipe','=','akademik')])
        val = {'value': {'predikat':''}}
        if predikat and self.nilai:
            for pred in predikat.predikat_ids:
                if pred.min_nilai <= self.nilai <= pred.max_nilai:
                    val['value']['predikat'] =  pred.name
        return val
    def _validate_nilai(self, nilai):
        if nilai < 0 or nilai > 100:
            return False
        return True