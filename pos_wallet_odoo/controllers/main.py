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
class DonasiController(http.Controller):
    
    @http.route('/cdn_donasi/get_donasi', type='json', auth='user')
    def get_all_donasi(self, domain=None):
        """
        Mengembalikan semua data dari model `cdn.donation` dengan atau tanpa filter domain.

        :param domain: List domain Odoo yang digunakan untuk memfilter data (opsional).
        :return: List berisi data dari model `cdn.donation` dalam format JSON.
        """
        # Jika tidak ada domain yang diberikan, gunakan domain kosong
        domain = domain or []

        # Fetch data dari model 'cdn.donation' menggunakan domain yang diberikan
        donasi_data = request.env['cdn.donation'].sudo().search_read(domain, [])

        return donasi_data