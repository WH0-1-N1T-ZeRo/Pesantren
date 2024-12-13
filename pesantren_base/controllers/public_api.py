# from odoo import http
# from odoo.http import request
# from odoo.models import check_method_name
# from odoo.api import call_kw

# API_URL = '/api/v1'

# class Api(http.Controller):
#     @http.route(API_URL+'/fasilitas', auth='public', type='json', method=['POST'])
#     def api_fasilitas(self):
#         return [{'name':fasilitas.name,'icon':fasilitas.icon,'image':fasilitas.image,'description':fasilitas.description}for fasilitas in http.request.env['cdn.mobile.fasilitas'].search([])]
    
    
from odoo import http
from odoo.http import request

class SantriController(http.Controller):
    @http.route('/kartu_santri', type='http', auth='public', methods=['POST'], csrf=False)
    def kartu_santri(self, **kwargs):
        import json

        # Parse JSON data from request
        data = json.loads(request.httprequest.data)
        
        # Ensure data is a list
        santri_list = data if isinstance(data, list) else [data]

        # Generate HTML for each santri
        santri_html = ""
        for idx, santri in enumerate(santri_list):
            if idx % 2 == 0 and idx > 0:
                santri_html += "<div style='clear: both;'></div>"

            santri_html += f"""
            <div style="float: left; width: 50%; padding: 10px; box-sizing: border-box;">
                <div class="card-container">
                    <!-- Kartu Santri Depan -->
                    <div class="card front">
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <img src="credit-card.png" style="width: 3rem; " alt="">
                        </div>
                        <div class="card-header">
                            <div>
                                <h1 class="title" style="font-size: 1.7rem;">Kartu Santri</h1>
                                <h3 class="subtitle" style="font-size: 1.4rem;">Daarul Qu`ran Istiqomah</h3>
                            </div>
                        </div>
                        <div class="barcode">
                            <img src="{santri['barcode']}" alt="Barcode">
                            <p>Jln. Kenanga no 5 perempatan pasar</p>
                        </div>
                        <div class="banner"></div>
                    </div>

                    <!-- Kartu Santri Belakang -->
                    <div class="card back">
                        <div class="card-header">
                            <img src="credit-card.png" class="icon-card" alt="">
                            <div class="right-s">
                                <div class="sprite"></div>
                                <div class="site"></div>
                            </div>
                            <img src="../dqi.png" width="45px" height="45px" alt="img">
                            <div>
                                <span class="title">Kartu Santri</span>
                                <br>
                                <span class="subtitle">Daarul Qu`ran Istiqomah</span>
                            </div>
                        </div>
                        <div style="display: flex; align-items: end; justify-content: space-between;">
                            <div class="card-info">
                                <p class="card-number">{santri['nis']}</p>
                                <p class="info">Nama: {santri['nama']}</p>
                                <p class="info">Telp: {santri['telfon']}</p>
                                <p class="info">Alamat: {santri['alamat']}</p>
                            </div>
                            <div class="qr-code">
                                <img src="{santri['foto']}" alt="QR Code">
                                <p style="font-weight: bold; text-align: center; margin-top: 5px;">
                                    {santri['kamar']}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """

        # Combine into full HTML response
        html_response = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Kartu Santri</title>
            <link rel="stylesheet" href="styles.css">
        </head>
        <body>
            {santri_html}
        </body>
        </html>
        """

        return request.make_response(html_response, headers=[('Content-Type', 'text/html')])

