from odoo import models, fields, api
from odoo.exceptions import ValidationError


class WizardSearchSiswa(models.TransientModel):
    _name = 'wizard.search.siswa'
    _description = 'Wizard Search Siswa'

    nis = fields.Char(string='NIS', required=True)
    name = fields.Many2one('cdn.siswa', string='Nama', compute='_compute_siswa_data', store=True, readonly=True)
    tmp_lahir = fields.Char(string='Tempat Lahir', readonly=True, compute='_compute_siswa_data', store=True)
    tgl_lahir = fields.Date(string='Tgl Lahir', readonly=True, compute='_compute_siswa_data', store=True)

    @api.depends('nis')
    def _compute_siswa_data(self):
        for record in self:
            if record.nis:
                siswa = self.env['cdn.siswa'].search([('nis', '=', record.nis)], limit=1)
                if siswa:
                    record.name = siswa.id
                    record.tmp_lahir = siswa.tmp_lahir
                    record.tgl_lahir = siswa.tgl_lahir
                else:
                    record.name = False
                    record.tmp_lahir = ''
                    record.tgl_lahir = False
                    raise ValidationError('Siswa dengan NIS tersebut tidak ditemukan.')

    def button_search(self):
        for record in self:
            if record.nis:
                siswa = self.env['cdn.siswa'].search([('nis', '=', record.nis)], limit=1)
                if siswa:
                    record.name = siswa.id
                    record.tmp_lahir = siswa.tmp_lahir
                    record.tgl_lahir = siswa.tgl_lahir
                else:
                    record.name = False
                    record.tmp_lahir = ''
                    record.tgl_lahir = False
                    raise ValidationError('Siswa dengan NIS tersebut tidak ditemukan.')
                
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.search.siswa',
            'view_mode': 'form',
            'view_id': self.env.ref('pesantren_base.view_wizard_search_siswa_form').id,
            'target': 'new',
            'res_id': self.id,
        }
