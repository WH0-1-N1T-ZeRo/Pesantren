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
    'name': "Modul Orang Tua SISFO Pesantren",

    'summary': """
        Aplikasi SISFO Pesantren
        - Modul Musyrif untuk SISFO Pesantren""",

    'description': """
        Aplikasi SISFO Pesantren memiliki fitur-fitur sebagai berikut :
        ===============================================================
        * Modul Base / Dasar
        * Modul Akademik
        * Modul Musyrif
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
    'depends': ['base','pesantren_base','pesantren_kesantrian','pesantren_keuangan', 'mail'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        

         # data
        'views/menu.xml',
        # 'data/ks_orangtua_data.xml',
        # views
        'views/absensi_siswa.xml',
        'views/nilai_siswa.xml',
        'views/invoice.xml',
        'views/payment.xml',
        'views/ajukan_ijin.xml',
        'views/tahfidz_quran.xml',
        'views/tahfidz_hadits.xml',
        'views/tahsin_quran.xml',
        'views/mutabaah_harian.xml',
        'views/pelanggaran.xml',
        'views/kesehatan.xml',
        'views/prestasi_siswa.xml',
        'views/pengumuman.xml',
        'views/siswa.xml',
        'views/orangtua.xml',
        'views/temp.xml',
        # wizard
        
       
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],'assets': {
    'web.assets_backend': [
        'pesantren_orangtua/static/src/js/delayed_notification.js',
    ],
},
    "installable": True,
	"auto_install": False,
	"application": True,  
}
