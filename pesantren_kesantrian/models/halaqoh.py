from odoo import api, fields, models
from odoo.exceptions import UserError


class Halaqoh(models.Model):
    _name = 'cdn.halaqoh'
    _description = 'Model untuk Pembagian Kelas Halaqoh'

    name = fields.Char(string='Nama Halaqoh', required=True)
    keterangan = fields.Char(string='Keterangan')
    fiscalyear_id = fields.Many2one('cdn.ref_tahunajaran', string='Tahun Ajaran', required=True, default=lambda self: self.env.user.company_id.tahun_ajaran_aktif.id)
    siswa_ids = fields.Many2many('cdn.siswa', string='Siswa')
    penanggung_jawab_id = fields.Many2one('hr.employee', string='Penanggung jawab', required=True)
    pengganti_ids = fields.Many2many('hr.employee', string='Ustadz Pengganti')
    status          = fields.Selection(string='Status', selection=[('draft', 'Draft'), ('konfirm', 'Terkonfirmasi')], default="draft")
    jml_siswa       = fields.Integer(string='Jumlah Siswa', compute='_compute_jml_siswa', store=True)


    #test
    def unlink(self):
        for siswa in self.siswa_ids:
            siswa.halaqoh_id = False
        return super(Halaqoh, self).unlink()
    
    def konfirmasi(self):
        for rec in self:
            rec.status = 'konfirm'
            
            conflicting_students = []
            for siswa in rec.siswa_ids:
                if siswa.halaqoh_id and siswa.halaqoh_id.id != rec.id and siswa.halaqoh_id.fiscalyear_id == rec.fiscalyear_id:
                    conflicting_students.append((siswa.name, siswa.halaqoh_id.name, siswa.kamar_id.fiscalyear_id.name))

            #Raise error saat santri yang ditambahkan sudah terdaftar di halaqoh lain
            if conflicting_students:
                conflict_message = "\n".join(["Siswa atas nama %s Sudah Terdaftar di halaqoh %s pada Tahun Ajaran %s!\n" % (name, halaqoh, tahun) for name, halaqoh, tahun in conflicting_students])
                raise UserError("Silakan dihapus dulu data siswa ybs di halaqoh tersebut:\n\n%s" % conflict_message)
            
            for siswa in rec.siswa_ids:
                siswa.halaqoh_id = rec.id
                
            siswa_existing = self.env['cdn.siswa'].search([('halaqoh_id', '=', rec.id)])
            for siswa in siswa_existing:
                if siswa.id not in rec.siswa_ids.ids:
                    siswa.halaqoh_id = False
            
    def draft(self):
        for rec in self:
            rec.status = 'draft'
    
    @api.depends('siswa_ids')
    def _compute_jml_siswa(self):
        for record in self:
            record.jml_siswa = len(record.siswa_ids)
            
    _sql_constraints = [
        ("name_check", "unique(name)", "Nama Halaqoh sudah ada!"),
    ]