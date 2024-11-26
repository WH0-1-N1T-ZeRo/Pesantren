from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Mutabaah(models.Model):
    _name = 'cdn.mutabaah'
    _description = 'Tabel Mutabaah'

    name = fields.Char(string='Nama', required=True)
    kategori_id = fields.Many2one(comodel_name='cdn.mutabaah.kategori', string='Kategori', required=True)
    sesi_id = fields.Many2one(comodel_name='cdn.mutabaah.sesi', string='Sesi Mutabaah')
    skor = fields.Integer(string='Skor/Nilai', default="1", required=True)
    active = fields.Boolean(string='Aktif', default=True)
    
class MutabaahKategori(models.Model):
    _name = 'cdn.mutabaah.kategori'
    _description = 'Cdn Mutabaah Kategori'

    name = fields.Char(string='Kategori Mutabaah', required=True)
    active = fields.Boolean(string='Aktif', default=True)


class MutabaahSesi(models.Model):
    _name = 'cdn.mutabaah.sesi'
    _description = 'Cdn Mutabaah Sesi'

    name = fields.Char(string='Sesi Mutabaah', required=True)
    jam_mulai = fields.Float(string='Jam Mulai', required=True)
    jam_selesai = fields.Float(string='Jam Selesai', required=True)
    active = fields.Boolean(string='Aktif', default=True)
    keterangan = fields.Text(string='Keterangan')

    @api.onchange('jam_mulai', 'jam_selesai')
    def _onchange_jam(self):
        # Validasi jam dan menit dalam batas 24-jam dan menit 59
        if self.jam_mulai or self.jam_selesai:
            # Memformat jam dan menit
            jam_mulai = max(0, min(int(self.jam_mulai), 23))
            menit_mulai = max(0, min(int((self.jam_mulai - jam_mulai) * 60), 59))
            jam_selesai = max(0, min(int(self.jam_selesai), 23))
            menit_selesai = max(0, min(int((self.jam_selesai - jam_selesai) * 60), 59))

            # Periksa jika jam selesai terjadi sebelum jam mulai
            mulai_total = jam_mulai * 60 + menit_mulai
            selesai_total = jam_selesai * 60 + menit_selesai
            if selesai_total < mulai_total:
                return {
                    'warning': {
                        'title': 'Perhatian',
                        'message': 'Jam Selesai tidak boleh lebih awal dari Jam Mulai.'
                    }
                }

            # Menyimpan nilai dalam format float yang benar
            self.jam_mulai = round(jam_mulai + menit_mulai / 60, 2)
            self.jam_selesai = round(jam_selesai + menit_selesai / 60, 2)

    

    


    
    








    

