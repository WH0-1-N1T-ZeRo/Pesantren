from odoo import api, fields, models


class TahfidzQuran(models.Model):
    _name = 'cdn.tahfidz_quran'

    name            = fields.Char(string='No Referensi', readonly=True)
    tanggal         = fields.Date(string='Tgl Tahfidz', required=True)
    siswa_id        = fields.Many2one('cdn.siswa', string='Siswa', required=True)
    last_tahfidz    = fields.Many2one('cdn.tahfidz_quran', string='Tahfidz Terakhir', related='siswa_id.last_tahfidz', readonly=True, store=True)
    halaqoh_id      = fields.Many2one('cdn.halaqoh', string='Halaqoh', readonly=True)
    ustadz_id       = fields.Many2one('hr.employee', string='Ustadz')
    sesi_tahfidz_id = fields.Many2one('cdn.sesi_tahfidz', string='Sesi', required=True)
    surah_id        = fields.Many2one('cdn.surah', string='Surah', states={'done': [('readonly', True)]})
    number          = fields.Integer(string='Surah Ke', related='surah_id.number', readonly=True)
    jml_ayat        = fields.Integer(string='Jumlah Ayat', related='surah_id.jml_ayat', readonly=True, store=True)

    ayat_awal       = fields.Many2one('cdn.ayat', string='Ayat Awal', states={'done': [('readonly', True)]})
    ayat_awal_name  = fields.Integer(string='Ayat Awal', related='ayat_awal.name', readonly=True)
    ayat_akhir      = fields.Many2one('cdn.ayat', string='Ayat Akhir', states={'done': [('readonly', True)]})
    jml_baris       = fields.Integer(string='Jumlah Baris', states={'done': [('readonly', True)]})
    nilai_id        = fields.Many2one('cdn.nilai_tahfidz', string='Nilai', states={'done': [('readonly', True)]})
    keterangan      = fields.Char(string='Keterangan', states={'done': [('readonly', True)]})
    state           = fields.Selection([('draft', 'Draft'),('done', 'Done')], default='draft', string='Status')
    musyrif_id = fields.Many2one(
    comodel_name='hr.employee', 
    string='Musyrif', 
    related='siswa_id.musyrif_id', 
    readonly=True, 
    store=True
)
    def get_last_tahfidz(self):
        last_tahfidz = self.env['cdn.tahfidz_quran'].search([
            ('siswa_id', '=', self.siswa_id.id),
            ('state', '=', 'done'),
        ], order='id desc', limit=1)
        return last_tahfidz

    def action_confirm(self):
        self.state = 'done'
        self.siswa_id.last_tahfidz = self.get_last_tahfidz()
    def action_draft(self):
        self.state = 'draft'
        self.siswa_id.last_tahfidz = self.get_last_tahfidz()

    @api.onchange('ayat_awal')
    def _onchange_ayat_awal(self):
        return {
            'value': {'ayat_akhir': False}
        }


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cdn.tahfidz_quran')
        return super(TahfidzQuran, self).create(vals)
    def name_get(self):
        result = []
        for record in self:
            if record.state == 'draft':
                result.append((record.id, record.name))
            else:
                result.append((
                    record.id, 
                    '{} # {} - {} # {} baris # {}'.format(
                        record.surah_id.display_name, 
                        record.ayat_awal.name, 
                        record.ayat_akhir.name, 
                        record.jml_baris, 
                        record.nilai_id.name
                    )
                ))
        return result

