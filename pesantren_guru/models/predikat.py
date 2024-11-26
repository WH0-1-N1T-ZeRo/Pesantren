from odoo import api, fields, models


class Predikat(models.Model):
    _name           = 'cdn.predikat'
    _description    = 'Data Predikat'

    name            = fields.Char(string='Nama', required=True)
    tipe            = fields.Selection([('akademik','Akademik'),('ekstrakulikuler','Ekstrakulikuler')], string='Tipe', required=True)
    predikat_ids    = fields.One2many(comodel_name='cdn.predikat_lines', inverse_name='predikat_id', string='Predikat Detail')

class PredikatLines(models.Model):
    _name           = 'cdn.predikat_lines'
    _description    = 'Data Predikat Detail'

    predikat_id     = fields.Many2one(comodel_name='cdn.predikat', string='Predikat')
    name            = fields.Char(string='Predikat', required=True)
    min_nilai       = fields.Float(string='Min Nilai', required=True)
    max_nilai       = fields.Float(string='Max Nilai', required=True)

    @api.onchange('min_nilai', 'max_nilai')
    def _onchange_min_nilai_max_nilai(self):
        message = {
            'title' : "Harap diperhatikan!",
            'message' : "Nilai tidak boleh kurang dari 0 atau melebihi 100"
        }
        if not self._validate_nilai(self.min_nilai):
            return {'warning': message,'value':{'min_nilai':self._origin.min_nilai}}
        if not self._validate_nilai(self.max_nilai):
            return {'warning': message,'value':{'max_nilai':self._origin.max_nilai}}
        if self.min_nilai > self.max_nilai:
            message['message'] = "Nilai minimal tidak boleh lebih besar dari nilai maksimal"
            return {'warning': message,'value':{'min_nilai':self._origin.min_nilai,'max_nilai':self._origin.max_nilai}}
    def _validate_nilai(self,nilai):
        if nilai < 0 or nilai > 100:
            return False
        return True
