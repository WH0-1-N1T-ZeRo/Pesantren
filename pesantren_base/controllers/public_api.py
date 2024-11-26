from odoo import http
from odoo.http import request
from odoo.models import check_method_name
from odoo.api import call_kw

API_URL = '/api/v1'

class Api(http.Controller):
    @http.route(API_URL+'/fasilitas', auth='public', type='json', method=['POST'])
    def api_fasilitas(self):
        return [{'name':fasilitas.name,'icon':fasilitas.icon,'image':fasilitas.image,'description':fasilitas.description}for fasilitas in http.request.env['cdn.mobile.fasilitas'].search([])]
    
    
    
