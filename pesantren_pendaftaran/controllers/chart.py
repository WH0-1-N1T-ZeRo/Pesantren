from odoo import http
from odoo.http import request
import json

class PendaftaranPublicController(http.Controller):
    @http.route('/pendaftaran/scrap', type='http', auth='public', methods=['GET'], csrf=False)
    def get_pendaftaran_data(self, **kwargs):
        try:
            # Query ke model `ubig.pendaftaran` mengambil nomor_pendaftaran dan state
            pendaftaran_records = request.env['ubig.pendaftaran'].sudo().search_read([], ['nomor_pendaftaran', 'state'])
            
            # Mengubah hasil query menjadi JSON untuk dikembalikan
            response_data = {
                'status': 'success',
                'data': pendaftaran_records
            }
        except Exception as e:
            # Handle error jika terjadi masalah
            response_data = {
                'status': 'error',
                'message': str(e)
            }
        
        return request.make_response(
            json.dumps(response_data), 
            headers={'Content-Type': 'application/json'}
        )
