from odoo import api, fields, models
from odoo.exceptions import UserError


class KamarSantri(models.Model):
    _name           = 'cdn.kamar_santri'
    _description    = 'Model untuk mencatat pembagian kamar'
    _rec_name       = 'kamar_id'

    kamar_id        = fields.Many2one(comodel_name='cdn.aset_pesantren', string='Nama Kamar', domain=[('is_kamar_santri', '=', True)], required=True)
    parent_id       = fields.Many2one(comodel_name='cdn.aset_pesantren', related='kamar_id.parent_id', string='Lokasi', store=True, readonly=True)
    musyrif_id      = fields.Many2one(comodel_name='hr.employee', string='Musyrif/Pembina', required=True)
    siswa_ids       = fields.Many2many(comodel_name='cdn.siswa', string='Siswa')
    keterangan      = fields.Char(string='Keterangan')
    fiscalyear_id   = fields.Many2one('cdn.ref_tahunajaran', string='Tahun Ajaran', required=True, default=lambda self: self.env.user.company_id.tahun_ajaran_aktif.id)
    pengganti_ids   = fields.Many2many('hr.employee', string='Ustadz Pengganti')
    status          = fields.Selection(string='Status', selection=[('draft', 'Draft'), ('konfirm', 'Terkonfirmasi')], default="draft")
    jml_siswa       = fields.Integer(string='Jumlah Siswa', compute='_compute_jml_siswa', store=True)
    
    def unlink(self):
        for siswa in self.siswa_ids:
            siswa.kamar_id = False
        return super(KamarSantri, self).unlink()
    
    def konfirmasi(self):
        for rec in self:
            rec.status = 'konfirm'
            
            conflicting_students = []
            for siswa in rec.siswa_ids:
                if siswa.kamar_id and siswa.kamar_id.id != rec.id and siswa.kamar_id.fiscalyear_id == rec.fiscalyear_id:
                    conflicting_students.append((siswa.name, siswa.kamar_id.kamar_id.name, siswa.kamar_id.fiscalyear_id.name))

            #Raise error saat santri yang ditambahkan sudah terdaftar di kamar lain
            if conflicting_students:
                conflict_message = "\n".join(["Siswa atas nama %s Sudah Terdaftar di Kamar %s tahun ajaran %s!\n" % (name, kamar, tahun) for name, kamar, tahun in conflicting_students])
                raise UserError("Silakan dihapus dulu data siswa ybs di Kamar tersebut:\n\n%s" % conflict_message)
            
            for siswa in rec.siswa_ids:
                siswa.kamar_id = rec.id
                
            siswa_existing = self.env['cdn.siswa'].search([('kamar_id', '=', rec.id)])
            for siswa in siswa_existing:
                if siswa.id not in rec.siswa_ids.ids:
                    siswa.kamar_id = False
            
    def draft(self):
        for rec in self:
            rec.status = 'draft'
    
    @api.depends('siswa_ids')
    def _compute_jml_siswa(self):
        for record in self:
            record.jml_siswa = len(record.siswa_ids)