import json
from odoo import http
from odoo.http import request
from odoo.models import check_method_name
from odoo.api import call_kw
from odoo.exceptions import UserError
API_URL = '/api/v1'

API_ALHAMRA = [ # * API Untuk Alhamra Mobile
    {
        'name':'res.partner',
        'allowed_methods':['search_read','write','calculate_wallet'],
        'read_fields':['id','name','display_name','email','jns_partner','type','street','phone','mobile','avatar_1920','avatar_128','user_id','virtual_account','va_saku','saldo_uang_saku','wallet_balance','wallet_pin'],
        'write_fields':['name','email','street','phone']
    },
    {
        'name': 'cdn.siswa',
        'allowed_methods':['search_read'],
        'read_fields':['id','name','partner_id','nis','nisn','tmp_lahir','tgl_lahir','gol_darah','jns_kelamin','rt_rw','propinsi_id','kota_id','kecamatan_id','kewarganegaraan','agama','panggilan','nik','anak_ke','jml_saudara_kandung','bahasa','hobi','cita_cita','ayah_nama','ayah_tmp_lahir','ayah_tgl_lahir','ayah_warganegara','ayah_telp','ayah_email','ayah_pekerjaan_id','ayah_pendidikan_id','ayah_kantor','ayah_penghasilan','ayah_agama','ibu_nama','ibu_tmp_lahir','ibu_tgl_lahir','ibu_warganegara','ibu_telp','ibu_email','ibu_pekerjaan_id','ibu_pendidikan_id','ibu_kantor','ibu_penghasilan','ibu_agama','wali_nama','wali_tmp_lahir','wali_tgl_lahir','wali_telp','wali_email','wali_agama','wali_hubungan','orangtua_id','tahunajaran_id','ruang_kelas_id','jenjang','tingkat','tgl_daftar','asal_sekolah','alamat_asal_sek','telp_asal_sek','prestasi_sebelum','bakat','jalur_pendaftaran','jurusan_sma','bebasbiaya','harga_komponen']
    },
    {
        'name':'cdn.orangtua',
        'allowed_methods':['search_read'],
        'read_fields':['id','name','nik','hubungan','siswa_ids']
    },
    {
        'name': 'cdn.penilaian_lines',
        'allowed_methods':['search_read'],
        'read_fields':['id','penilaian_id','name','mapel_id','tipe','semester','state','siswa_id','nilai','predikat']
    },
    {
        'name': 'cdn.absensi_siswa',
        'allowed_methods':['search_read'],
        'read_fields':['id','name','tanggal','hari','jampelajaran_id','start_time','end_time','kelas_id','tingkat_id','walikelas_id','tahunajaran_id','semester','guru_id','pertemuan_ke','mapel_id','rpp_id','dokumen','tema','materi','state','absensi_ids'],
    },
    {
        'name': 'cdn.absensi_siswa_lines',
        'allowed_methods':['search_read'],
        'read_fields':['id','absensi_id','mapel_id','tanggal','kelas_id','siswa_id','name','nis','kehadiran']
    },
    {
        'name': 'cdn.tahfidz_quran',
        'allowed_methods':['search_read'],
        'read_fields':['id','name','tanggal','siswa_id','last_tahfidz','halaqoh_id','ustadz_id','sesi_tahfidz_id','surah_id','number','jml_ayat','ayat_awal','ayat_akhir','jml_baris','nilai_id','keterangan','state']
    },
    {
        'name': 'cdn.nilai_tahfidz',
        'allowed_methods':['search_read'],
        'read_fields':['id','name','lulus']
    },
    {
        'name': 'cdn.tahsin_quran',
        'allowed_methods':['search_read'],
        'read_fields':['id','name','tanggal','siswa_id','kelas_id','halaqoh_id','ustadz_id','level_tahsin_id','nilai_tajwid','nilai_makhroj','nilai_mad','keterangan','state']
    },
    {
        'name': 'cdn.perijinan',
        'allowed_methods':['search_read','create'],
        'read_fields':['id','name','tgl_ijin','tgl_kembali','waktu_keluar','waktu_kembali','penjemput','siswa_id','kelas_id','halaqoh_id','catatan','keperluan','lama_ijin','jatuh_tempo','state']
    },
    {
        'name': 'cdn.kesehatan',
        'allowed_methods':['search_read'],
        'read_fields':['id','name','tgl_diperiksa','siswa_id','kelas_id','keluhan','diperiksa_oleh','diagnosa','obat','catatan','lokasi_rawat','keterangan_rawat','tgl_selesai','state']
    },
    {
        'name': 'cdn.uang_saku',
        'allowed_methods':['search_read'],
        'read_fields':['id','name','tgl_transaksi','siswa_id','va_saku','saldo_awal','jns_transaksi','amount_in','amount_out','validasi_id','validasi_time','keterangan','state']
    },
    {
        'name': 'cdn.mutabaah_harian',
        'allowed_methods': ['search_read'],
        'read_fields': ['id','name','tgl','siswa_id','halaqoh_id','mutabaah_lines']
    },
    {
        'name': 'cdn.mutabaah_line',
        'allowed_methods': ['search_read'],
        'read_fields': ['id','mutabaah_harian_id','kategori','tgl','name','is_sudah','kategori','keterangan']
    },
    {
        'name': 'account.move',
        'allowed_methods': ['search_read'],
        'read_fields': [
            'id','name','invoice_date','siswa_id','orangtua_id','komponen_id','periode_id','ruang_kelas_id','amount_total_signed','amount_residual_signed','state','payment_state','ref','journal_id','line_ids'
        ]
    },
    {
        'name': 'account.move.line',
        'allowed_methods': ['search_read'],
        'read_fields': [
            'id','name','move_id','move_name','date','partner_id','debit','credit','tax_tag_ids'
        ]
    },
    {
        'name': 'account.payment',
        'allowed_methods': ['search_read'],
        'read_fields': [
            'id','move_id','date','name','journal_id','partner_id','siswa_id','amount','payment_type','ref','state'
        ]
    },
    {
        'name': 'cdn.pelanggaran',
        'allowed_methods': ['search_read'],
        'read_fields': [
            'id','name','state','tgl_pelanggaran','siswa_id','kelas_id','pelanggaran_id','kategori','poin','deskripsi','tindakan_id','deskripsi_tindakan','diperiksa_oleh','catatan_ka_asrama','tgl_disetujui','user_disetujui'
        ]
    },
    {
        'name': 'pos.wallet.transaction',
        'allowed_methods':['search_read'],
        'read_fields':[
            'id','name','wallet_type','amount_float','create_date'
        ]
    },
    {
        'name': 'cdn.ruang_kelas',
        'allowed_methods': ['search_read'],
        'read_fields':[
            'id','name','siswa_ids','jenjang','tingkat','tahunajaran_id','walikelas_id'
        ]
    }
]

class Api(http.Controller):
    def _call_kw(self, model, method, args, kwargs):
        check_method_name(method)
        return call_kw(request.env[model], method, args, kwargs)

    @http.route(API_URL + '/session/logout', auth='user', type='json', methods=['POST'])
    def logout(self):
        request.session.logout()
        return {'code': 200, 'message': 'Successfully logged out'}

    @http.route(API_URL + '/session/authenticate', auth='none', type='json', methods=['POST'], csrf=False)
    def authenticate(self, **kw):
        data = json.loads(request.httprequest.data.decode('utf-8'))
        params = data.get('params', {})
        db = params.get('db')
        login = params.get('login')
        password = params.get('password')

        if not all([db, login, password]):
            return {'error': {'code': 400, 'message': 'Missing required parameters'}}

        try:
            request.session.authenticate(db, login, password)
            session_info = request.env['ir.http'].session_info()
            orangtua = request.env['cdn.orangtua'].search([('partner_id', '=', session_info['partner_id'])])
            
            result = {
                'uid': session_info['uid'],
                'partner_id': session_info['partner_id'],
                'name': session_info['name'],
                'username': session_info['username'],
                'orangtua_id': False,
                'siswa_id': False,
                'avatar_1920': False,
                'avatar_128': False
            }
            
            if orangtua:
                result.update({
                    'orangtua_id': orangtua.id,
                    'avatar_1920': orangtua.partner_id.avatar_1920,
                    'avatar_128': orangtua.partner_id.avatar_128
                })
            if orangtua.siswa_ids:
                result.update({'siswa_id': orangtua.siswa_ids[0].id})
            
            return result
        
        except Exception as e:
            return {'error': {'code': 401, 'message': str(e)}}

    @http.route(API_URL + '/changepassword', auth='user', type='json', methods=['POST'])
    def api_change_password(self, orangtua_id, old, new):
        Orangtua = request.env['cdn.orangtua'].search([('id', '=', orangtua_id)])
        if Orangtua:
            Orangtua.partner_id.user_id.change_password(old, new)
            return True
        else:
            return {'message': 'Orangtua not found', 'error_code': 404}

    @http.route(API_URL + '/alhamra/orangtua', auth='user', type='json', methods=['POST'])
    def api_multi(self, model, method, args=[], **kwargs):
        api = list(filter(lambda x: x.get('name', False) == model, API_ALHAMRA))
        if len(api) == 0:
            return {'error': {'message': 'You are not allowed to access this model', 'error_code': 403}}
        if method not in api[0].get('allowed_methods', []):
            return {'error': {'message': 'You are not allowed to access this method', 'error_code': 403}}
        if method == 'search_read':
            kwargs.update({'fields': api[0]['read_fields']})
        if method == 'write':
            vals = [args[0]]
            for item in args[1:]:
                val = {}
                for field in api[0]['write_fields']:
                    f = item.get(field, False)
                    if f:
                        val.update({field: f})
                vals.append(val)
            args = vals

        return self._call_kw(model, method, args, kwargs)

    @http.route(API_URL + '/siswa/saku', auth='user', type='json', methods=['POST'])
    def api_saku(self, siswa_id):
        Siswa = request.env['cdn.siswa'].search([('id', '=', siswa_id)])
        if Siswa and Siswa.partner_id:
            return Siswa.partner_id.calculate_saku()
        else:
            return {'message': 'Siswa not found', 'error_code': 404}

    @http.route(API_URL + '/siswa/wallet', auth='user', type='json', methods=['POST'])
    def api_wallet(self, siswa_id):
        Siswa = request.env['cdn.siswa'].search([('id', '=', siswa_id)])
        if Siswa:
            return Siswa.partner_id.calculate_wallet()
        else:
            return {'message': 'Siswa not found', 'error_code': 404}

    @http.route(API_URL + '/keuangan/biaya', auth='user', type='json', methods=['POST'])
    def api_keuangan_spp(self, siswa_id):
        Siswa = request.env['cdn.siswa'].search([('id', '=', siswa_id)])
        if Siswa:
            res = []
            for biaya in Siswa.tahunajaran_id.biaya_ids:
                res.append({
                    'name': biaya.name.name,
                    'nominal': biaya.nominal
                })
            return res
        else:
            return {'message': 'Siswa not found', 'error_code': 404}