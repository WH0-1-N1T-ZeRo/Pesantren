from odoo import api, fields, models


class TahsinQuran(models.Model):
    _name           = 'cdn.tahsin_quran'
    _description    = 'Tabel Tahsin Quran'

    name            = fields.Char(string='No Referensi', readonly=True)
    tanggal         = fields.Date(string='Tgl Tahfidz', required=True, states={'done': [('readonly', True)]})

    siswa_id        = fields.Many2one('cdn.siswa', string='Siswa', required=True)
    kelas_id        = fields.Many2one('cdn.ruang_kelas', string='Kelas', related='siswa_id.ruang_kelas_id', readonly=True, store=True)

    halaqoh_id      = fields.Many2one('cdn.halaqoh', string='Halaqoh', required=True, states={'done': [('readonly', True)]})
    ustadz_id       = fields.Many2one('hr.employee', string='Ustadz Pembimbing', required=True, states={'done': [('readonly', True)]})

    level_tahsin_id = fields.Many2one('cdn.level_tahsin', string='Level Tahsin', states={'done': [('readonly', True)]})
    nilai_tajwid    = fields.Integer(string='Nilai Tajwid', states={'done': [('readonly', True)]})
    nilai_makhroj   = fields.Integer(string='Nilai Makhroj', states={'done': [('readonly', True)]})
    nilai_mad       = fields.Integer(string='Mad', states={'done': [('readonly', True)]})

    # Revisi : Tambahkan field Buku Tahsin
    buku_tahsin_id  = fields.Many2one('cdn.buku_tahsin', string='Buku Tahsin', states={'done': [('readonly', True)]})
    jilid_tahsin_id = fields.Many2one('cdn.jilid_tahsin', string='Jilid Tahsin', states={'done': [('readonly', True)]})
    halaman_tahsin  = fields.Char(string='Halaman', states={'done': [('readonly', True)]})
    

    keterangan      = fields.Char(string='Keterangan', states={'done': [('readonly', True)]})

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Selesai')
    ], default='draft', string='Status')
    penanggung_jawab_id = fields.Many2one('hr.employee', string='Penanggung Jawab', related='halaqoh_id.penanggung_jawab_id', readonly=True, store=True)

    # Jika buku tahsin diubah, maka jilid dan halaman direset
    @api.onchange('buku_tahsin_id')
    def _onchange_buku_tahsin_id(self):
        self.jilid_tahsin_id = False
        self.halaman_tahsin = False

    def action_confirm(self):
        # if not self.level_tahsin_id or not self.nilai_tajwid or not self.nilai_makhroj or not self.nilai_mad:
        #     raise models.ValidationError('Proses KONFIRMASI harus menyertakan Keterangan Jilid Tahsin dan Nilai-nilainya !')
        # Cek buku tahsin, jilid dan halaman
        if not self.buku_tahsin_id or not self.jilid_tahsin_id or not self.halaman_tahsin:
            raise models.ValidationError('Proses KONFIRMASI harus menyertakan Buku Tahsin, Jilid dan Halaman !')
        self.state = 'done'
    def action_draft(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cdn.tahsin_quran')
        return super(TahsinQuran, self).create(vals)
    
    # def write(self, vals):
    #     if not vals.get('level_tahsin_id',self.level_tahsin_id.id) or not vals.get('nilai_tajwid',self.nilai_tajwid) or not vals.get('nilai_makhroj',self.nilai_makhroj) or not vals.get('nilai_mad',self.nilai_mad):
    #         raise models.ValidationError('ERROR ! Periksa kembali pengisian KATEGORI Tahsin dan Nilai-nilainya !')
    #     return super(TahsinQuran, self).write(vals)



class BukuTahsin(models.Model):
    _name           = 'cdn.buku_tahsin'
    _description    = 'Tabel Buku Tahsin'

    name            = fields.Char(string='Nama Buku', required=True)
    jilid_ids       = fields.One2many('cdn.jilid_tahsin', 'buku_tahsin_id', string='Jilid Tahsin')
    keterangan      = fields.Char(string='Keterangan')

class JilidTahsin(models.Model):
    _name           = 'cdn.jilid_tahsin'
    _description    = 'Tabel Jilid Tahsin'

    name            = fields.Char(string='Jilid', required=True)
    buku_tahsin_id  = fields.Many2one('cdn.buku_tahsin', string='Buku Tahsin', required=True)
    keterangan      = fields.Char(string='Keterangan')