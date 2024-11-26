# from addons.pesantren_kesantrian.models.mutabaah_harian import Mutabaah_harian
from odoo import api, fields, models
from datetime import date

class Prestasi_siswa(models.Model):
    _name = 'cdn.prestasi_siswa'
    _description = 'prestasi Siswa'
    _order = 'tgl_prestasi desc'

    #get domain
    
    name             = fields.Char(string='No. Referensi', readonly=True)
    tgl_prestasi     = fields.Date(string='Tgl Prestasi', default=lambda self: date.today(), required=True)
    siswa_id         = fields.Many2one(comodel_name='cdn.siswa', string='Nama siswa', required=True)
    tingkat_prestasi = fields.Selection(string='Tingkat Prestasi', selection=[('Internal', 'Internal'), ('Lokal', 'Lokal'), ('Kecamatan', 'Kecamatan'),('Kota', 'Kota'), ('Provinsi', 'Provinsi'), ('Nasional', 'Nasional'), ('Internasional', 'Internasional')], required=True)
    jns_prestasi_id  = fields.Many2one(comodel_name='cdn.jns_prestasi', string='Jenis Prestasi', required=True)
    #juara = fields.Selection(string='Juara', selection=[('1', 'Ke-1'), ('2', 'Ke-2'), ('3', 'Ke-3'), ('harapan 1','Harapan 1'), ('harapan 2', 'Harapan 2'), ('harapan 3', 'Harapan 3')], required=True)
    joara            = fields.Char(string='Juara', required=True)
    keterangan       = fields.Text(string='Keterangan')
    foto             = fields.Binary(string='Foto')
    
    MutabaahHarian   = fields.Many2one(comodel_name='cdn.mutabaah_harian')
    

    
    @api.model
    def create(self, vals):
        vals["name"] = self.env["ir.sequence"].next_by_code("cdn.prestasi_siswa")
        return super(Prestasi_siswa, self).create(vals)

    # @api.onchange('juara')
    # def _onchange_juara(self):
    #     MutabaahHarian = 
    
    

    
    
    
