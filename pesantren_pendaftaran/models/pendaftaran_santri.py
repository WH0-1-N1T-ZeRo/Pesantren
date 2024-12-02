from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.exceptions import ValidationError, UserError
import uuid
from datetime import datetime, timedelta
from odoo.tools import format_date
import pytz
import random
import string

class ResPartner(models.Model):
    _inherit            = 'res.partner'

    virtual_account     = fields.Char(string='Virtual Account', store=True)
    va_saku             = fields.Char(string='No. VA Uang Saku', store=True)
    bank                = fields.Many2one('ubig.bank', string="Bank", help="Pilih bank untuk membuat virtual account")
    petunjuk_pembayaran = fields.Text(related='bank.petunjuk_pembayaran', string="Petunjuk Pembayaran")
    jns_partner         = fields.Selection(
        string='Jenis Partner',
        selection=[('siswa', 'Siswa'), ('ortu', 'Orang Tua'), ('guru', 'Guru'), ('umum', 'Umum'), ('calon_santri', 'Calon Santri')]
    , default="calon_santri", readonly="true")

class DataPendaftaran(models.Model):
    _name               = 'ubig.pendaftaran'
    _inherit            = ['mail.thread', 'mail.activity.mixin']
    _inherits           = {"res.partner": "partner_id"}
    _description        = 'Data Pendaftaran'
    _order              = 'total_nilai desc'
    

    token = fields.Char(string='Token')
    nomor_pendaftaran   = fields.Char(string='No Pendaftaran', readonly=True)
    tanggal_daftar      = fields.Date(string='Tanggal Daftar', default=fields.Date.context_today)
    partner_id          = fields.Many2one('res.partner', string="Nama Santri", required=False, help="Nama Calon Santri")

    # Username
    nik                 = fields.Char(string="NIK", help="Nomor Induk Keluarga Calon santri")
    email               = fields.Char(string="email", help="Email Calon Santri")
    password            = fields.Char(string="Kata Sandi", help="Kata Sandi Login")
    nomor_hp            = fields.Char(string="Nomor HP", help="Nomor HP/WhatsApp Calon Santri")

    # Jenjang Calon Santri
    jenjang_id          = fields.Many2one('ubig.pendidikan', string="Jenjang Pendidikan")
    jenjang             = fields.Selection(related='jenjang_id.jenjang', string='Jenjang', readonly=True)
    biaya               = fields.Integer(related='jenjang_id.biaya', string='Biaya Pendaftaran', readonly=True)
    keterangan          = fields.Char(related='jenjang_id.keterangan', string='Keterangan', readonly=True)

    # Data Diri
    gender              = fields.Selection([('L','Laki - Laki'),('P','Perempuan'),], string="Jenis Kelamin")
    kota_lahir          = fields.Char(string="Kota Kelahiran")
    tanggal_lahir       = fields.Date(string="Tanggal Lahir Calon Santri")
    golongan_darah      = fields.Selection([
                          ('A', 'A'),
                          ('B', 'B'),
                          ('AB', 'AB'),
                          ('O', 'O'),
                        ], string="Golongan Darah")
    kewarganegaraan     = fields.Selection(selection=[('wni','WNI'),('wna','WNA')],  string="Kewarganegaraan",  help="")
    alamat              = fields.Char(string='Alamat Calon Santri')
    provinsi_id         = fields.Many2one(comodel_name="cdn.ref_propinsi",  string="Provinsi",  help="")
    kota_id             = fields.Many2one(comodel_name="cdn.ref_kota",  string="Kota",  help="")
    kecamatan_id        = fields.Many2one(comodel_name="cdn.ref_kecamatan",  string="Kecamatan",  help="")
    nisn                = fields.Char(string="NISN", required=True)
    nis                 = fields.Char(string="NIS", store=True)
    anak_ke             = fields.Integer( string="Anak ke",  help="")
    jml_saudara_kandung = fields.Integer( string="Jml Saudara Kandung",  help="")
    cita_cita           = fields.Char(string='Cita-Cita')

    # Data Pendidikan
    asal_sekolah        = fields.Char(string='Asal Sekolah')
    alamat_asal_sek     = fields.Char(string='Alamat Sekolah Asal')
    telp_asal_sek       = fields.Char(string='No Telp Sekolah Asal')
    status_sekolah_asal = fields.Selection(string='Status Sekolah Asal', selection=[('swasta', 'Swasta'), ('negeri', 'Negeri'),])
    npsn                = fields.Char(string='NPSN Sekolah')

    # Data Orang Tua - Ayah
    nama_ayah           = fields.Char(string="Nama Ayah")
    ktp_ayah            = fields.Char(string="Nomor KTP Ayah")
    tanggal_lahir_ayah  = fields.Date(string="Tanggal Lahir Ayah")
    telepon_ayah        = fields.Char(string="Nomor Telepon Ayah")
    pekerjaan_ayah      = fields.Many2one('cdn.ref_pekerjaan',string="Pekerjaan Ayah")
    penghasilan_ayah    = fields.Selection([
                          ('1juta', ' < Rp. 1.000.000'),
                          ('5juta', 'Rp. 1.000.000 - Rp. 5.000.000'),
                          ('10juta', 'Rp. 6.000.000 - Rp. 10.000.000'),
                          ('11juta', '> Rp. 10.000.000')
                          ], string="Penghasilan Ayah")
    email_ayah          = fields.Char(string="Email Ayah")
    agama_ayah          = fields.Selection([
                          ('islam', 'Islam'),
                          ('kristen', 'Kristen'),
                          ('katolik', 'Katolik'),
                          ('hindu', 'Hindu'),
                          ('budha', 'Budha'),
                          ('lainnya', 'Lainnya'),
                          ], string="Agama Ayah")
    kewarganegaraan_ayah = fields.Selection(selection=[('wni','WNI'),('wna','WNA')], string="Kewarganegaraan Ayah")
    pendidikan_ayah     = fields.Many2one('cdn.ref_pendidikan', string="Riwayat Pendidikan Ayah")

    # Data Orang Tua - Ibu
    nama_ibu            = fields.Char(string="Nama Ibu")
    ktp_ibu             = fields.Char(string="Nomor KTP Ibu")
    tanggal_lahir_ibu   = fields.Date(string="Tanggal Lahir Ibu")
    telepon_ibu         = fields.Char(string="Nomor Telepon Ibu")
    pekerjaan_ibu       = fields.Many2one('cdn.ref_pekerjaan', string="Pekerjaan Ibu")
    penghasilan_ibu     = fields.Selection([
                          ('1juta', ' < Rp. 1.000.000'),
                          ('5juta', 'Rp. 1.000.000 - Rp. 5.000.000'),
                          ('10juta', 'Rp. 6.000.000 - Rp. 10.000.000'),
                          ('11juta', '> Rp. 10.000.000')
                          ], string="Penghasilan Ibu")
    email_ibu           = fields.Char(string="Email Ibu")
    agama_ibu           = fields.Selection([
                          ('islam', 'Islam'),
                          ('kristen', 'Kristen'),
                          ('katolik', 'Katolik'),
                          ('hindu', 'Hindu'),
                          ('budha', 'Budha'),
                          ('lainnya', 'Lainnya'),
                          ], string="Agama Ibu")
    kewarganegaraan_ibu = fields.Selection(selection=[('wni','WNI'),('wna','WNA')], string="Kewarganegaraan Ibu")
    pendidikan_ibu      = fields.Many2one('cdn.ref_pendidikan', string="Riwayat Pendidikan Ibu")

    wali_nama           = fields.Char( string="Nama Wali",  help="")
    wali_tmp_lahir      = fields.Char( string="Tmp lahir (Wali)",  help="")
    wali_tgl_lahir      = fields.Date( string="Tgl lahir (Wali)",  help="")
    wali_telp           = fields.Char( string="No Telepon (Wali)",  help="")
    wali_email          = fields.Char( string="Email (Wali)",  help="")
    wali_password       = fields.Char( string="Password", help="")
    wali_agama          = fields.Selection(selection=[('islam', 'Islam'), ('katolik', 'Katolik'), ('protestan', 'Protestan'), ('hindu', 'Hindu'), ('budha', 'Budha')],  string="Agama (Wali)",  help="")
    wali_hubungan       = fields.Char( string="Hubungan dengan Siswa",  help="")
                          
    # Dokumen Anak
    akta_kelahiran      = fields.Binary(string="Akta Kelahiran")
    kartu_keluarga      = fields.Binary(string="Kartu Keluarga")
    ijazah              = fields.Binary(string="Ijazah")
    surat_kesehatan     = fields.Binary(string="Surat Keterangan Sehat")
    pas_foto            = fields.Binary(string="Pas Foto Berwarna")
    skhun               = fields.Binary(string="SKHUN")
    raport_terakhir     = fields.Binary(string="Raport Terakhir")

    # Dokumen Orang Tua
    ktp_ortu            = fields.Binary(string="KTP Orang Tua/Wali")

    # Aspek Penilaian
    soal_ids            = fields.Many2many('seleksi.penilaian', string="Detail Penilaian")

    # Computed field untuk total nilai
    total_nilai         = fields.Integer(string="Total Nilai", compute="_compute_total_nilai", store=True)

    orangtua_id         = fields.Many2one('cdn.orangtua', string="Data Orang Tua", readonly=True)
    siswa_id            = fields.Many2one('cdn.siswa', string="Data Siswa", readonly=True)

    status_va           = fields.Selection([
                            ('temporary', 'Temporary'),
                            ('permanent', 'Permanent'),
                            ('inactive', 'Inactive'),
                        ], string="Status Virtual Account", default='temporary')

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('terdaftar', 'Terdaftar'),
        ('seleksi', 'Seleksi'),
        ('diterima', 'Diterima'),
        ('ditolak', 'Ditolak'),
        ('batal', 'Batal'),
    ], string='Status', default='draft',
        track_visibility='onchange')
    
    # def _generate_virtual_account(self):
    #     """Helper method to generate a Virtual Account"""
    #     return f"{random.randint(10000000, 99999999)}"

    @api.depends('soal_ids')

    def _compute_total_nilai(self):
        for record in self:
            # Menghitung total nilai dari soal_ids
            record.total_nilai = sum(soal.nilai for soal in record.soal_ids if soal.nilai)

    # Constraint untuk validasi nilai antara 1 hingga 10
    # @api.onchange(
    #     'tajwid', 'makhraj', 'fashahah', 'gharib', 'irama', 'tartil', 
    #     'motivasi', 'pemahaman', 'komitmen', 'kedisiplinan', 
    #     'pengetahuan', 'minat'
    # )
    # def _onchange_nilai(self):
    #     for record in self:
    #         fields_to_check = [
    #             'tajwid', 'makhraj', 'fashahah', 'gharib', 'irama', 
    #             'tartil', 'motivasi', 'pemahaman', 'komitmen', 
    #             'kedisiplinan', 'pengetahuan', 'minat'
    #         ]
            
    #         # Check each field for valid range (1-10)
    #         for field in fields_to_check:
    #             value = getattr(record, field)
    #             if value and (value < 1 or value > 10):
    #                 # Set the value to 0 to reset invalid input
    #                 setattr(record, field, 0)
    #                 return {
    #                     'warning': {
    #                         'title': 'Nilai Tidak Valid',
    #                         'message': f'Nilai untuk {field} harus berada antara 1 - 10. Nilai telah direset ke 0.',
    #                     }
    #                 }

    @api.model

    # def get_kuota_pendaftaran(self):
    #     # Ambil nilai dari config parameter, jika tidak ada gunakan default 7
    #     return int(self.env['ir.config_parameter'].sudo().get_param('kuota_pendaftaran', default=1))

    # kuota_pendaftaran = fields.Integer(
    #     string="Kuota Pendaftaran",
    #     default=lambda self: self.get_kuota_pendaftaran()
    # )

    def create(self, vals):
        # Get the current year
        current_year = fields.Date.context_today(self).year % 100
        
        # Search for existing records with the same year
        existing_records = self.search([('nomor_pendaftaran', 'ilike', f'{current_year}%')])
        
        # Determine the next sequence number
        if existing_records:
            last_number = max(int(record.nomor_pendaftaran[len(str(current_year)):]) for record in existing_records)
            next_number = last_number + 1
        else:
            next_number = 1
            
        # Generate the new nomor_pendaftaran
        vals['nomor_pendaftaran'] = f'{current_year}{str(next_number).zfill(4)}'

        # Generate UUID token
        vals['token'] = str(uuid.uuid4())

        record = super(DataPendaftaran, self).create(vals)

        if record.state == 'draft':
            # Buat data virtual account
            if not record.virtual_account:
                nopen = record.nomor_pendaftaran
                record.virtual_account = record._generate_virtual_account_temporary(nopen)
                record.status_va = 'temporary'
        return record

    def get_psb_statistics(self):
        total_pendaftar = self.search_count([])
        total_diterima = self.search_count([('state', '=', 'diterima')])
        
        # Mengambil nilai kuota pendaftaran dari ir.config_parameter
        config_param = self.env['ir.config_parameter'].sudo()
        kuota_pendaftaran = int(config_param.get_param('pesantren_pendaftaran.kuota_pendaftaran', default=0))

        sisa_kuota = kuota_pendaftaran - total_pendaftar

        return {
            'total_pendaftar': total_pendaftar,
            'total_diterima': total_diterima,
            'kuota_pendaftaran': kuota_pendaftaran,
            'sisa_kuota': max(sisa_kuota, 0),  # Pastikan tidak negatif
        }
    
    def hapus_pendaftaran_kadaluarsa(self):
        # Tentukan zona waktu Anda, misalnya 'Asia/Jakarta' untuk WIB
        timezone = pytz.timezone('Asia/Jakarta')
        for record in self:
            if record.tanggal_daftar:
                tgl_hari_ini = datetime.now(timezone).date()
                batas_waktu = record.tanggal_daftar + timedelta(days=7)

                # Debug
                # raise UserError(f"Tanggal setelah satu hari: {batas_waktu}, Tanggal hari ini: {tgl_hari_ini}")

                if tgl_hari_ini > batas_waktu:
                    pendaftaran_kadaluarsa = self.search([('state', '=', 'draft')])
                    pendaftaran_kadaluarsa.unlink()

    def action_terdaftar(self):
        self.state = 'terdaftar'

    def action_seleksi(self):
        self.state = 'seleksi'

    def action_diterima(self):
        self.state = 'diterima'

    def action_ditolak(self):
        self.state = 'ditolak'

    def action_batal(self):
        self.state = 'batal'

    def action_draft(self):
        # Optional: You can define additional actions for when "Draft" is clicked
        self.write({'state': 'draft'})


    def action_report_pendaftaran(self):
        # Logika untuk meng-generate laporan PDF atau aksi lainnya
        return self.env.ref('pesantren_pendaftaran.action_report_pendaftaran').report_action(self)

    # @api.model
    # def default_get(self, fields):
    # res = super(DataPendaftaran, self).default_get(fields)  # Use the exact class name here
    # res['jns_partner'] = 'calon_santri'
    # return res

    def write(self, vals):

        if 'state' in vals and vals['state'] == 'diterima':
            for record in self:
                # Buat akun orang tua jika belum ada
                if not record.orangtua_id:
                    orangtua = record.create_orangtua()
                    record.orangtua_id = orangtua.id

                # Buat data siswa jika belum ada
                if not record.siswa_id:
                    siswa = record.create_siswa()
                    record.siswa_id = siswa.id

                # Buat data virtual account
                # if not record.virtual_account:
                #     nisn = record.nisn
                #     record.virtual_account = record._generate_virtual_account(nisn)
                nis = record.nis
                jenjang = record.jenjang
                record.virtual_account = record._generate_virtual_account_permanent(nis, jenjang)
                record.status_va = 'permanent'

                # Buat data virtual account uang saku
                if not record.va_saku:
                    record.va_saku = record._generate_va_uangsaku(nis, jenjang)

                # Generate nis
                # if not record.nis:
                #     nisn = record.nisn
                #     record.nis = record._generate_nis(nisn)

        elif 'state' in vals and vals['state'] == 'ditolak':
            for record in self:
                record.virtual_account = False # Menghapus Virtual Account
                record.status_va = 'inactive'

        # Check if state is being changed to 'terdaftar'
        # if 'state' in vals and vals['state'] == 'diterima':
        #     for record in self:
        #         if not record.virtual_account:
        #             record.virtual_account = "01" + record._generate_virtual_account()

        return super(DataPendaftaran, self).write(vals)
    
    def create_orangtua(self):
        for record in self:
            """Fungsi untuk membuat akun orang tua di cdn.orangtua"""

            # Cek apakah email orang tua sudah ada di res.partner
            existing_partner = self.env['res.partner'].search([('email', '=', record.wali_email)], limit=1)

            if existing_partner:
                # Jika partner sudah ada, cek apakah data orang tua sudah ada
                existing_orangtua = self.env['cdn.orangtua'].sudo().search([('partner_id', '=', existing_partner.id)], limit=1)
                if existing_orangtua:
                    # Jika data orang tua sudah ada, gunakan data tersebut
                    return existing_orangtua
                else:
                     # Jika partner ada tapi data orang tua belum ada, buat data orang tua
                     orangtua_vals = {
                         'partner_id': existing_partner.id,
                         'hubungan': 'wali',
                         'email': record.wali_email,
                     }
                     orangtua = self.env['cdn.orangtua'].sudo().create(orangtua_vals)
                     return orangtua
            else:
                # Jika partner belum ada, buat data partner baru
                # Membuat data orangtua otomatis saat pendaftaran diterima
                partner_vals = {
                    'name': record.wali_nama,
                    'email': record.wali_email,  # Asumsi field email ada di model Pendaftaran
                    'phone': record.wali_telp,  # Asumsi field phone ada di model Pendaftaran
                    'city': record.kota_id.name,
                }
                
                # Membuat data partner untuk orang tua
                partner = self.env['res.partner'].create(partner_vals)

                orangtua_vals = {
                    'partner_id': partner.id,
                    'hubungan': 'wali',
                    'email': record.wali_email,
                }
                orangtua = self.env['cdn.orangtua'].sudo().create(orangtua_vals)

                # Mengatur password untuk user_id yang sudah dibuat otomatis
                if partner.user_id:  # Pastikan user_id sudah ada
                    password = record.wali_password
                    partner.user_id.write({'password': password,})

                # Mengirim email menggunakan mail.mail
                # email_values = {
                #     'subject': "Informasi Login Orang Tua Santri Baru Pesantren Daarul Qur'an Istiqomah",
                #     'email_to': record.wali_email,
                #     'body_html': f'''
                #         <p>Assalamualaikum Wr.wb, Bapak/Ibu {record.wali_nama}</p>
                #         <p>Akun OrangTua telah dibuat di sistem pesantren kami. Dengan ini kami kirimkan informasi akun login sebagai berikut:</p>
                #         <p style="font-style: italic; color: red;">Sebelum Bapak/Ibu menggunakan akun ini, harap mengganti password demi keamanan akun.</p>
                #         <a href="localhost:9069/web/reset_password" class="btn btn-link">Ganti Password</a>
                #         <ul>
                #             <li>Web Login   : Gunakan <a href="localhost:9069/odoo">Akun Anda</a></li>
                #             <li>Email       : {record.wali_email}</li>
                #             <li>Password    : {password}</li>
                #         </ul>
                #         <p>Apabila terdapat kesulitan saat login atau membutuhkan bantuan, Bapak/Ibu dapat menghubungi tim teknis kami melalui nomor telepon 0822 5207 9785/0853 9051 1124. <br> <br>
                #         Kami harap portal ini dapat memudahkan Bapak/Ibu dalam memantau perkembangan putra/putri selama berada di pesantren. <br> <br>
                #         Demikian informasi ini kami sampaikan. Atas perhatian dan kerjasamanya, kami ucapkan terima kasih.<br> <br> <br>

                #         Hormat kami, <br>
                #         Admin Pendaftaran <br>
                #         Pesantren Tahfizh Daarul Qur'an Istiqomah</p>
                #     ''',
                # }

                # email_values = {
                #     'subject': "Informasi Login Orang Tua Santri Baru Pesantren Daarul Qur'an Istiqomah",
                #     'email_to': record.wali_email,
                #     'body_html': f'''
                #         <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9;">
                #             <div style="text-align: center; margin-bottom: 20px;">
                #                 <img src="https://example.com/logo.png" alt="Pesantren Daarul Qur'an Istiqomah" style="max-width: 150px;">
                #             </div>
                #             <h2 style="color: #333; text-align: center;">Informasi Login Akun Orang Tua</h2>
                #             <p style="color: #555;">Assalamualaikum Wr. Wb,</p>
                #             <p style="color: #555;">Bapak/Ibu <strong>{record.wali_nama}</strong>,</p>
                #             <p style="color: #555;">Akun Orang Tua telah dibuat di sistem pesantren kami. Berikut informasi login Anda:</p>
                #             <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                #                 <tr>
                #                     <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Email</td>
                #                     <td style="padding: 8px; border: 1px solid #ddd;">{record.wali_email}</td>
                #                 </tr>
                #                 <tr>
                #                     <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Password</td>
                #                     <td style="padding: 8px; border: 1px solid #ddd;">{password}</td>
                #                 </tr>
                #                 <tr>
                #                     <td style="padding: 8px; border: 1px solid #ddd; font-weight: bold;">Web Login</td>
                #                     <td style="padding: 8px; border: 1px solid #ddd;">
                #                         <a href="http://localhost:9069/odoo" style="color: #0066cc; text-decoration: none;">Klik di sini untuk login</a>
                #                     </td>
                #                 </tr>
                #             </table>
                #             <p style="color: #555; font-style: italic;">Sebelum menggunakan akun ini, harap mengganti password demi keamanan.</p>
                #             <p style="text-align: center;">
                #                 <a href="http://localhost:9069/web/reset_password" style="background-color: #0066cc; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Ganti Password</a>
                #             </p>
                #             <p style="color: #555;">Apabila terdapat kesulitan atau membutuhkan bantuan, silakan hubungi tim teknis kami melalui nomor:</p>
                #             <ul style="color: #555;">
                #                 <li>0822 5207 9785</li>
                #                 <li>0853 9051 1124</li>
                #             </ul>
                #             <p style="color: #555;">Kami berharap portal ini dapat membantu Bapak/Ibu memantau perkembangan putra/putri selama berada di pesantren.</p>
                #             <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                #             <p style="text-align: center; color: #888; font-size: 12px;">
                #                 Pesantren Tahfizh Daarul Qur'an Istiqomah<br>
                #                 <a href="http://example.com" style="color: #0066cc; text-decoration: none;">Website Kami</a>
                #             </p>
                #         </div>
                #     ''',
                # }

                email_values = {
                    'subject': "Informasi Login Orang Tua Santri Baru Pesantren Daarul Qur'an Istiqomah",
                    'email_to': record.wali_email,
                    'body_html': f'''
                        <div style="background-color: #d9eaf7; padding: 20px; font-family: Arial, sans-serif;">
                            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden;">
                                <!-- Header -->
                                <div style="background-color: #0066cc; color: #ffffff; text-align: center; padding: 20px;">
                                    <h1 style="margin: 0; font-size: 24px;">Pesantren Daarul Qur'an Istiqomah</h1>
                                </div>
                                <!-- Body -->
                                <div style="padding: 20px; color: #555555;">
                                    <p style="margin: 0 0 10px;">Assalamualaikum Wr. Wb,</p>
                                    <p style="margin: 0 0 20px;">
                                        Bapak/Ibu <strong>{record.wali_nama}</strong>,<br>
                                        Akun Orang Tua telah dibuat di sistem pesantren kami. Berikut adalah informasi login Anda:
                                    </p>
                                    <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                        <table style="width: 100%; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 8px; font-weight: bold; color: #333333;">Email</td>
                                                <td style="padding: 8px; color: #555555;">{record.wali_email}</td>
                                            </tr>
                                        </table>
                                    </div>
                                    <p style="text-align: center;">
                                        <a href="http://localhost:9069/odoo" style="background-color: #0066cc; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                                            Masuk Ke Akun Anda
                                        </a>
                                    </p>
                                    <p style="margin: 20px 0;">
                                        Apabila terdapat kesulitan atau membutuhkan bantuan, silakan hubungi tim teknis kami melalui nomor:
                                    </p>
                                    <ul style="margin: 0; padding-left: 20px; color: #555555;">
                                        <li>0822 5207 9785</li>
                                        <li>0853 9051 1124</li>
                                    </ul>
                                    <p style="margin: 20px 0;">
                                        Kami berharap portal ini dapat membantu Bapak/Ibu memantau perkembangan putra/putri selama berada di pesantren.
                                    </p>
                                </div>
                                <!-- Footer -->
                                <div style="background-color: #f1f1f1; text-align: center; padding: 10px;">
                                    <p style="font-size: 12px; color: #888888; margin: 0;">
                                        &copy; 2024 Pesantren Tahfizh Daarul Qur'an Istiqomah. All rights reserved.
                                    </p>
                                </div>
                            </div>
                        </div>
                    ''',
                }



                # Membuat dan mengirim email
                mail = self.env['mail.mail'].sudo().create(email_values)
                mail.send()

                return orangtua

    def create_siswa(self):
        for record in self:
            """Fungsi untuk membuat data siswa dari pendaftaran"""
            siswa_vals = {
                'name'                  : record.partner_id.name,
                'propinsi_id'           : record.provinsi_id.id,
                'kota_id'               : record.kota_id.id,
                'kecamatan_id'          : record.kecamatan_id.id,
                'street'                : record.alamat,
                'nisn'                  : record.nisn,
                'nis'                   : record.nis,
                'nik'                   : record.nik,
                'jenjang'               : record.jenjang,
                'kewarganegaraan'       : record.kewarganegaraan,
                'orangtua_id'           : record.orangtua_id.id,
                'tgl_lahir'             : record.tanggal_lahir,
                'jns_kelamin'           : record.gender,
                'tmp_lahir'             : record.kota_lahir,
                'gol_darah'             : record.golongan_darah,
                'anak_ke'               : record.anak_ke,
                'asal_sekolah'          : record.asal_sekolah,
                'status_sekolah_asal'   : record.status_sekolah_asal,
                'telp_asal_sek'         : record.telp_asal_sek,
                'alamat_asal_sek'       : record.alamat_asal_sek,
                'virtual_account'       : record.virtual_account,
                'va_saku'               : record.va_saku,

                # Orang Tua
                'ayah_nama'             : record.nama_ayah,
                'ayah_tgl_lahir'        : record.tanggal_lahir_ayah,
                'ayah_telp'             : record.telepon_ayah,
                'ayah_pekerjaan_id'     : record.pekerjaan_ayah.id,
                'ayah_agama'            : record.agama_ayah,
                'ayah_warganegara'      : record.kewarganegaraan_ayah,
                'ayah_pendidikan_id'    : record.pendidikan_ayah.id,

                'ibu_nama'              : record.nama_ibu,
                'ibu_tgl_lahir'         : record.tanggal_lahir_ibu,
                'ibu_telp'              : record.telepon_ibu,
                'ibu_pekerjaan_id'      : record.pekerjaan_ibu.id,
                'ibu_agama'             : record.agama_ibu,
                'ibu_warganegara'       : record.kewarganegaraan_ibu,
                'ibu_pendidikan_id'     : record.pendidikan_ibu.id,

                'wali_nama'             : record.wali_nama,
                'wali_tgl_lahir'        : record.wali_tgl_lahir,
                'wali_telp'             : record.wali_telp,
                'wali_email'            : record.wali_email,
                'wali_hubungan'         : record.wali_hubungan,
            }
            siswa = self.env['cdn.siswa'].sudo().create(siswa_vals)
            return siswa
    

    # def generate_password_akun_ortu(self):
    #     # Kombinasi karakter yang akan digunakan untuk password
    #     characters = string.ascii_letters + string.digits  # Huruf besar, kecil, dan angka
    #     # Menghasilkan password acak sepanjang 8 karakter
    #     password = ''.join(random.choices(characters, k=8))
    #     return password
    
    # def _generate_virtual_account(self, vals, nis):
    #     # if not self.bank or not self.bank.kode_bank:
    #     #     raise ValueError("Kode bank tidak ditemukan. Pastikan Anda memilih bank dengan kode yang valid.")
        
    #     bank = self.env['ubig.bank'].browse(vals.get('bank'))

    #     kode_va_bank = bank.kode_va_bank if bank else ''
    #     account_type = "01"

    #     nis = nis

    #     return f"{kode_va_bank}{account_type}{nis}"


    def _generate_virtual_account_temporary(self, nopen):
        for record in self:
            kode_bank_bri = "002"
            # account_type = "01"
            # Pastikan NIS selalu memiliki panjang tertentu
            nopen = nopen # Contoh padding NIS menjadi 6 digit

            return f"{kode_bank_bri}{nopen}"
        
    def _generate_virtual_account_permanent(self, nis, jenjang):
        for record in self:
            kode_bank_bri = "002"
            account_type = "01"
            # Pastikan NIS selalu memiliki panjang tertentu
            nis = nis

            if jenjang == "sdmi":
                kode_jenjang = "10"
                return f"{kode_bank_bri}{kode_jenjang}{account_type}{nis}"
            elif jenjang == "smpmts":
                kode_jenjang = "20"
                return f"{kode_bank_bri}{kode_jenjang}{account_type}{nis}"
            elif jenjang == "smama":
                kode_jenjang = "30"
                return f"{kode_bank_bri}{kode_jenjang}{account_type}{nis}"
        
    def _generate_va_uangsaku(self, nis, jenjang):
        for record in self:
            kode_bank_bri = "002"
            account_type = "02"
            # Pastikan NIS selalu memiliki panjang tertentu
            nis = nis

            if jenjang == "sdmi":
                kode_jenjang = "10"
                return f"{kode_bank_bri}{kode_jenjang}{account_type}{nis}"
            elif jenjang == "smpmts":
                kode_jenjang = "20"
                return f"{kode_bank_bri}{kode_jenjang}{account_type}{nis}"
            elif jenjang == "smama":
                kode_jenjang = "30"
                return f"{kode_bank_bri}{kode_jenjang}{account_type}{nis}"
        
    # def _generate_nis(self, nisn):
    #     for record in self:
    #         nisn = nisn
    #         if nisn and len(nisn) >= 5:
    #             last_nisn = nisn[-5:]
    #             npsn = record.jenjang_id.npsn
    #             last_npsn = npsn[-3:]
    #             thn_sekarang = str(datetime.now().year)
    #             last_thn_sekarang = thn_sekarang[-2:]
    #             nis = f"{last_nisn}{last_npsn}{last_thn_sekarang}"
    #         else:
    #             last_nisn = ''
    #     return nis


    def get_formatted_tanggal(self):
        if self.tanggal_daftar:
            return format_date(self.env, self.tanggal_daftar, date_format='dd MMMM yyyy')
        return 'Tanggal tidak tersedia'



# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'

#     # Tambahkan field konfigurasi
#     kuota_pendaftaran = fields.Integer(
#         string="Kuota Pendaftaran",
#         default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('kuota_pendaftaran', default=1)),
#     )

#     # Override fungsi set_values untuk menyimpan nilai
#     def set_values(self):
#         super(ResConfigSettings, self).set_values()
#         self.env['ir.config_parameter'].sudo().set_param('kuota_pendaftaran', self.kuota_pendaftaran)


class ResConfigSettings(models.TransientModel):
   _inherit = 'res.config.settings'
   
   kuota_pendaftaran = fields.Integer(
        string="Kuota Pendaftaran Santri",
        config_parameter='pesantren_pendaftaran.kuota_pendaftaran',
        default=0,
        help="Jumlah kuota pendaftaran"
    )
   tgl_mulai_pendaftaran = fields.Datetime(
        string="Tanggal Mulai Pendaftaran",
        config_parameter='pesantren_pendaftaran.tgl_mulai_pendaftaran',
        help="Atur tgl dibukanya pendaftaran",
    )
   tgl_akhir_pendaftaran = fields.Datetime(
        string="Tanggal Akhir Pendaftaran",
        config_parameter='pesantren_pendaftaran.tgl_akhir_pendaftaran',
        help="Atur tgl akhir dari pendaftaran",
    )
   tgl_mulai_seleksi = fields.Datetime(
        string="Tanggal Mulai Seleksi",
        config_parameter='pesantren_pendaftaran.tgl_mulai_seleksi',
        help="Atur tgl mulai seleksi",
    )
   tgl_akhir_seleksi = fields.Datetime(
        string="Tanggal Akhir Seleksi",
        config_parameter='pesantren_pendaftaran.tgl_akhir_seleksi',
        help="Atur tgl akhir seleksi",
    )
   tgl_pengumuman_hasil_seleksi = fields.Datetime(
        string="Tanggal Pengumuman Hasil Seleksi",
        config_parameter='pesantren_pendaftaran.tgl_pengumuman_hasil_seleksi',
        help="Atur tgl pengumuman hasil seleksi",
    )
   
   is_halaman_pengumuman = fields.Boolean(
        string="Tampilkan Halaman Pengumuman",
        config_parameter='pesantren_pendaftaran.is_halaman_pengumuman',
        default=False,
        help="Tampilkan halaman pengumuman",
    )

   @api.model
   def set_values(self):
        res = super(ResConfigSettings, self).set_values()

        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.kuota_pendaftaran',
            self.kuota_pendaftaran
        )
        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.tgl_mulai_pendaftaran',
            self.tgl_mulai_pendaftaran.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_mulai_pendaftaran else False
        )
        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.tgl_akhir_pendaftaran',
            self.tgl_akhir_pendaftaran.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_akhir_pendaftaran else False
        )
        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.tgl_mulai_seleksi',
            self.tgl_mulai_seleksi.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_mulai_seleksi else False
        )
        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.tgl_akhir_seleksi',
            self.tgl_akhir_seleksi.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_akhir_seleksi else False
        )
        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.tgl_pengumuman_hasil_seleksi',
            self.tgl_pengumuman_hasil_seleksi.strftime('%Y-%m-%d %H:%M:%S') if self.tgl_pengumuman_hasil_seleksi else False
        )

        self.env['ir.config_parameter'].set_param(
            'pesantren_pendaftaran.is_halaman_pengumuman',
            self.is_halaman_pengumuman
        )

        return res

   @api.model
   def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        icp = self.env['ir.config_parameter']
        
        # Tentukan default values jika tidak ada di ir.config_parameter
        tgl_mulai_pendaftaran = icp.get_param('pesantren_pendaftaran.tgl_mulai_pendaftaran', default=False)
        if not tgl_mulai_pendaftaran:
            tgl_mulai_pendaftaran = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')

        tgl_akhir_pendaftaran = icp.get_param('pesantren_pendaftaran.tgl_akhir_pendaftaran', default=False)
        if not tgl_akhir_pendaftaran:
            tgl_akhir_pendaftaran = (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S')

        tgl_mulai_seleksi = icp.get_param('pesantren_pendaftaran.tgl_mulai_seleksi', default=False)
        if not tgl_mulai_seleksi:
            tgl_mulai_seleksi = (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S')

        tgl_akhir_seleksi = icp.get_param('pesantren_pendaftaran.tgl_akhir_seleksi', default=False)
        if not tgl_akhir_seleksi:
            tgl_akhir_seleksi = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S')

        tgl_pengumuman_hasil_seleksi = icp.get_param('pesantren_pendaftaran.tgl_pengumuman_hasil_seleksi', default=False)
        if not tgl_pengumuman_hasil_seleksi:
            tgl_pengumuman_hasil_seleksi = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')

        res.update({
            'kuota_pendaftaran': int(icp.get_param('pesantren_pendaftaran.kuota_pendaftaran', default=0)),
            'tgl_mulai_pendaftaran': tgl_mulai_pendaftaran,
            'tgl_akhir_pendaftaran': tgl_akhir_pendaftaran,
            'tgl_mulai_seleksi': tgl_mulai_seleksi,
            'tgl_akhir_seleksi': tgl_akhir_seleksi,
            'tgl_pengumuman_hasil_seleksi': tgl_pengumuman_hasil_seleksi,
            'is_halaman_pengumuman': icp.get_param('pesantren_pendaftaran.is_halaman_pengumuman', default=False),
        })
        return res


class SeleksiPenilaian(models.Model):
    _name = 'seleksi.penilaian'
    _description = 'Penilaian Seleksi Siswa Baru'

    name            = fields.Char(string='Nama Penilaian', required=True)
    soal_ids        = fields.One2many(comodel_name='seleksi.soal', inverse_name='penilaian_id', string='Soal Seleksi')
    nilai           = fields.Integer(string='Nilai Seleksi', default=0)
    penilaian_id    = fields.Many2one('seleksi.penilaian', string='Penilaian ID')  # Many2one ke penilaian lain
    daftar_soal     = fields.Text(string='Daftar Soal', compute='_compute_daftar_soal', store=True)

    @api.depends('soal_ids')
    def _compute_daftar_soal(self):
        for rec in self:
            rec.daftar_soal = ', '.join(soal.name for soal in rec.soal_ids)

    @api.depends('soal_ids')
    def _compute_name(self):
        for rec in self:
            rec.name = 'Penilaian: ' + ', '.join(soal.name for soal in rec.soal_ids)

    @api.onchange('soal_ids')
    def _onchange_soal_ids(self):
        # Mengisi penilaian_id berdasarkan soal_ids yang terpilih
        if self.soal_ids:
            # Ambil penilaian_id dari soal pertama yang dipilih
            self.penilaian_id = self.soal_ids[0].penilaian_id.id


class SoalSeleksi(models.Model):
    _name = 'seleksi.soal'
    _description = 'Soal untuk Seleksi Siswa Baru'

    name            = fields.Char(string='Nama Soal', required=True)
    active          = fields.Boolean(string='Aktif', default=True)
    penilaian_id    = fields.Many2one(comodel_name='seleksi.penilaian', string='Penilaian', required=True)
    nilai           = fields.Integer(string='Nilai', default=0)
    jenjang         = fields.Selection(selection=[('sdmi','SD / MI'),('smpmts','SMP / MTS'),('smama','SMA / MA'),('smk','SMK')], string='Jenjang', required=True)
    deskripsi       = fields.Text(string='Deskripsi Soal')

    @api.depends('penilaian_id', 'name')
    def _compute_name(self):
        for record in self:
            # Set the name of soal as the combination of penilaian and soal names
            record.name = '%s - %s' % (record.penilaian_id.name, record.name)

