from odoo import api, fields, models


class AsetPesantren(models.Model):
    _name = 'cdn.aset_pesantren'
    _description = 'Model untuk mencatat daftar fasilitas pesantren'
    # constraints
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Nama Aset Pesantren sudah ada!'),
    ]

    name     = fields.Char(string='Nama Aset', required=True)
    jns_aset = fields.Selection(string='Jenis Aset', selection=[
        ('ruang_kelas', 'Ruang Kelas'),
        ('asrama', 'Asrama'),
        ('kantor', 'Kantor'),
        ('laboratorium', 'Laboratorium'),
        ('lapangan', 'Lapangan'),
        ('lainnya', 'Lainnya')
    ], required=True)
    is_kamar_santri = fields.Boolean(string='Kamar Santri',compute='_compute_is_kamar_santri',store=True)
    child_ids       = fields.One2many(comodel_name='cdn.aset_pesantren', inverse_name='parent_id', string='Child', readonly=True)
    
    #hierarchy
    parent_id       = fields.Many2one(comodel_name='cdn.aset_pesantren', string='Lokasi Induk')

    @api.depends('jns_aset', 'parent_id')
    def _compute_is_kamar_santri(self):
        for record in self:
            # doesn't have children and type asrama
            if record.id not in self.env['cdn.aset_pesantren'].search([]).mapped('parent_id').ids and record.jns_aset == 'asrama':
                record.is_kamar_santri = True
                #update parent 
                record.parent_id.is_kamar_santri = False
            else:
                record.is_kamar_santri = False
