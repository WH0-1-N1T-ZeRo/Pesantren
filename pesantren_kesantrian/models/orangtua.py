from odoo import api, fields, models


class OrangTua(models.Model):
    _inherit = 'cdn.orangtua'

    @api.model
    def create(self, vals):
        # Membuat record 'OrangTua' menggunakan inheritance
        res = super(OrangTua, self).create(vals)
        
        # Membuat user baru dengan login berbasis email dan password default
        user = self.env['res.users'].with_context(no_reset_password=True).sudo().create({
            'login': res.email,  # Menggunakan email dari field model
            'name': res.name,  # Nama pengguna
            'company_id': self.env.ref('base.main_company').id,  # Mengatur perusahaan default
            'partner_id': res.partner_id.id,  # Hubungkan dengan partner terkait
            'password': 'partner',  # Password default
            'groups_id': [(6, 0, [
                # Assign grup internal user (standard)
                self.env.ref('base.group_user').id, 
                # Assign grup orang tua
                self.env.ref('pesantren_kesantrian.group_kesantrian_orang_tua').id,
                # Assign grup sekolah user
                self.env.ref('pesantren_base.group_sekolah_user').id,
                # Assign grup sekolah user
                self.env.ref('pesantren_kesantrian.group_kesantrian_user').id,
                # Assign grup keuangan user
                self.env.ref('pesantren_keuangan.group_keuangan_user').id
            ])]
        })
        
        res.user_id = user.id
        return res

    def unlink(self):
        for orangtua in self:
            users = self.env['res.users'].search([('partner_id', '=', orangtua.partner_id.id)])
            if users:
                partner = users.partner_id
                users.unlink()
                partner.unlink()
        return super(OrangTua,self).unlink()
    


