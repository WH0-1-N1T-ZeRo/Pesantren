from odoo import api, fields, models

class JamPelajaran(models.Model):
    _name           = 'cdn.ref_jam_pelajaran'
    _description    = 'Data Jam Pelajaran'

    name            = fields.Char(string='Nama', required=True)
    start_time      = fields.Float(string='Jam Mulai', required=True)
    end_time        = fields.Float(string='Jam Selesai', required=True)

    #onchange
    @api.onchange('start_time', 'end_time')
    def onchange_start_time(self):
        if self.start_time > self.end_time:
            self.end_time = self.start_time
            return {'warning': {'title': 'Warning', 'message': 'Jam Mulai tidak boleh lebih besar dari Jam Selesai'}}
        else:
            return {}
    
