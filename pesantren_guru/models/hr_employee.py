from odoo import models, fields, api, exceptions


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model
    def create(self, values):
        # Check if a user with the same email already exists
        existing_user = self.env['res.users'].search([('login', '=', values.get('work_email'))])
        if existing_user:
            raise exceptions.ValidationError(f"The email {values.get('work_email')} is already in use.")

        res = super(HrEmployee, self).create(values)

        # Create partner
        partner = self.env['res.partner'].create({
            'name': res.name,
            'email': res.work_email,
        })

        # Create user
        users = self.env['res.users'].create({
            'login': res.work_email,
            'partner_id': partner.id,
            'password': 'employee',
        })

        res.user_id = users.id

        # Add groups
        groups = [
            (4, self.env.ref('pesantren_base.group_sekolah_user').id),
            (4, self.env.ref('pesantren_guru.group_guru_user').id),
        ]

        users.groups_id = groups
        return res