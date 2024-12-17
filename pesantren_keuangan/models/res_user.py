from odoo import models, api, _
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    def konfigurasi_akses_keuangan(self):
        """Update user groups for financial access."""
        for user in self:
            # Hapus semua grup yang sudah ada
            user.groups_id = [(5, 0, 0)]  # Clear all groups

            # Tambahkan grup akses yang baru
            user.groups_id = [(6, 0, [
                self.env.ref('base.group_user').id,  # Default Internal User
                self.env.ref('account.group_account_manager').id,
                self.env.ref('pesantren_keuangan.group_keuangan_manager').id,  # Grup Keuangan
                self.env.ref('pesantren_base.group_sekolah_user').id,  # Grup Sekolah
                self.env.ref('hr_holidays.group_hr_holidays_user').id,  # Menambahkan grup Cuti
                self.env.ref('hr.group_hr_user').id,  # Menambahkan grup HR User
                self.env.ref('hr_attendance.group_hr_attendance_officer').id,  # Menambahkan grup Absensi
            ])]

        # Tambahkan notifikasi bahwa hak akses berhasil diubah
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Konfigurasi Hak Akses'),
                'message': _('Hak akses keuangan berhasil diperbarui untuk pengguna ini.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    @api.model
    def create(self, vals):
        # Pastikan email diisi dan disinkronkan ke work_email
        if 'email' in vals and vals['email']:
            vals['work_email'] = vals['email']  # Set work_email
        elif 'login' in vals:  # Jika email kosong, gunakan login sebagai work_email
            vals['work_email'] = vals['login']
        else:
            raise ValueError(_("Email atau login harus diisi untuk membuat user."))
        
        user = super(ResUsers, self).create(vals)
        return user
