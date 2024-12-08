from odoo import models, fields, api


class Bank(models.Model):
    _name           = 'ubig.bank'
    _description    = 'Bank'

    name            = fields.Char(string="Nama Bank", required=True)
    kode_va_bank    = fields.Char(string="Kode VA Bank", required=True, help="digit kode va bank")
    active          = fields.Boolean(string='Active', default=True)
    petunjuk_pembayaran = fields.Text(string='Petunjuk Pembayaran')
    keterangan      = fields.Text(string="Keterangan")