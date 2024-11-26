from odoo import api, fields, models
from odoo.exceptions import UserError

class PerijinanCheckIn(models.TransientModel):
    _name           = 'cdn.perijinan.checkin'
    _description    = 'CheckIn Perijinan Santri'

    tgl_ijin    = fields.Date(string='Tgl Masuk', required=True, default=fields.Date.context_today)
    siswa_id    = fields.Many2one('cdn.siswa', string='Siswa', required=True)
    perijinan_id = fields.Many2one('cdn.perijinan', string='Perijinan', required=True)
    kelas_id    = fields.Many2one('cdn.ruang_kelas', string='Kelas', related='siswa_id.ruang_kelas_id', readonly=True)
    kamar_id    = fields.Many2one('cdn.kamar_santri', string='Kamar', related='siswa_id.kamar_id', readonly=True)
    halaqoh_id  = fields.Many2one('cdn.halaqoh', string='Halaqoh', related='siswa_id.halaqoh_id', readonly=True)
    musyrif_id  = fields.Many2one('hr.employee', string='Musyrif', related='siswa_id.musyrif_id', readonly=True)
    keperluan   = fields.Text(string='Keperluan', related='perijinan_id.keperluan', readonly=True)
    lama_ijin   = fields.Integer(string='Lama Ijin', related='perijinan_id.lama_ijin', readonly=True)
    tgl_kembali = fields.Date(string='Tgl Kembali', related='perijinan_id.tgl_kembali', readonly=True)
    penjemput   = fields.Char(string='Penjemput', related='perijinan_id.penjemput', readonly=True)

    @api.onchange('siswa_id')
    def _onchange_siswa_id(self):
        if self.siswa_id:
            Perijinan = self.env['cdn.perijinan'].search([('siswa_id', '=', self.siswa_id.id), ('state', '=', 'Permission')], limit=1)
            # Jika tidak ada perijinan yang sudah di approve maka akan muncul pesan error
            if not Perijinan:
                raise UserError('Tidak ada perijinan keluar untuk santri ini, Silakan di cek kembali!')
            
            self.perijinan_id = Perijinan.id

    def action_checkin(self):
        self.perijinan_id.write({
            'state'         : 'Return',
            'waktu_kembali' : fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'cdn.perijinan',
            'view_mode': 'form',
            'res_id': self.perijinan_id.id,
            'target': 'current',
        }