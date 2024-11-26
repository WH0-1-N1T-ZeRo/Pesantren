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
    'name': "Modul Keuangan SISFO Pesantren",

    'summary': """
        Aplikasi SISFO Pesantren
        - Modul Keuangan untuk SISFO Pesantren""",

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
    'depends': ['base','pesantren_base','base_accounting_kit', 'account', 'point_of_sale','pos_wallet_odoo'],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
       
        'data/ir_sequence.xml',
        # 'data/ks_keuangan_data.xml',

         # data
        'views/menu.xml',
        
        # views
        'views/uang_saku.xml',
        'views/siswa_inherit.xml',
        'views/res_company_inherit.xml',
        'views/wallet_recharge_inherit.xml',
        'views/biaya_skolah.xml',
        'views/account_payment_inherit.xml',
        'views/invoice.xml',
        'views/harga_diskon.xml',
        'views/penetapan_tagihan.xml',
        'views/pos_wallet_transaction.xml',
        'views/res_partner_inherit.xml',
        'views/tagihan_vendor.xml',
        'views/pos_order.xml',
        'views/siswa.xml',
        # wizard
        

    ],
    'assets': {
        'web.assets_qweb': [
            'pesantren_keuangan/static/src/xml/**/*.xml',
            'pesantren_keuangan/static/src/js/**/*.js',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "installable": True,
	"auto_install": False,
	"application": True,  
}
