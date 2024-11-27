from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

class PublicStockController(http.Controller):

    @http.route('/api/product_stock', type='json', auth='user')
    def fetch_product_stock(self, domain=None):
        """
        Mengambil data stok produk dari model `product.product` dengan filter domain opsional.
        
        :param domain: List berisi filter domain Odoo untuk memfilter data produk (opsional).
        :return: List berisi data produk sesuai filter yang diberikan, termasuk stok yang tersedia.
        """
        try:
            # Jika tidak ada domain, gunakan list kosong agar semua data diambil
            domain = domain or []

            # Jika domain diberikan, batasi hasil pencarian menjadi satu data
            limit = 1 if domain else None

            # Cari data sesuai domain yang diberikan dengan limit jika diperlukan
            product_records = request.env['product.product'].sudo().search_read(domain, ['name', 'qty_available'], limit=limit)

            if not product_records:
                raise ValidationError("Product not found or no data available.")

            return product_records
        except ValidationError as e:
            # Tangkap ValidationError untuk pesan error yang lebih terstruktur
            return {'error': str(e)}
        except Exception as e:
            # Tangkap error lain untuk debugging
            return {'error': f"An unexpected error occurred: {str(e)}"}
