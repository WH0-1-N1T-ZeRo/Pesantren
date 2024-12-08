# -*- coding: utf-8 -*-

# ██╗   ██╗██████╗ ██╗ ██████╗     ██████╗ ███████╗███████╗ █████╗ ███╗   ██╗████████╗██████╗ ███████╗███╗   ██╗                                              
# ██║   ██║██╔══██╗██║██╔════╝     ██╔══██╗██╔════╝██╔════╝██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔════╝████╗  ██║                                            
# ██║   ██║██████╔╝██║██║  ███╗    ██████╔╝█████╗  ███████╗███████║██╔██╗ ██║   ██║   ██████╔╝█████╗  ██╔██╗ ██║                                             
# ██║   ██║██╔══██╗██║██║   ██║    ██╔═══╝ ██╔══╝  ╚════██║██╔══██║██║╚██╗██║   ██║   ██╔══██╗██╔══╝  ██║╚██╗██║                                             
# ╚██████╔╝██████╔╝██║╚██████╔╝    ██║     ███████╗███████║██║  ██║██║ ╚████║   ██║   ██║  ██║███████╗██║ ╚████║                                             
#  ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝     ╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝                                             

{
    'name': "Modul Pendaftaran Santri SISFO Pesantren",

    'summary': """
        Aplikasi SISFO Pesantren
        - Modul Pendaftaran untuk SISFO Pesantren""",

    'description': """
        Aplikasi SISFO Pesantren memiliki fitur-fitur sebagai berikut :
        ===============================================================
        * Modul Base / Dasar
        * Modul Akademik
        * Modul Musyrif
        * Modul Guru
        * Modul Orang Tua
        * Modul Kesantrian
        * Modul Pendaftaran

        Developed by : 
        - Fahmi
        - Aby
        - Aliga
        - Akim

        November 2024

        Informasi Lebih lanjut, hubungi :

            PT. Universal Big Data 
            - Ruko Modern Kav A16-A17
              Jl Loncat Indah, Tasikmadu, Kota Malang
    """,

    'author': "PT. Universal Big Data",
    'website': "https://ubig.co.id",
    'category': 'Education',
    'version': '18.0.1.0',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'pesantren_base'],

    # always loaded
    'data': [
        # security
        'security/groups.xml',
        'security/ir.model.access.csv',

        # Data
        'data/ubig_pendaftaran_action.xml',

        # View
        'views/pendaftaran_santri.xml',
        'views/ref_bank.xml',
        'views/ref_biaya.xml',
        'views/pendaftaran_form_template.xml',
        'views/pendaftaran_succses_template.xml',
        'views/pendaftaran_cetak_form_pembayaran_template.xml',
        'views/pendaftaran_seleksi_template.xml',
        'views/komponen_biaya.xml',
        'views/biaya_daftarulang.xml',
        'views/res_config_settings.xml',
        'views/pendaftaran_seleksi.xml',
        'views/cron_job.xml',

        # report
        'report/ubig_pendaftaran_report.xml',

        # wizard
        

        # Menu
        'views/menu.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'assets': {
        'web.assets_backend': [
            'pesantren_pendaftaran/static/src/css/style.css',
        ],
    },
}

