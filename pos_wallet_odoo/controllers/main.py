# File: pos_wallet_odoo/controllers/main.py
from odoo import http
from odoo.http import request

class SiswaController(http.Controller):
    
    @http.route('/pos_wallet_odoo/siswa', type='json', auth='user')
    def get_all_siswa(self, domain=None):
        """
        Mengembalikan semua data dari model `cdn.siswa` dengan atau tanpa domain filter.
        
        :param domain: List domain Odoo yang digunakan untuk memfilter data (opsional).
        :return: List berisi semua field dari model `cdn.siswa`.
        
        """
        # Jika tidak ada domain yang diberikan, gunakan domain kosong
        domain = domain or []
        
        # Fetch data dari model 'cdn.siswa' menggunakan domain yang diberikan
        siswa_data = request.env['cdn.siswa'].sudo().search_read(domain, [])
        
        return siswa_data
