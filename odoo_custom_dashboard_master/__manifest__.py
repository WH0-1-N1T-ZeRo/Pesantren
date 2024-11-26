# -*- coding: utf-8 -*-
{
    'name' : 'Dashboard',
    'version' : '1.0',
    'summary': 'OWL',
    'sequence': -1,
    'description': """OWL Custom Dashboard""",
    'category': 'OWL',
    'depends' : ['base', 'web', 'sale', 'board', 'pesantren_orangtua', 'pesantren_kesantrian', 'pesantren_guruquran'],
    'data': [
        'views/dashboard.xml',
        'views/dashboard_kesantrian.xml',
        'views/dashboard_musyrif.xml',
        'views/dashboard_orangtua.xml',
        'views/dashboard_guruquran.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {
        'web.assets_backend': [
            # Kesantrian
            'odoo_custom_dashboard_master/static/src/kesantrian/**/*.js', 
            'odoo_custom_dashboard_master/static/src/kesantrian/**/*.xml', 
            'odoo_custom_dashboard_master/static/src/kesantrian/**/*.scss', 
    
            # Keuangan
            'odoo_custom_dashboard_master/static/src/keuangan/**/*.js', 
            'odoo_custom_dashboard_master/static/src/keuangan/**/*.xml', 
            'odoo_custom_dashboard_master/static/src/keuangan/**/*.scss', 
            
            # Musyrif
            'odoo_custom_dashboard_master/static/src/musyrif/**/*.js', 
            'odoo_custom_dashboard_master/static/src/musyrif/**/*.xml', 
            'odoo_custom_dashboard_master/static/src/musyrif/**/*.scss',
             
            # Orangtua
            'odoo_custom_dashboard_master/static/src/orangtua/**/*.js', 
            'odoo_custom_dashboard_master/static/src/orangtua/**/*.xml', 
            'odoo_custom_dashboard_master/static/src/orangtua/**/*.scss', 
            
            # Guru Quran
            'odoo_custom_dashboard_master/static/src/guruquran/**/*.js', 
            'odoo_custom_dashboard_master/static/src/guruquran/**/*.xml', 
            'odoo_custom_dashboard_master/static/src/guruquran/**/*.scss', 
            
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css',
            
        ], 
        'web.assets_frontend': [ 
            'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css', 
            
        ],

    },
}
