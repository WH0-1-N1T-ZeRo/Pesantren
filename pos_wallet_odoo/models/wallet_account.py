from odoo import models, fields, api

class POSWalletAccount(models.Model):
    _name = 'pos.wallet.account'
    _description = 'POS Wallet Account'

    name = fields.Char(string='Wallet Name', required=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    balance = fields.Float(string='Balance', default=0.0)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.company.currency_id)

    def action_recharge_wallet(self):
        # Isi dengan logic recharge sesuai kebutuhan Anda
        pass

