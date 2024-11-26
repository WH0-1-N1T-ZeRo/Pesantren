from odoo import api, fields, models

class AspekPenilaian(models.Model):
    _name           = 'cdn.aspek_penilaian'
    _description    = 'Data Aspek Penilaian'

    name            = fields.Char(string='Nama', required=True)
    keterangan      = fields.Text(string='Keterangan')
    parent_id       = fields.Many2one(comodel_name='cdn.aspek_penilaian', string='Aspek')
    is_root         = fields.Boolean(string='Is Root', compute='_compute_is_root', store=True)

    # compute
    @api.depends('parent_id','name')
    def _compute_is_root(self):
        for rec in self:
            if rec.id not in self.search([('parent_id','!=',False)]).ids:
                rec.is_root = True
            else:
                rec.is_root = False
