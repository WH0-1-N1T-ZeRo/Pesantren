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
from odoo import fields, models, api


class AccountJournal(models.Model):
    """Adding fields to account journal"""
    _inherit = "account.journal"

    wallet_journal = fields.Boolean(string="Jurnal Dompet",
                                    help="Jurnal Dompet")
class Donation(models.Model):
    _name = 'cdn.donation'
    _description = 'Tabel Donasi'

    name = fields.Char(string='Judul Sumbangan', required=True)
    description = fields.Html(string='Deskripsi')
    target_amount = fields.Float(
        string='Target Donasi', 
        help='Jumlah target donasi yang ingin dicapai'
    )
    collected_amount = fields.Float(
        string='Donasi Terkumpul', 
        compute='_compute_collected_amount', 
        store=True, 
        help='Jumlah donasi yang sudah terkumpul'
    )
    start_date = fields.Date(
        string='Tgl Mulai', 
        help='Tgl dimulainya penggalangan donasi'
    )
    end_date = fields.Date(
        string='Tgl Berakhir', 
        help='Tgl berakhirnya penggalangan donasi'
    )
    is_active = fields.Boolean(
        string='Masih Aktif', 
        compute='_compute_is_active', 
        store=True, 
        help='Status apakah penggalangan donasi masih aktif'
    )
    qr_image = fields.Binary(
        string='QR Code', 
        help='Upload QR Code yang akan digunakan untuk donasi'
    )
    bank_account = fields.Char(
        string='Rekening Bank', 
        help='Nomor rekening bank untuk menerima donasi jika tidak menggunakan QR Code'
    )

    # Relasi ke donasi yang masuk
    donation_detail_ids = fields.One2many(
        'cdn.donation.detail', 
        'donation_id', 
        string='Detail Donasi', 
        help='Daftar donasi yang masuk untuk penggalangan ini'
    )

    @api.depends('donation_detail_ids.amount', 'donation_detail_ids.state')
    def _compute_collected_amount(self):
        """Menghitung jumlah donasi yang terkumpul hanya untuk status 'terverifikasi'."""
        for record in self:
            # Filter donation_detail_ids yang memiliki state = 'terverifikasi'
            verified_donations = record.donation_detail_ids.filtered(lambda d: d.state == 'terverifikasi')
            record.collected_amount = sum(verified_donations.mapped('amount'))

    @api.depends('start_date', 'end_date')
    def _compute_is_active(self):
        """Menghitung apakah donasi masih aktif berdasarkan tanggal mulai dan berakhir."""
        today = fields.Date.today()
        for record in self:
            record.is_active = bool(record.start_date and record.end_date and record.start_date <= today <= record.end_date)


class DonationDetail(models.Model):
    _name = 'cdn.donation.detail'
    _description = 'Detail Donasi'

    name = fields.Char(string='Nama Donatur', required=True)
    amount = fields.Float(string='Jumlah Donasi', required=True, help="Jumlah donasi yang diberikan")
    date = fields.Date(string='Tgl Donasi', default=fields.Date.today, required=True)
    donation_id = fields.Many2one(
        'cdn.donation', 
        string='Terkait Sumbangan', 
        help='Penggalangan donasi yang terkait dengan detail donasi ini'
    )
    state = fields.Selection(
        string='Status',
        selection=[('draft', 'Draft'), ('terverifikasi', 'Terverifikasi')],
        default='draft'
    )
    bukti_image = fields.Binary(
        string='Bukti Transaksi', 
        help='Upload Bukti donasi anda'
    )
    # Field Related
    qr_image = fields.Binary(
        string='QR Code',
        related='donation_id.qr_image',
        readonly=True,
        store=False,
    )
    bank_account = fields.Char(
        string='Rekening Bank',
        related='donation_id.bank_account',
        readonly=True,
        store=False,
    )
    created_by = fields.Many2one(
        'res.users', 
        string='Dibuat Oleh', 
        default=lambda self: self.env.user, 
        readonly=True,
        help='Pengguna yang membuat detail donasi'
    )

    def action_set_to_terverifikasi(self):
        """Ubah status menjadi 'Terverifikasi'"""
        for record in self:
            record.state = 'terverifikasi'

    def action_set_to_draft(self):
        """Ubah status menjadi 'Draft'"""
        for record in self:
            record.state = 'draft'
