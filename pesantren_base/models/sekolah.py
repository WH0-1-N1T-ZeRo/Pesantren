from odoo import api, fields, models


class res_company(models.Model):
    _inherit                = 'res.company'

    tahun_ajaran_aktif      = fields.Many2one(comodel_name='cdn.ref_tahunajaran', string='Tahun Ajaran Aktif')
    no_statistik_sekolah    = fields.Char(string='No Statistik Sekolah')
    status_sekolah          = fields.Selection(string='Status Sekolah', selection=[('swasta', 'Swasta'), ('negeri', 'Negeri'),])