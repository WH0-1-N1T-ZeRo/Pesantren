# from odoo import api, fields, models


# class ResUsers(models.Model):
#     _inherit = 'res.users'

#     @api.model
#     def create(self, vals):
#         Users = super().create(vals)
#         if Users.partner_id.jns_partner == 'ortu':
#             Users.groups_id = [
#                 (5,0,0),
#                 (4, self.env.ref('pesantren_kesantrian.group_kesantrian_orang_tua').id),
#             ]
            
#         return Users
