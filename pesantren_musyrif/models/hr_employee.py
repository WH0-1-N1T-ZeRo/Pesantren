# from odoo import api, models

# class hr_employee(models.Model):
#     _inherit = 'hr.employee'

#     @api.model
#     def create(self, vals):
#         employee = super(hr_employee, self).create(vals)
#         group_musyrif = self.env.ref('pesantren_musyrif.group_musyrif_musyrif')
#         if vals.get('jns_pegawai') == 'musyrif' and employee.user_id:
#             employee.user_id.groups_id = [(4, group_musyrif.id)]
#         return employee

#     def write(self, vals):
#         res = super(hr_employee, self).write(vals)
#         group_musyrif = self.env.ref('pesantren_musyrif.group_musyrif_musyrif')
#         for record in self:
#             if record.jns_pegawai == 'musyrif' and group_musyrif not in record.user_id.groups_id:
#                 record.user_id.groups_id = [(4, group_musyrif.id)]
#             elif record.jns_pegawai != 'musyrif' and group_musyrif in record.user_id.groups_id:
#                 record.user_id.groups_id = [(3, group_musyrif.id)]
#         return res
