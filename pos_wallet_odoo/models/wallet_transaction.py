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
from odoo import api, fields, models


class WalletTransaction(models.Model):
    """Adding wallet transaction fields"""
    _name = 'pos.wallet.transaction'
    _description = "Create Wallet Transaction Details"

    name = fields.Char(string="Nama", help="Urutan transaksi dompet")
    type = fields.Char(string="Type", help="Jenis transaksi dompet")
    customer = fields.Char(string="Pelanggan",
                           help="Pelanggan Transaksi Dompet")
    wallet_type = fields.Selection([
    ('dompet', 'Dompet'),
    ('kas', 'Kas')],
    string='Tipe Dompet', default='dompet')

    pos_order_id = fields.Many2one('pos.order',string="Pesanan",
                            help="Pesanan referensi transaksi dompet")
    amount = fields.Float(string="Jumlah",
                          help="Jumlah transaksi dompet")
    currency = fields.Char(string="Mata uang",
                           help="Mata uang transaksi dompet")
    reference = fields.Char(string='Referensi')
    currency_id = fields.Many2one('res.currency', string='Pembayaran')
    # Definisikan field status
    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], string='Status', default='draft')

    @api.model
    def create(self, vals):
        """Create sequence for wallet transaction"""
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'pos.wallet.transaction')
        return super(WalletTransaction, self).create(vals)

    partner_id = fields.Many2one('res.partner', string='Siswa')
    siswa_id = fields.Many2one('res.partner', string='Siswa', compute='_compute_siswa')

    @api.depends('partner_id')
    def _compute_siswa(self):
        # Implementasi logika compute di sini
        return


    