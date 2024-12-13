from odoo import http
from odoo.http import request
import werkzeug
from odoo.addons.web.controllers import home
from odoo.exceptions import UserError

class PosScreen(home.Home):
    """The class PosScreen is used to log in pos session directly"""
   
    @http.route('/web/login', type='http', auth="public", website=True, sitemap=False)
    def web_login(self, redirect=None, **kw):
        """Override to add direct login to POS"""
        # Panggil method login asli dari parent class
        res = super(PosScreen, self).web_login(redirect=redirect, **kw)
       
        # Periksa apakah pengguna memiliki konfigurasi POS
        if request.env.user.pos_conf_id:
            try:
                # Cari sesi POS yang sudah terbuka
                existing_sessions = request.env['pos.session'].sudo().search([
                    ('user_id', '=', request.env.uid),
                    ('state', '=', 'opened'),
                    ('config_id', '=', request.env.user.pos_conf_id.id)
                ])
                
                # Tutup sesi yang sudah terbuka sebelumnya
                if existing_sessions:
                    for session in existing_sessions:
                        try:
                            session.action_pos_session_closing_control()
                        except Exception:
                            session.state = 'closed'
                
                # Buat sesi baru
                new_session = request.env['pos.session'].sudo().create({
                    'user_id': request.env.uid,
                    'config_id': request.env.user.pos_conf_id.id,
                    'state': 'opened'
                })
                
                # Redirect ke halaman POS
                return werkzeug.utils.redirect(f'/pos/ui?config_id={new_session.config_id.id}')
            
            except Exception as e:
                # Tangani kesalahan yang mungkin terjadi
                return request.render('web.login', {
                    'error': str(e)
                })
       
        # Kembalikan respons default jika tidak ada konfigurasi POS
        return res