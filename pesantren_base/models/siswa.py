#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from io import BytesIO
import qrcode
from odoo.exceptions import ValidationError
import random

class res_partner(models.Model):
    _inherit = 'res.partner'

    jns_partner = fields.Selection(string='Jenis Partner', selection=[('siswa', 'Siswa'), ('ortu', 'Orang Tua'), ('guru', 'Guru'), ('umum', 'Umum')])

class siswa(models.Model):

    _name               = "cdn.siswa"
    _description        = "Tabel siswa"
    _inherit            = ['mail.thread', 'mail.activity.mixin']
    _inherits           = {"res.partner": "partner_id"}

    partner_id          = fields.Many2one('res.partner', 'Partner', ondelete="cascade")
    active_id           = fields.Many2one('res.partner', string='Customer Active', compute="_compute_partner_id")
    nis                 = fields.Char( string="NIS", required=True,  help="")
    nisn                = fields.Char( string="NISN",  help="")
    tmp_lahir           = fields.Char( string="Tempat Lahir",  help="")
    tgl_lahir           = fields.Date( string="Tgl Lahir",  help="")
    gol_darah           = fields.Selection(selection=[('A','A'),('B','B'),('AB','AB'),('O','O')],  string="Golongan Darah",  help="")
    jns_kelamin         = fields.Selection(selection=[('L','Laki-laki'),('P','Perempuan')],  string="Jenis Kelamin",  help="")

    rt_rw               = fields.Char(string="RT/RW")
    propinsi_id         = fields.Many2one(comodel_name="cdn.ref_propinsi",  string="Provinsi",  help="")
    kota_id             = fields.Many2one(comodel_name="cdn.ref_kota",  string="Kota",  help="")
    kecamatan_id        = fields.Many2one(comodel_name="cdn.ref_kecamatan",  string="Kecamatan",  help="")


    kewarganegaraan     = fields.Selection(selection=[('wni','WNI'),('wna','WNA')],  string="Kewarganegaraan",  help="")
    agama               = fields.Selection(selection=[('islam', 'Islam'), ('katolik', 'Katolik'), ('protestan', 'Protestan'), ('hindu', 'Hindu'), ('budha', 'Budha')],  string="Agama", default='islam', help="")
    panggilan           = fields.Char( string="Nama Panggilan",  help="")
    
    nik                 = fields.Char( string="No Induk Keluarga",  help="")
    anak_ke             = fields.Integer( string="Anak ke",  help="")
    jml_saudara_kandung = fields.Integer( string="Jml Saudara Kandung",  help="")
    bahasa              = fields.Char( string="Bahasa Sehari-hari",  help="")
    hobi                = fields.Many2one(comodel_name='cdn.ref_hobi', string='Hobi')
    cita_cita           = fields.Char(string='Cita-Cita')

    #Data Tempat Tinggal
    # tinggal_di          = fields.Selection(string='Tinggal di', selection=[('rumah', 'Rumah'), ('pondok', 'Pondok Pesantren'),], default='rumah')
    # pesantren_id        = fields.Many2one(comodel_name='res.partner', string='Nama Pesantren', domain="[('is_pesantren','=',True)]")
    # pesantren_alamat    = fields.Char(string='Alamat Pesantren', related='pesantren_id.street')
    # pesantren_telp      = fields.Char(string='No Telp Pesantren', related='pesantren_id.phone')

    @api.depends('partner_id')  # Jika `partner_id` field ada, atau bisa diubah ke field lain yang relevan
    def _compute_partner_id(self):
        for record in self:
            if record.partner_id:
                # Mengisi active_id berdasarkan data partner_id
                record.active_id = record.partner_id  # Bisa disesuaikan dengan field partner_id yang ingin digunakan
            else:
                record.active_id = 'No Partner'  # Nilai default jika partner_id kosong
    
    # Data Orang Tua
    ayah_nama           = fields.Char( string="Nama Ayah",  help="")
    ayah_tmp_lahir      = fields.Char( string="Tmp Lahir (Ayah)",  help="")
    ayah_tgl_lahir      = fields.Date( string="Tgl Lahir (Ayah)",  help="")
    ayah_warganegara    = fields.Selection(selection=[('wni','WNI'),('wna','WNA')],  string="Warganegara (Ayah)",  help="")
    ayah_telp           = fields.Char( string="No Telepon (Ayah)",  help="")
    ayah_email          = fields.Char( string="Email (Ayah)",  help="")
    ayah_pekerjaan_id   = fields.Many2one(comodel_name="cdn.ref_pekerjaan",  string="Pekerjaan (Ayah)",  help="")
    ayah_pendidikan_id  = fields.Many2one(comodel_name="cdn.ref_pendidikan",  string="Pendidikan (Ayah)",  help="")
    ayah_kantor         = fields.Char( string="Kantor (Ayah)",  help="")
    ayah_penghasilan    = fields.Integer( string="Penghasilan (Ayah)",  help="")
    ayah_agama          = fields.Selection(selection=[('islam', 'Islam'), ('katolik', 'Katolik'), ('protestan', 'Protestan'), ('hindu', 'Hindu'), ('budha', 'Budha')],  string="Agama (Ayah)",  help="")
    
    ibu_nama            = fields.Char( string="Nama Ibu",  help="")
    ibu_tmp_lahir       = fields.Char( string="Tmp lahir (Ibu) ",  help="")
    ibu_tgl_lahir       = fields.Date( string="Tgl lahir (Ibu)",  help="")
    ibu_warganegara     = fields.Selection(selection=[('wni','WNI'),('wna','WNA')],  string="Warganegara (Ibu)",  help="")
    ibu_telp            = fields.Char( string="No Telepon (Ibu)",  help="")
    ibu_email           = fields.Char( string="Email (Ibu)",  help="")
    ibu_pekerjaan_id    = fields.Many2one(comodel_name="cdn.ref_pekerjaan",  string="Pekerjaan (Ibu)",  help="")
    ibu_pendidikan_id   = fields.Many2one(comodel_name="cdn.ref_pendidikan",  string="Pendidikan (Ibu)",  help="")
    ibu_kantor          = fields.Char( string="Kantor (Ibu)",  help="")
    ibu_penghasilan     = fields.Integer( string="Penghasilan (Ibu)",  help="")
    ibu_agama           = fields.Selection(selection=[('islam', 'Islam'), ('katolik', 'Katolik'), ('protestan', 'Protestan'), ('hindu', 'Hindu'), ('budha', 'Budha')],  string="Agama (Ibu)",  help="")
    
    wali_nama           = fields.Char( string="Nama Wali",  help="")
    wali_tmp_lahir      = fields.Char( string="Tmp lahir (Wali)",  help="")
    wali_tgl_lahir      = fields.Date( string="Tgl lahir (Wali)",  help="")
    wali_telp           = fields.Char( string="No Telepon (Wali)",  help="")
    wali_email          = fields.Char( string="Email (Wali)",  help="")
    wali_agama          = fields.Selection(selection=[('islam', 'Islam'), ('katolik', 'Katolik'), ('protestan', 'Protestan'), ('hindu', 'Hindu'), ('budha', 'Budha')],  string="Agama (Wali)",  help="")
    wali_hubungan       = fields.Char( string="Hubungan dengan Siswa",  help="")

    orangtua_id         = fields.Many2one(comodel_name="cdn.orangtua",  string="Orangtua",  help="")
    tahunajaran_id      = fields.Many2one(comodel_name="cdn.ref_tahunajaran",  string="Thn Ajaran",  help="")
    ruang_kelas_id      = fields.Many2one(comodel_name="cdn.ruang_kelas",  string="Ruang Kelas",  help="")
    ekstrakulikuler_ids = fields.Many2many("cdn.ekstrakulikuler",string="Ekstrakulikuler")
    jenjang             = fields.Selection(selection=[('sd','SD/MI'),('smp','SMP/MTS'),('sma','SMA/MA/SMK')],  string="Jenjang", related="ruang_kelas_id.name.jenjang", readonly=True, store=True, help="")
    tingkat             = fields.Many2one(comodel_name="cdn.tingkat",  string="Tingkat", related="ruang_kelas_id.name.tingkat", readonly=True, store=True, help="")

    # Data Pendaftaran
    tgl_daftar          = fields.Date(string='Tgl Pendaftaran')
    asal_sekolah        = fields.Char(string='Asal Sekolah')
    alamat_asal_sek     = fields.Char(string='Alamat Sekolah Asal')
    telp_asal_sek       = fields.Char(string='No Telp Sekolah Asal')
    kepsek_sekolah_asal = fields.Char(string='Nama Kepala Sekolah')
    status_sekolah_asal = fields.Selection(string='Status Sekolah Asal', selection=[('swasta', 'Swasta'), ('negeri', 'Negeri'),])
    
    prestasi_sebelum    = fields.Char(string='Prestasi Diraih')
    bakat               = fields.Many2many(comodel_name='cdn.ref_bakat', string='Bakat Siswa')
    jalur_pendaftaran   = fields.Many2one(comodel_name='cdn.jalur_pendaftaran', string='Jalur Pendaftaran')
    jurusan_sma         = fields.Many2one(comodel_name='cdn.master_jurusan', string='Bidang/Jurusan')
    
    #Nilai Rata-rata Raport Kelas
    raport_4sd_1 = fields.Float(string='Raport 4 SD Smt 1')
    raport_4sd_2 = fields.Float(string='Raport 4 SD Smt 2')
    raport_5sd_1 = fields.Float(string='Raport 5 SD Smt 1')
    raport_5sd_2 = fields.Float(string='Raport 5 SD Smt 2')
    raport_6sd_1 = fields.Float(string='Raport 4 SD Smt 1')
    baca_quran   = fields.Selection(string="Baca Qur'an", selection=[('belumbisa', 'Belum Bisa'), ('kuranglancar', 'Kurang Lancar'),('lancar','Lancar'),('tartil','Tartil')])
    
    

    # Potongan Biaya / Bebas Biaya 
    bebasbiaya          = fields.Boolean(string='Bebas Biaya', default=False)
    harga_komponen      = fields.One2many(comodel_name='cdn.harga_khusus', inverse_name='siswa_id', string='Harga Khusus')
    penetapan_tagihan_id = fields.Many2one('cdn.penetapan_tagihan', string='penetapan_tagihan_id')

    barcode_santri      = fields.Char(string='Barcode Santri')    
    
    
    _sql_constraints = [('nis_uniq', 'unique(nis)', 'Data NIS tersebut sudah pernah terdaftar, pastikan NIS harus unik !'),
                        ('nisn_uniq', 'unique(nisn)', 'Data NISN tersebut sudah pernah terdaftar, pastikan NISN harus unik !'),
                        ('nik_uniq', 'unique(nik)', 'Data NIK tersebut sudah pernah terdaftar, pastikan NIK harus unik !')]
    
    # @api.model
    # def create(self, vals):
    #     # Update barcode_santri in res.partner before creation
    #     if 'barcode_santri' in vals:
    #         partner = self.env['res.partner'].browse(vals['partner_id'])
    #         partner.write({'barcode_santri': vals['barcode_santri']})
    #     return super(siswa, self).create(vals)

    def write(self, vals):
        # Update barcode_santri in res.partner on record update
        if 'barcode_santri' in vals:
            for record in self:
                record.partner_id.write({'barcode_santri': vals['barcode_santri']})
        return super(siswa, self).write(vals)
    
    @api.model
    def default_get(self, fields):
       res = super(siswa,self).default_get(fields)
       res['jns_partner'] = 'siswa'
       return res

    def _get_saldo_tagihan(self):
        saldo_invoice       = self.env['account.move'].search([('partner_id','=',self.partner_id.id),('state','=','posted')])
        self.saldo_tagihan  = sum(item.amount_residual for item in saldo_invoice)

    saldo_tagihan           = fields.Float('Saldo Tagihan', compute='_get_saldo_tagihan')

    def open_tagihan(self):
        # return {
        #     'name'          : _('Tagihan'),
        #     'domain'        : [('partner_id','=',self.partner_id.id),('state','=','posted'),('move_type','=','out_invoice')],
        #     # 'view_type' : 'form',
        #     'res_model'     : 'account.move',
        #     'view_id'       : False,
        #     'view_mode'     : 'list,form',
        #     'context': "{'default_move_type': 'out_invoice'}",
        #     'type'          :'ir.actions.act_window'
        # }
        action = self.env.ref('action_tagihan_inherit_view').read()[0]
        action['domain'] = [('partner_id','=',self.partner_id.id),('state','=','posted'),('move_type','=','out_invoice')]
        return action

    @api.model
    def print_kartu_santri(self, additional_arg=None):
        return self.env.ref("pesantren_base.action_report_kartu_santri").report_action(self)

    @api.model
    def print_sertifikat_santri(self, additional_arg=None):
        return self.env.ref("pesantren_base.action_report_sertifikat_santri").report_action(self)
