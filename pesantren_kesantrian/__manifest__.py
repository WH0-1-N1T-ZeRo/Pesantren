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
    'name': "Pesantren Kesantrian",

    'summary': """
        Aplikasi SISFO Pesantren
        - Modul Kesantrian""",

    'description': """  Aplikasi SISFO Pesantren
        - Modul Kesantrian
    """,

    'author': "PT. Cendana Teknika Utama",
    'website': "https://www.cendana2000.co.id",
    'category': 'Education',
    'version': '18.0.1.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','pesantren_base'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        

         #data
        'views/menu.xml',
        'views/menu_satpam.xml',
        'data/ir_sequence_data.xml',
        'data/ir_rule_data.xml',
        'data/hr_job_data.xml',
        # 'data/ks_kesantrian_data.xml',
        'data/cdn_surah_data.xml',
        'data/cdn_ayat_data.xml',
        
        #views  
        'views/quran.xml',
        'views/guru.xml',
        'views/guru_quran.xml',
        'views/sesi_tahfidz.xml',
        'views/tindakan_hukuman.xml',
        'views/data_pelanggaran.xml',
        'views/jns_pelanggaran.xml',
        'views/halaqoh.xml',
        'views/kesehatan.xml',
        'views/mutabaah.xml',
        # 'views/level_tahsin.xml',
        'views/buku_tahsin.xml',
        'views/daftar_hadits.xml',
        'views/aset_pesantren.xml',
        'views/nilai_tahfidz.xml',
        'views/kamar_santri.xml',
        'views/pelanggaran.xml',
        'views/orangtua.xml',
        'views/santri.xml',
        'views/jns_prestasi.xml',
        'views/prestasi_siswa.xml',
        'views/mutabaah_harian.xml',
        'views/musyrif.xml',
        'views/perijinan.xml',
        'views/absen_tahfidz_quran.xml',
        'views/tahfidz_hadits.xml',
        'views/absen_tahsin_quran.xml',
        'views/tahsin_quran.xml',
        'views/tahfidz_quran.xml',
        'views/cdn_ayat.xml',
        'views/mutabaah_kategori.xml',
        'views/mutabaah_sesi.xml',
        'views/satpam_perijinan.xml',
        # 'views/scan_kts.xml',
        'wizards/wizard_checkout.xml',
        'wizards/wizard_checkin.xml',

       

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'pesantren_kesantrian/static/src/js/popup_scan.js',
    #     ],
    # },

    "installable": True,
	"auto_install": False,
	"application": True,  
}
