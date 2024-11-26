from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

class SiswaController(http.Controller):

    @http.route('/siswa/get_data', type='json', auth='user')
    def get_data(self, domain=None):
        """
        Mengambil data dari model `res.partner` dengan filter domain opsional.
        
        :param domain: List berisi filter domain Odoo untuk memfilter data siswa (opsional).
        :return: List berisi data siswa sesuai filter yang diberikan.
        """
        try:
            # Jika tidak ada domain, gunakan list kosong agar semua data diambil
            domain = domain or []

            # Jika domain diberikan, batasi hasil pencarian menjadi satu data
            limit = 1 if domain else None

            # Cari data sesuai domain yang diberikan dengan limit jika diperlukan
            siswa_records = request.env['res.partner'].sudo().search(domain, limit=limit)

            data = [{
                'partner_id': record.id,
                'name': record.name,
                'nis': record.nis,
                'wallet_balance': record.wallet_balance,
                'pin': record.wallet_pin,
            } for record in siswa_records]

            return data
        except Exception as e:
            return {'error': str(e)}

    @http.route('/siswa/deduct_wallet', type='json', auth='user')
    def deduct_wallet(self, partner_id, amount):
        """
        Mengurangi wallet_balance pada partner yang diberikan dengan amount tertentu.
        
        :param partner_id: ID dari partner (siswa) yang wallet_balance-nya akan dikurangi.
        :param amount: Jumlah yang akan dikurangi dari wallet_balance.
        :return: Status sukses atau error.
        """
        try:
            # Validasi amount harus positif
            if amount <= 0:
                raise ValidationError("Jumlah yang dikurangi harus lebih besar dari nol.")
            
            # Cari partner berdasarkan ID
            partner = request.env['res.partner'].sudo().browse(partner_id)
            
            # Validasi jika partner ditemukan
            if not partner.exists():
                raise ValidationError("Siswa dengan ID tersebut tidak ditemukan.")
            
            # Validasi jika saldo mencukupi
            if partner.wallet_balance < amount:
                raise ValidationError("Saldo tidak mencukupi untuk melakukan pengurangan.")

            # Kurangi saldo
            partner.sudo().write({'wallet_balance': partner.wallet_balance - amount})

            return {'success': True, 'new_balance': partner.wallet_balance}
        except ValidationError as e:
            return {'error': str(e)}
        except Exception as e:
            return {'error': 'Terjadi kesalahan: ' + str(e)}

    @http.route('/siswa/get_data/bar', type='json', auth='user')
    def get_data_bar(self, barcode=None):
        """
        Mengambil data dari model `res.partner` berdasarkan barcode.
        
        :param barcode: String berisi barcode untuk memfilter data siswa (opsional).
        :return: Dictionary berisi data siswa sesuai barcode yang diberikan.
        """
        try:
            # Jika barcode tidak diberikan, kembalikan error
            if not barcode:
                return {'error': 'Barcode tidak diberikan'}

            # Cari data siswa berdasarkan barcode
            siswa_record = request.env['res.partner'].sudo().search([('barcode', '=', barcode)], limit=1)

            # Jika tidak ditemukan, kembalikan pesan error
            if not siswa_record:
                return {'error': 'Data siswa tidak ditemukan'}

            data = {
                'partner_id': siswa_record.id,
                'name': siswa_record.name,
                'nis': siswa_record.nis,
                'wallet_balance': siswa_record.wallet_balance,
                'pin': siswa_record.wallet_pin,
            }

            return data
        except Exception as e:
            # raise ValidationError(f"Error fetching data for barcode {barcode}: {str(e)}")
            return {'error': str(e)}
