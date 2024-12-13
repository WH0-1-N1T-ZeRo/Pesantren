# from odoo import models, fields, api
# from datetime import datetime, timedelta

# class ResUsers(models.Model):
#     _inherit = 'res.users'

#     @api.model
#     def show_popup_average_time(self):
#         # Hitung rata-rata waktu yang Anda tentukan
#         # avg_time_minutes = 1
#         # last_login = self.env.user.login_date or datetime.now()
#         # delta = datetime.now() - last_login

#         # Jika sudah 10 menit, tampilkan popup
#         # if delta > timedelta(minutes=avg_time_minutes):
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Popup Setting',
#             'res_model': 'cdn.pengumuman',
#             'view_mode': 'form',
#             'target': 'new',
#         }
