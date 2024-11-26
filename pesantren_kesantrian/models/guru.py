from odoo import api, fields, models
import re

class Guru(models.Model):
    _inherit = 'hr.employee'
    _sql_constraints = [
        ('email_uniq', 'unique(work_email)', 'Email sudah ada!'),
    ]

    work_email = fields.Char(string='Email', required=True)

    @api.model
    def create(self, vals):
        res = super(Guru, self).create(vals)
        #create partner
        partner = self.env['res.partner'].create({
            'name' : res.name,
            'email' : res.work_email,
        })
        #create user
        users = self.env['res.users'].create({
            'login' : res.work_email,
            'partner_id' : partner.id,
            'password' : 'employee',
        })
        res.user_id = users.id
        # add groups
        # groups = [
        #     (4, self.env.ref('pesantren_base.group_sekolah_user').id),
        #     (4, self.env.ref('pesantren_kesantrian.group_kesantrian_user').id),
        # ]
        # if res.jns_pegawai == 'ustadz':
        #     groups.append((4, self.env.ref('pesantren_kesantrian.group_kesantrian_user').id))
        # elif res.jns_pegawai == 'musyrif':
        #     groups.append((4, self.env.ref('pesantren_musyrif.group_musyrif_user').id))
        #     groups.append((4, self.env.ref('pesantren_keuangan.group_keuangan_user').id))
        # elif res.jns_pegawai == 'guru':
        #     groups.append((4, self.env.ref('pesantren_base.group_sekolah_sekolah').id))
        #     groups.append((4, self.env.ref('pesantren_guru.group_guru_user').id))
        # elif res.jns_pegawai == 'guruquran':
        #     groups.append((4, self.env.ref('pesantren_guruquran.group_guru_quran').id))
        #     groups.append((4, self.env.ref('pesantren_guruquran.group_guru_quran_user').id))
        # elif res.jns_pegawai == 'kesehatan':
        #     groups.append((4, self.env.ref('pesantren_kesantrian.group_kesantrian_kesehatan').id))
        # elif res.jns_pegawai == 'keamanan':
        #     groups.append((4, self.env.ref('pesantren_kesantrian.group_kesantrian_keamanan').id))
        #     groups.append((4, self.env.ref('pesantren_kesantrian.group_kesantrian_perijinan').id))
        # elif res.jns_pegawai == 'kasrama':
        #     groups.append((4, self.env.ref('pesantren_kesantrian.group_kesantrian_kepala_asrama').id))
        #     groups.append((4, self.env.ref('pesantren_kesantrian.group_kesantrian_manager').id))
        # users.groups_id = groups
        return res
    def unlink(self):
        for guru in self:
            users = self.env['res.users'].browse(guru.user_id.id)
            if users:
                partner = users.partner_id
                users.unlink()
                partner.unlink()
        return super(Guru, self).unlink()
    

    @api.constrains('work_email')
    def _check_email(self):
        for guru in self:
            if guru.work_email:
                #regex
                if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', guru.work_email):
                    raise models.ValidationError('Email tidak valid!')
