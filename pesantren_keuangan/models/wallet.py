from odoo import api, fields, models

class pos_wallet_transaction(models.Model):
    _inherit='pos.wallet.transaction'

    amount_float = fields.Float(string='Amount',compute='_compute_amount_float',store=True)
    
    @api.depends('amount')
    def _compute_amount_float(self):
        for rec in self:
            if rec.amount:
                rec.amount_float = float(rec.amount)

    def wallet_recharge(self, partner_id, wallet, journal):
        super(pos_wallet_transaction,self).wallet_recharge(partner_id,wallet,journal)
        Partner = self.env['res.partner'].browse(partner_id['id'])
        Partner.write({'wallet_balance':Partner.calculate_wallet()})
        return True     

class pos_order(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create_from_ui(self, orders, draft=False):
        res = super(pos_order, self).create_from_ui(orders)
        for x in res:
            pos_order_id = self.browse(x.get('id'))
            pos_order_id.partner_id.write({
                'wallet_balance': pos_order_id.partner_id.calculate_wallet()
            })
        return res

class PosMakePayment(models.TransientModel):
    _inherit = 'pos.make.payment'

    def check(self):
        self.ensure_one()
        res = super(PosMakePayment, self).check()
        order = self.env['pos.order'].browse(self.env.context.get('active_id', False))
        order.partner_id.write({
            'wallet_balance':order.partner_id.calculate_wallet()
        })
        return res
