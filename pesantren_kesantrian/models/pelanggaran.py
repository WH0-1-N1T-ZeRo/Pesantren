from odoo import api, fields, models
from lxml import etree


class Pelanggaran(models.Model):
    _name = 'cdn.pelanggaran'
    _description = 'Model untuk Mencatat Aktivitas Pelanggaran'
    _order = 'create_date desc'

    name = fields.Char(string='No. Referensi', readonly=True)
    state = fields.Selection(string='Status', selection=[
        ('draft', 'Draft'),
        ('confirmed', 'Konfirmasi'),
        ('approved', 'Disetujui'),
    ], default='draft')
    #data santri
    tgl_pelanggaran = fields.Date(string='Tgl Pelanggaran',
        states={
            'draft': [('readonly', False)],
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
        }, default=fields.Date.context_today, required=True)
    siswa_id = fields.Many2one(comodel_name='cdn.siswa', string='Siswa',
        states={
            'draft': [('readonly', False)],
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
        } ,
        required=True, readonly=True)
    kelas_id = fields.Many2one(comodel_name='cdn.ruang_kelas', string='Kelas', 
        related='siswa_id.ruang_kelas_id', readonly=True, store=True)
    #data pelanggaran
    pelanggaran_id = fields.Many2one(comodel_name='cdn.data_pelanggaran', string='Nama Pelanggaran', 
        states={
            'draft': [('readonly', False)],
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
        },
        required=True, readonly=True)
    kategori = fields.Selection(string='Kategori', selection=[
        ('ringan', 'Ringan'), ('sedang', 'Sedang'), ('berat', 'Berat'), ('sangat_berat', 'Sangat Berat')
    ], related='pelanggaran_id.kategori', store=True)
    poin = fields.Integer(string='Poin', related='pelanggaran_id.poin', store=True)
    deskripsi = fields.Text(string='Deskripsi Pelanggaran', 
        states={
            'draft': [('readonly', False)],
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
        })
    #data tindakan
    tindakan_id = fields.Many2one(comodel_name='cdn.tindakan_hukuman', string='Tindakan',
        states={
            'draft': [('readonly', False)],
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
        },
        required=True, readonly=True)
    deskripsi_tindakan = fields.Text(string='Deskripsi Tindakan', 
        states={
            'draft': [('readonly', False)],
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
        })

    diperiksa_oleh = fields.Many2one(comodel_name='hr.employee', string='Diperiksa Oleh',
        states={
            'draft': [('readonly', False)],
            'confirmed': [('readonly', True)],
            'approved': [('readonly', True)],
        },
        default=lambda self: self.env['res.users'].browse(self.env.uid).employee_id.id if self.env.uid else False,
        required=True, readonly=True)

    catatan_ka_asrama = fields.Text(string='Catatan Ustadz / Kepala Asrama',
        states={
            'draft': [('readonly', True)],
            'confirmed': [('readonly', False)],
            'approved': [('readonly', False)],
        }
    )
    tgl_disetujui = fields.Date(string='Tgl Disetujui',
        states={
            'draft': [('readonly', True)],
            'confirmed': [('readonly', False)],
            'approved': [('readonly', False)],
        },readonly=True)
    user_disetujui = fields.Many2one(comodel_name='res.users', string='Disetujui oleh', 
        states={
            'draft': [('readonly', True)],
            'confirmed': [('readonly', False)],
            'approved': [('readonly', False)],
        }, readonly=True)
    musyrif_id = fields.Many2one(
    comodel_name='hr.employee', 
    string='Musyrif', 
    related='siswa_id.musyrif_id', 
    readonly=True, 
    store=True
)
    # ir_squence for no. referensi
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('cdn.pelanggaran')
        return super(Pelanggaran, self).create(vals)

    def action_confirmed(self):
        self.state = 'confirmed'
    def action_approved(self):
        if not self.tgl_disetujui:
            self.tgl_disetujui = fields.Date.context_today(self)
        if not self.user_disetujui:
            self.user_disetujui = self.env.user.id
        self.state = 'approved'
    def action_set_to_draft(self):
        self.state = 'draft'
    


