from odoo import api, fields, models


class PenilaianEkstrakulikuler(models.Model):
    _name = 'cdn.penilaian_ekstrakulikuler'
    _description = 'Data penilaian ekstrakulikuler'

    penilaianakhir_id   = fields.Many2one('cdn.penilaian_akhir', string='penilaian_akhir')

    name                = fields.Char(string='Nama', required=True)
    is_wajib            = fields.Boolean(string='Ekstra Wajib', required=True)
    nilai               = fields.Float(string='Nilai')
    predikat            = fields.Char(string='Predikat')

    @api.onchange('nilai')
    def _onchange_nilai1(self):
        message = {
            'title' : "Harap diperhatikan!",
            'message' : "Nilai tidak boleh kurang dari 0 atau melebihi 100"
        }
        if not self._validate_nilai(self.nilai):
            return {'warning': message,'value':{'nilai':self._origin.nilai}}
        # nilai predikat
        Predikat = self.env['cdn.predikat'].search([('tipe','=','ekstrakulikuler')])
        val = {'value':{'predikat':''}}
        if Predikat and self.nilai:
            for pred in Predikat.predikat_ids:
                if pred.min_nilai <= self.nilai <= pred.max_nilai:
                    val['value']['predikat'] = pred.name
        return val
    def _validate_nilai(self,nilai):
        if nilai < 0 or nilai > 100:
            return False
        return True