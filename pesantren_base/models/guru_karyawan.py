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
# args=None
    def activate_account(self):
        # Mengambil email dan jenis pegawai langsung dari instance hr.employee
        if not self.work_email:
            raise UserError("Email tidak ditemukan di data karyawan.")
        if not self.nip or not self.name:
            raise UserError("NIP atau Nama karyawan belum diisi.")
        
        # Cari user berdasarkan email dari work_email
        user = self.env['res.users'].search([('login', '=', self.work_email)], limit=1)
        
        if not user:
            raise UserError(f"User dengan email {self.work_email} tidak ditemukan.")

        # Menentukan group yang sesuai berdasarkan jenis pegawai
        groups_to_add = []
        
        if self.jns_pegawai == 'guruquran':
            groups_to_add.append(self.env.ref('pesantren_guruquran.group_guru_quran_staff'))
            groups_to_add.append(self.env.ref('pesantren_kesantrian.group_kesantrian_user'))
            groups_to_add.append(self.env.ref('pesantren_base.group_sekolah_user'))
        elif self.jns_pegawai == 'guru':
            groups_to_add.append(self.env.ref('pesantren_guru.group_guru_staff'))
            groups_to_add.append(self.env.ref('pesantren_base.group_sekolah_user'))
            groups_to_add.append(self.env.ref('hr.group_hr_user'))
        elif self.jns_pegawai in ['musyrif', 'ustadz']:
            groups_to_add.append(self.env.ref('pesantren_musyrif.group_musyrif_staff'))
            groups_to_add.append(self.env.ref('pesantren_kesantrian.group_kesantrian_user'))
            groups_to_add.append(self.env.ref('pesantren_base.group_sekolah_user'))
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
        new_password = f"{self.nip[:6]}"  # Gunakan 4 digit pertama NIP
        user.write({'password': new_password})

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
    