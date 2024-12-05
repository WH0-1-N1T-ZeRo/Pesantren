from odoo import http
from odoo.http import request

class POSUserGroupCheck(http.Controller):
    @http.route('/pos/check_user_group', type='json', auth='user')
    def check_user_group(self, group_xml_id):
        try:
            # Dapatkan pengguna yang sedang login
            user = request.env.user
            # Periksa apakah pengguna memiliki grup yang diminta
            has_group = user.has_group(group_xml_id)
            return {'has_group': has_group}
        except Exception as e:
            return {'error': str(e)}
