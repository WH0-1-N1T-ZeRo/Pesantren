from odoo import api, fields, models


class AbsenTahsinQuran(models.Model):
    _name           = 'cdn.absen_tahsin_quran'
    _description    = 'Tabel Absen Tahsin Quran'

    #get domain 
    def _get_halaqoh(self):
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
    halaqoh_id      = fields.Many2one('cdn.halaqoh', string='Halaqoh', required=True, domain=_get_halaqoh, states={'Done': [('readonly', True)]})
    ustadz_id       = fields.Many2one('hr.employee', string='Ustadz', required=True, states={'Done': [('readonly', True)]})
    fiscalyear_id   = fields.Many2one('cdn.ref_tahunajaran', string='Tahun Ajaran',readonly=True, default=lambda self:self.env.user.company_id.tahun_ajaran_aktif.id, states={'Done': [('readonly', True)]})
    absen_ids       = fields.One2many('cdn.absen_tahsin_quran_line', 'absen_id', string='Absen', states={'Done': [('readonly', True)]})
    state           = fields.Selection([
        ('Draft', 'Draft'),
        ('Proses', 'Proses'),
        ('Done','Selesai'),
    ], default='Draft', string='Status')


    def action_proses(self):
        self.state = 'Proses'
        for absen in self.absen_ids:
            if absen.kehadiran == 'Hadir':
                tahsin_quran_vals = {
                    'tanggal': self.name,
                    'siswa_id': absen.siswa_id.id,
                    'halaqoh_id': self.halaqoh_id.id,
                    'ustadz_id': self.ustadz_id.id,
                    'state': 'draft',
                }
                self.env['cdn.tahsin_quran'].create(tahsin_quran_vals)
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
                    'kehadiran': 'Hadir'
                }))
            
            ustadz = halaqoh.penanggung_jawab_id | halaqoh.pengganti_ids
            
            if not self.env.user.has_group('pesantren_kesantrian.group_kesantrian_manager'):
                ustadz = ustadz.filtered(lambda x: x.user_id == self.env.user)
            
            return {
                'domain': {
                    'ustadz_id': [('id', 'in', ustadz.ids)]
                },
                'value': {
                    'absen_ids': absen_ids,
                    'ustadz_id': ustadz[0].id if ustadz else False
                }
            }
    
    @api.model
    def default_get(self, fields_tree):
        tahun_ajaran = self.env['res.company'].search([('id', '=', self.env.ref('base.main_company').id)]).tahun_ajaran_aktif.id
        if not tahun_ajaran:
            raise models.ValidationError('Tahun ajaran belum di set')
        return super().default_get(fields_tree)

class AbsenTahsinQuranLine(models.Model):
    _name = 'cdn.absen_tahsin_quran_line'
    _description = 'Tabel Absen Tahsin Quran Line'

    absen_id = fields.Many2one('cdn.absen_tahsin_quran', string='Absen', ondelete='cascade')
    tanggal = fields.Date(string='Tgl Absen', related='absen_id.name', readonly=True, store=True)
    halaqoh_id = fields.Many2one('cdn.halaqoh', string='Halaqoh', related='absen_id.halaqoh_id', readonly=True, store=True)
    siswa_id = fields.Many2one('cdn.siswa', string='Siswa')
    name = fields.Char(string='Nama', related='siswa_id.name', readonly=True, store=True)
    nis = fields.Char(string='NIS', related='siswa_id.nis', readonly=True, store=True)
    kehadiran = fields.Selection([
        ('Hadir', 'Hadir'),
        ('Izin', 'Izin'),
        ('Sakit', 'Sakit'),
        ('Alpa', 'Alpa'),
    ], string='Kehadiran', required=True)
    


