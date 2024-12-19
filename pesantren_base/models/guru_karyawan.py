from odoo import api, fields, models
from odoo.exceptions import UserError

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    nip = fields.Char('NIP')
    lembaga = fields.Selection([('SMP', 'SMP/MTS'), ('SMA', 'SMA/MA')], string='Lembaga', default='SMA')
    pendidikan_guru_ids = fields.One2many(comodel_name="edu.employee", inverse_name="employee_id", string="Riwayat Pendidikan", help="")
    marital = fields.Selection(string='Status Pernikahan', selection=[('single', 'Belum Kawin'), ('married', 'Menikah'), ('divorced', 'Cerai Hidup'), ('cerai', 'Cerai Mati')])
    jns_pegawai = fields.Selection([
        ('musyrif', 'Musyrif'),
        ('ustadz', 'Ustadz'),
        ('guru', 'Guru'),
        ("guruquran", "Guru Qur'an"),
        ('keamanan', 'Keamanan'),
        ('kesehatan', 'Kesehatan'),
        ('kasrama', 'Kepala Asrama')
    ], string='Jenis Pegawai')
    mata_pelajaran_ids = fields.Many2many(comodel_name="cdn.mata_pelajaran", string="Mata Pelajaran", help="")
    password = fields.Char(
        string='Password',
        compute="_compute_password",
        store=True
    )

    @api.depends('nip')
    def _compute_password(self):
        for record in self:
            if record.nip and len(record.nip) >= 6:
                record.password = record.nip[:6]
            else:
                record.password = ''
    
# args=None
    def activate_account(self):
        # Mengambil email dan jenis pegawai langsung dari instance hr.employee
        if not self.work_email:
            raise UserError("Email tidak ditemukan di data karyawan.")
        if not self.password or not self.name:
            raise UserError("Password atau Nama karyawan belum diisi.")
        
        # Cari user berdasarkan email dari work_email
        user = self.env['res.users'].search([('login', '=', self.work_email)], limit=1)
        
        if not user:
            raise UserError(f"User dengan email {self.work_email} tidak ditemukan.")

        user.groups_id = [(5, 0, 0)]  # Menghapus semua grup yang sudah ada

        # Menentukan group yang sesuai berdasarkan jenis pegawai
        groups_to_add = []
        groups_to_add.append(self.env.ref('base.group_user'))
        if self.jns_pegawai == 'guruquran':
            groups_to_add.append(self.env.ref('pesantren_guruquran.group_guru_quran_staff'))
            groups_to_add.append(self.env.ref('pesantren_kesantrian.group_kesantrian_user'))
            groups_to_add.append(self.env.ref('pesantren_base.group_sekolah_user'))
            groups_to_add.append(self.env.ref('hr_holidays.group_hr_holidays_user'))  # Menambahkan grup Cuti
            groups_to_add.append(self.env.ref('hr.group_hr_user'))  # Menambahkan grup HR User
            groups_to_add.append(self.env.ref('hr_attendance.group_hr_attendance_officer'))  # Menambahkan grup Absensi
        elif self.jns_pegawai == 'guru':
            groups_to_add.append(self.env.ref('pesantren_guru.group_guru_staff'))
            groups_to_add.append(self.env.ref('pesantren_base.group_sekolah_user'))
            groups_to_add.append(self.env.ref('hr_holidays.group_hr_holidays_user'))  # Menambahkan grup Cuti
            groups_to_add.append(self.env.ref('hr.group_hr_user'))  # Menambahkan grup HR User
            groups_to_add.append(self.env.ref('hr_attendance.group_hr_attendance_officer'))  # Menambahkan grup Absensi
        elif self.jns_pegawai in ['musyrif', 'ustadz']:
            groups_to_add.append(self.env.ref('pesantren_musyrif.group_musyrif_staff'))
            groups_to_add.append(self.env.ref('pesantren_kesantrian.group_kesantrian_user'))
            groups_to_add.append(self.env.ref('pesantren_base.group_sekolah_user'))
            groups_to_add.append(self.env.ref('hr_holidays.group_hr_holidays_user'))  # Menambahkan grup Cuti
            groups_to_add.append(self.env.ref('hr.group_hr_user'))  # Menambahkan grup HR User
            groups_to_add.append(self.env.ref('hr_attendance.group_hr_attendance_officer'))  # Menambahkan grup Absensi
        else:
            groups_to_add.append(self.env.ref('pesantren_base.group_sekolah_user'))
            groups_to_add.append(self.env.ref('pesantren_kesantrian.group_kesantrian_user'))
        
        if not groups_to_add:
            raise UserError("Jenis pegawai tidak terdaftar untuk penambahan group.")
        
        # Menambahkan semua grup yang diperlukan ke user
        for group in groups_to_add:
            if group not in user.groups_id:
                user.groups_id = [(4, group.id)]

        # Atur ulang password user dengan format name-nip
        new_password = f"{self.password}"  # Gunakan 4 digit pertama NIP
        masked_password = new_password[:2] + '*' * (len(new_password) - 4) + new_password[-2:]

        user.write({'password': new_password})

        email_values = { 
                    'subject': "Akun Diaktifkan", 
                    'email_to': self.work_email, 
                    'body_html': f''' 
                        <div style="background-color: #f0f8ff; padding: 20px; font-family: Arial, sans-serif;"> 
                            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);"> 
                                <!-- Header --> 
                                <div style="background-color: #0078d7; color: #ffffff; text-align: center; padding: 25px;"> 
                                    <h1 style="margin: 0; font-size: 26px;">Aktivasi Akun Anda</h1> 
                                </div> 
                                <!-- Body --> 
                                <div style="padding: 20px; color: #333333;"> 
                                    <p style="margin: 0 0 10px; font-size: 16px;">Assalamualaikum Wr. Wb,</p> 
                                    <p style="margin: 0 0 20px; font-size: 16px;"> 
                                        Selamat, akun Anda telah berhasil diaktifkan! Berikut adalah informasi akun Anda: 
                                    </p> 
                                    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;"> 
                                        <table style="width: 100%; border-collapse: collapse;"> 
                                            <tr> 
                                                <td style="padding: 10px; font-weight: bold; color: #555555;">Email :</td> 
                                                <td style="padding: 10px; color: #555555;">{self.work_email}</td> 
                                            </tr> 
                                            <tr> 
                                                <td style="padding: 10px; font-weight: bold; color: #555555;">Kata Sandi :</td> 
                                                <td style="padding: 10px; color: #555555;">{masked_password}</td> 
                                            </tr> 
                                            <tr> 
                                                <td style="padding: 10px; font-weight: bold; color: #555555;">Jenis Akun :</td> 
                                                <td style="padding: 10px; color: #555555;">{self.jns_pegawai}</td> 
                                            </tr> 
                                            <tr> 
                                                <td style="padding: 10px; font-weight: bold; color: #555555;">Tanggal Aktivasi :</td> 
                                                <td style="padding: 10px; color: #555555;">{fields.Datetime.now()}</td> 
                                            </tr> 
                                        </table> 
                                    </div> 
                                    <p style="text-align: center;"> 
                                        <a href="https://aplikasi.dqi.ac.id/login" style="background-color: #0078d7; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 16px;"> 
                                            Masuk Ke Akun Anda 
                                        </a> 
                                    </p> 
                                    <p style="margin: 20px 0; font-size: 14px;"> 
                                        Apabila Anda mengalami kendala, silakan hubungi tim teknis kami melalui nomor berikut: 
                                    </p> 
                                    <ul style="margin: 0; padding-left: 20px; color: #555555; font-size: 14px;"> 
                                        <li>0822 5207 9785</li> 
                                        <li>0853 9051 1124</li> 
                                    </ul> 
                                    <p style="margin: 20px 0; font-size: 14px;"> 
                                        Terima kasih telah menggunakan layanan kami. Kami berharap akun ini dapat membantu Anda dalam menjalankan aktivitas di pesantren. 
                                    </p> 
                                </div> 
                                <!-- Footer --> 
                                <div style="background-color: #f1f1f1; text-align: center; padding: 15px; border-top: 1px solid #dddddd;"> 
                                    <p style="font-size: 12px; color: #888888; margin: 0;"> 
                                        &copy; 2024 Pesantren Tahfizh Daarul Qur'an Istiqomah. All rights reserved. 
                                    </p> 
                                </div> 
                            </div> 
                        </div> 
                    ''' 
                }

        mail = self.env['mail.mail'].sudo().create(email_values)
        mail.send()


        # Arahkan ke form user yang baru saja diperbarui
        return {
            'type': 'ir.actions.act_window',
            'name': 'User',
            'res_model': 'res.users',
            'res_id': user.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }

class pendidikan_guru(models.Model):
    _name               = 'edu.employee'
    _description        = 'Riwayat Pendidikan Guru'

    name                = fields.Char(string='Nama Institusi')
    jenjang             = fields.Selection(string='Jenjang', selection=[('sd', 'SD/MI'), ('smp', 'SMP/MTS'),('sma', 'SMA/MA'),('diploma', 'D1/D2/D3'),('sarjana', 'D4/S1'),('pasca', 'S2/S3'),('lainnya', 'Lainnya/Non Formal')])
    fakultas            = fields.Char(string='Fakultas/Jurusan')
    gelar               = fields.Char(string='Gelar')
    karya_ilmiah        = fields.Char(string='Skripsi/Tesis/Disertasi')
    lulus               = fields.Date(string='Lulus')
    employee_id         = fields.Many2one(comodel_name="hr.employee",  string="Guru/Karyawan",  help="")
    