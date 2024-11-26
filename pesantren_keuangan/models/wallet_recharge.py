from datetime import datetime
from odoo import api, fields, models


class WalletRecharge(models.TransientModel):
    _inherit = 'recharge.wallet'

    def _get_partner_id(self):
        context = self._context
        active_id = context.get('active_id')
        model = context.get('active_model')

        partner_id = active_id
        if model == 'cdn.siswa':
            Siswa = self.env['cdn.siswa'].browse(active_id)
            partner_id = Siswa.partner_id.id
        return partner_id

    # defaults
    def _default_amount(self):
        Partner = self.env['res.partner'].browse(self.siswa_id.id)
        dompet = Partner.wallet_balance
        max_wallet = self.env.user.company_id.max_wallet
        return max_wallet - dompet if dompet < max_wallet else 0

    # fields
    recharge_amount = fields.Float('Recharge Amount', required=True, default=0)
    siswa_id = fields.Many2one(comodel_name='res.partner', string='Siswa', readonly=True, default=lambda self: self._get_partner_id())
    wallet_balance = fields.Float(string='Saldo Dompet', related='siswa_id.wallet_balance', readonly=True)
    saldo_uang_saku = fields.Float(string='Saldo Uang Saku', related='siswa_id.saldo_uang_saku', readonly=True)
    recharge_type = fields.Selection(selection=[
        ('manual_based', 'Isi Dompet Manual'),
        ('saku_based', 'Isi Berdasarkan Saldo'),
    ], default='saku_based', string='Recharge Type', help="Nilai pilihan saku_based didasarkan pada selisih nilai maksimum wallet dan saldo wallet saat ini.")

    # override
    def post(self):
        if self.recharge_amount <= 1000:
            raise models.ValidationError('Nilai recharge dompet harus lebih dari 1000 Rupiah.')

        AccountPayment = self.env['account.payment']
        
        # Gunakan siswa_id sebagai partner
        Partner = self.siswa_id

        # Cek saldo uang saku
        if self.saldo_uang_saku < self.recharge_amount and self.recharge_type:
            raise models.ValidationError('Saldo Uang Saku Tidak Cukup!')

        PosWalletTransaction = self.env['pos.wallet.transaction']
        date_now = datetime.strftime(datetime.now(), '%Y-%m-%d')
        timestamp = fields.Datetime.now()

        payment_create = AccountPayment.sudo().create({
            'name': self.env['ir.sequence'].with_context(ir_sequence_date=date_now).next_by_code('account.payment.customer.invoice'),
            'payment_type': "inbound",
            'amount': self.recharge_amount,
            'date': datetime.now().date(),
            'journal_id': self.journal_id.id,
            'payment_method_id': 1,
            'partner_type': 'customer',
            'partner_id': Partner.id,
        })
        payment_create.action_post()  # Confirm Account Payment

        value = {
            'wallet_type': 'kas',
            'reference': 'manual',
            'amount': self.recharge_amount,
            'partner_id': Partner.id,
            'currency_id': Partner.property_product_pricelist.currency_id.id,
        }
        PosWalletTransaction.sudo().create(value)

        Partner.write({'wallet_balance': Partner.calculate_wallet()})

        if self.recharge_type in ['saku_based', 'manual_based']:
            UangSaku = self.env['cdn.uang_saku'].sudo()
            UangSaku.create({
                'tgl_transaksi': timestamp,
                'siswa_id': Partner.id,
                'jns_transaksi': 'keluar',
                'amount_out': self.recharge_amount,
                'validasi_id': self.env.user.id,
                'validasi_time': timestamp,
                'keterangan': 'Wallet Recharge',
                'state': 'confirm',
            })
            Partner.write({
                'saldo_uang_saku': Partner.calculate_saku(),
            })
        return

    # onchange
    @api.onchange('recharge_amount')
    def _onchange_recharge_amount(self):
        if self.recharge_type == 'saku_based' and (self.recharge_amount+self.wallet_balance) > self.env.user.company_id.max_wallet:
            return {
                'warning': {
                    'title': 'Warning',
                    'message': 'Pengisian saldo dompet melebihi batas maksimal dompet, batas maksimal dompet adalah Rp. ' + str(self.env.user.company_id.max_wallet)
                },
                'value': {
                    'recharge_amount': self._default_amount()
                },
            }

    @api.onchange('recharge_type')
    def _onchange_recharge_type(self):
        if self.recharge_type == 'saku_based':
            self.recharge_amount = self._default_amount()
        else:
            self.recharge_amount = 0
