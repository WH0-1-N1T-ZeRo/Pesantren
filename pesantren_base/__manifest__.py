# -*- coding: utf-8 -*-
#    ________  __      ________  _______   ______          _______    _______   ________     __      _____  ___  ___________  _______    _______  _____  ___   
#   /"       )|" \    /"       )/"     "| /    " \        |   __ "\  /"     "| /"       )   /""\    (\"   \|"  \("     _   ")/"      \  /"     "|(\"   \|"  \  
#  (:   \___/ ||  |  (:   \___/(: ______)// ____  \       (. |__) :)(: ______)(:   \___/   /    \   |.\\   \    |)__/  \\__/|:        |(: ______)|.\\   \    | 
#   \___  \   |:  |   \___  \   \/    | /  /    ) :)      |:  ____/  \/    |   \___  \    /' /\  \  |: \.   \\  |   \\_ /   |_____/   ) \/    |  |: \.   \\  | 
#    __/  \\  |.  |    __/  \\  // ___)(: (____/ //       (|  /      // ___)_   __/  \\  //  __'  \ |.  \    \. |   |.  |    //      /  // ___)_ |.  \    \. | 
#   /" \   :) /\  |\  /" \   :)(:  (    \        /       /|__/ \    (:      "| /" \   :)/   /  \\  \|    \    \ |   \:  |   |:  __   \ (:      "||    \    \ | 
#  (_______/ (__\_|_)(_______/  \__/     \"_____/       (_______)    \_______)(_______/(___/    \___)\___|\____\)    \__|   |__|  \___) \_______) \___|\____\) 
#
#

                                                                                                                                                            

{
    'name': "Modul Dasar/Base SISFO Pesantren",

    'summary': """
        Aplikasi SISFO Pesantren
        - Modul Dasar / Base untuk SISFO Pesantren""",

    'description': """
        Aplikasi SISFO Pesantren memiliki fitur-fitur sebagai berikut :
        ===============================================================
        * Modul Base / Dasar
        * Modul Akademik
        * Modul Keuangan
        * Modul Guru
        * Modul Orang Tua
        * Modul Kesantrian

        Developed by : 
        - Imam Masyhuri
        - Supriono

        Maret 2022

        Informasi Lebih lanjut, hubungi :
            PT. Cendana Teknika Utama 
            - Ruko Permata Griyashanta NR 24-25 
              Jl Soekarno Hatta - Malang
    """,

    'author': "PT. Cendana Teknika Utama",
    'website': "https://www.cendana2000.co.id",
    'category': 'Education',
    'version': '18.0.1.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','l10n_id','l10n_id_efaktur','mail','hr','sale','account','muk_web_theme', 'pos_wallet_odoo'],
    #test
    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        # 'data/ks_sekolah_data.xml',

        #data
        'views/menu.xml',
        'data/company_data.xml',
        'data/base_data.xml',
        'data/ir_sequence_data.xml',
        'data/cdn_tingkat_data.xml',
        # report
        'report/cetak_sertifikat_santri.xml',
        'report/cetak_kartu_santri.xml',
        # views
        'views/siswa.xml',
        'views/orangtua.xml',
        'views/ref_pekerjaan.xml',
        'views/ref_pendidikan.xml',
        'views/ref_propinsi.xml',
        'views/ref_kota.xml',
        'views/ref_kecamatan.xml',
        'views/ref_tahunajaran.xml',
        'views/biaya_tahunajaran.xml',
        'views/komponen_biaya.xml',
        'views/master_kelas.xml',
        'views/ruang_kelas.xml',
        'views/jurusan.xml',
        'views/guru.xml',
        'views/guru_karyawan.xml',
        'views/sekolah.xml',
        'views/harga_khusus.xml',
        'views/invoice_view.xml',
        'views/aspek_penilaian.xml',
        'views/ref_jam_pelajaran.xml',
        'views/mata_pelajaran.xml',
        'views/jadwal_pelajaran.xml',
        'views/hr_views_inherit.xml',
        'views/account_menuitem_inherit.xml',
        'views/organisasi.xml',
        'views/ekstrakulikuler.xml',
        'views/mobile_fasilitas.xml',
        # wizard
        'wizard/wizard_invoice.xml',
        'wizard/wizard_siswa.xml',
        
        

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "installable": True,
	"auto_install": False,
	"application": True,  
}
