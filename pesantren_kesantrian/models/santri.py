from odoo import api, fields, models


class Santri(models.Model):
    _inherit = 'cdn.siswa'
    _sql_constraints = [
        ('nis_unique', 'unique(nis)', 'NIS harus unik!'),
    ]
    partner_id          = fields.Many2one('res.partner', string='Siswa', required=True)
    last_tahfidz        = fields.Many2one('cdn.tahfidz_quran', string='Tahfidz Terakhir', readonly=True )
    kamar_id            = fields.Many2one('cdn.kamar_santri', string='Kamar', readonly=True)
    musyrif_id          = fields.Many2one('hr.employee', related='kamar_id.musyrif_id', string='Musyrif/Pembina', readonly=True)
    musyrif_ganti_ids   = fields.Many2many(comodel_name='hr.employee', related='kamar_id.pengganti_ids', string='Musyrif Pengganti', readonly=True)
    halaqoh_id          = fields.Many2one('cdn.halaqoh', string='Halaqoh', readonly=True)
    penanggung_jawab_id = fields.Many2one(comodel_name='hr.employee', related='halaqoh_id.penanggung_jawab_id', string='Penanggung Jawab', readonly=True)
    pengganti_ids       = fields.Many2many(comodel_name ='hr.employee', related='halaqoh_id.pengganti_ids', string='Ustadz Pengganti', readonly=True)
    
    tahfidz_quran_ids   = fields.One2many('cdn.tahfidz_quran', 'siswa_id', string='Tahfidz Quran', readonly=True)

    #state info smart button
    kesehatan_count     = fields.Integer(string='Kesehatan', compute='_compute_count_kesehatan')
    pelanggaran_count   = fields.Integer(string='Pelanggaran', compute='_compute_count_pelanggaran')
    prestasi_siswa_count = fields.Integer(string='Prestasi', compute='_compute_count_prestasi')
    tahfidz_quran_count = fields.Integer(string='Tahfidz Quran', compute='_compute_count_tahfidz_quran')
    saldo_tagihan_count = fields.Float(string='Saldo Tagihan', compute='_compute_count_saldo_tagihan', widget="integer")
    uang_saku_count = fields.Float(string='Uang Saku', compute='_compute_count_uang_saku', widget="integer")

    
    def _compute_count_kesehatan(self):
        for siswa in self:
            siswa.kesehatan_count = self.env['cdn.kesehatan'].search_count([('siswa_id', '=', siswa.id)])
    def _compute_count_pelanggaran(self):
        for siswa in self:
            siswa.pelanggaran_count = self.env['cdn.pelanggaran'].search_count([('siswa_id', '=', siswa.id)])
    def _compute_count_prestasi(self):
        for siswa in self:
            siswa.prestasi_siswa_count = self.env['cdn.prestasi_siswa'].search_count([('siswa_id', '=', siswa.id)])
    def _compute_count_tahfidz_quran(self):
        for siswa in self:
            siswa.tahfidz_quran_count = self.env['cdn.tahfidz_quran'].search_count([('siswa_id', '=', siswa.id)])

    def _compute_count_saldo_tagihan(self):
        for siswa in self:
            if siswa.partner_id:
                tagihan = self.env['account.move'].search([('partner_id', '=', siswa.partner_id.id)])
                print(tagihan)
                siswa.saldo_tagihan_count = sum(tagihan.mapped('amount_total_signed'))

    def _compute_count_uang_saku(self):
        for siswa in self:
            if siswa.partner_id:
                uang_saku = self.env['cdn.uang_saku'].search([('siswa_id', '=', siswa.partner_id.id), ('state', '=', 'confirm')])
                print(uang_saku)
                siswa.uang_saku_count = sum(uang_saku.mapped('amount_in')) - sum(uang_saku.mapped('amount_out'))

    # actions smart button
    def action_kesehatan(self):
        return {
            'name': 'Kesehatan',
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'cdn.kesehatan',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'default_siswa_id': self.id,
            },
            'domain': [('siswa_id', '=', self.id)]
        }
    def action_pelanggaran(self):
        return {
            'name': 'Pelanggaran',
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'cdn.pelanggaran',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'default_siswa_id': self.id,
            },
            'domain': [('siswa_id', '=', self.id)]
        }
    def action_prestasi_siswa(self):
        return {
            'name': 'Prestasi',
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'cdn.prestasi_siswa',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'default_siswa_id': self.id,
            },
            'domain': [('siswa_id', '=', self.id)]
        }
    def action_tahfidz_quran(self):
        return {
            'name': 'Tahfidz Quran',
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'cdn.tahfidz_quran',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {
                'default_siswa_id': self.id,
            },
            'domain': [('siswa_id', '=', self.id)]
        }

    def action_saldo_tagihan(self):
        return {
            'name': 'Saldo Tagihan',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'default_partner_id': self.partner_id.id, 'default_move_type': 'out_invoice'},
            'domain': [('partner_id', '=', self.partner_id.id),('move_type', '=', 'out_invoice')]
        }

    def action_uang_saku(self):
        return {
            'name': 'Uang Saku',
            'view_mode': 'list,form',
            'res_model': 'cdn.uang_saku',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'context': {'default_siswa_id': self.partner_id.id},
            'domain': [('siswa_id', '=', self.partner_id.id)]
        }
