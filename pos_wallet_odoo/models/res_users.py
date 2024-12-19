from odoo import models, fields, api

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    overtime_status = fields.Selection([
        ('to_approve', 'To Approve'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
    ], default='to_approve')
