#!/usr/bin/python
#-*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ruang_kelas(models.Model):

    _name               = "cdn.ruang_kelas"
    _description        = "Tabel Data Ruang Kelas"

    name                = fields.Many2one(comodel_name="cdn.master_kelas",  string="Rombongan Belajar", required=True, copy=False, help="")
    siswa_ids           = fields.Many2many('cdn.siswa','ruang_kelas_siswa_rel','ruang_kelas_id','siswa_id', string='Daftar Siswa', domain=[('active', '=', True)])
    tahunajaran_id      = fields.Many2one(comodel_name="cdn.ref_tahunajaran",  string="Tahun Pelajaran", required=True, help="Tahun ajaran aktif saat ini" , default=lambda self: self.env.user.company_id.tahun_ajaran_aktif.id)
    walikelas_id        = fields.Many2one(comodel_name="hr.employee",  string="Wali Kelas",  help="", domain="[('jns_pegawai','=','guru')]")
    jenjang             = fields.Selection(selection=[('sd','SD/MI'),('smp','SMP/MTS'),('sma','SMA/MA/SMK')],  string="Jenjang", related='name.jenjang', help="")
    tingkat             = fields.Many2one(comodel_name="cdn.tingkat",  string="Tingkat", related='name.tingkat', help="")
    jurusan_id          = fields.Many2one(comodel_name='cdn.master_jurusan', string='Jurusan / Peminatan', related='name.jurusan_id')
    status              = fields.Selection(string='Status', selection=[('draft', 'Draft'), ('konfirm', 'Terkonfirmasi')], default="draft")
    jml_siswa       = fields.Integer(string='Jumlah Siswa', compute='_compute_jml_siswa', store=True)
    # ruang_kelas_lines   = fields.One2many(comodel_name='cdn.ruang_kelas_lines', inverse_name='ruang_kelas_id', string='')
    
    
    

    keterangan          = fields.Char( string="Keterangan",  help="")

    _sql_constraints = [('ruang_kelas_uniq', 'unique(name, tahunajaran_id)', 'Data Rombongan Belajar dan Tahun Pelajaran harus unik !')]
    
    
    def konfirmasi(self):
        for rec in self:
            rec.status = 'konfirm'
            
            conflicting_students = []
            for siswa in rec.siswa_ids:
                if siswa.ruang_kelas_id and siswa.ruang_kelas_id.id != rec.id and siswa.ruang_kelas_id.tahunajaran_id == rec.tahunajaran_id:
                    conflicting_students.append((siswa.name, siswa.ruang_kelas_id.name.name, siswa.ruang_kelas_id.tahunajaran_id.name))

            #Raise error saat santri yang ditambahkan sudah terdaftar di kelas lain
            if conflicting_students:
                conflict_message = "\n".join(["Siswa atas nama %s Sudah Terdaftar di %s pada Tahun Ajaran %s!\n" % (name, kelas, tahun) for name, kelas, tahun in conflicting_students])
                raise UserError("Silakan dihapus dulu data siswa ybs di tersebut:\n\n%s" % conflict_message)
            
            #buat field ruang_kelas_id jadi rec.id
            for siswa in rec.siswa_ids:
                siswa.ruang_kelas_id = rec.id
                
            siswa_existing = self.env['cdn.siswa'].search([('ruang_kelas_id', '=', rec.id)])
            for siswa in siswa_existing:
                if siswa.id not in rec.siswa_ids.ids:
                    siswa.ruang_kelas_id = False
                    
            message_id = self.env['message.wizard'].create({'message': _("Update Ruang Kelas Siswa - SUKSES !!")})
            return {
                'name': _('Successfull'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'message.wizard',
                # pass the id
                'res_id': message_id.id,
                'target': 'new'
            }
    
    def draft(self):
        for rec in self:
            rec.status = 'draft'
    
    @api.depends('siswa_ids')
    def _compute_jml_siswa(self):
        for record in self:
            record.jml_siswa = len(record.siswa_ids)

class MessageWizard(models.TransientModel):
    _name = 'message.wizard'

    message = fields.Text('Informasi', required=True)

    def action_ok(self):
        """ close wizard"""
        return {'type': 'ir.actions.act_window_close'}
    
    
    
    
    
