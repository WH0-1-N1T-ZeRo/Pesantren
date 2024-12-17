# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Sruthi Pavithran (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'Pesantren Wallet Management',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'This Module Helps to Manage Customer Wallet in POS.',
    'description': """This Module Helps to Manage Customer Wallet in POS.""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': 'https://www.cybrosys.com',
    'depends': ['base', 'contacts', 'account', 'point_of_sale','web','base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/res_partner_views.xml',
        'views/wallet_transaction_views.xml',
        'views/account_journal_views.xml',
        'views/pos_payment_method_views.xml',
        'wizard/recharge_wallet_views.xml',
        'views/res_users_views.xml',
        'views/beforeload.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
          'pos_wallet_odoo/static/src/overrides/components/control_buttons/control_buttons.js',
          'pos_wallet_odoo/static/src/overrides/components/control_buttons/control_buttons.xml',
          'pos_wallet_odoo/static/src/overrides/components/InheritTabel/InheritTabel.js',
          'pos_wallet_odoo/static/src/overrides/components/InheritTabel/InheritTabel.xml',
          'pos_wallet_odoo/static/src/overrides/components/InheritTabel/InheritLine/InheritLine.xml',
          'pos_wallet_odoo/static/src/overrides/components/InheritTabel/InheritLine/InheritLine.js',
          'pos_wallet_odoo/static/src/overrides/components/InheritButton/InheritButton.xml',
          'pos_wallet_odoo/static/src/overrides/components/InheritButton/InheritButton.js',
          'pos_wallet_odoo/static/src/overrides/components/InheritProduct/InheritProduct.xml',
          'pos_wallet_odoo/static/src/overrides/components/InheritProduct/InheritProduct.js',
          'pos_wallet_odoo/static/src/overrides/components/InheritProduct/InheritPopupArea.xml',
          'pos_wallet_odoo/static/src/overrides/components/menu/menu.js',
          'pos_wallet_odoo/static/src/overrides/components/menu/menu.xml',
          'pos_wallet_odoo/static/src/overrides/components/menu/close.js',
          'pos_wallet_odoo/static/src/overrides/components/menu/close.xml',
        ],'web.assets_backend': [
            'pos_wallet_odoo/static/src/js/PopupOnce.js',
            'pos_wallet_odoo/static/src/xml/custom_number_popup.xml',
            'pos_wallet_odoo/static/src/js/icon.js',
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}