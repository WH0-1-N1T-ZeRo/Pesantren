from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
import time
from odoo.exceptions import UserError

class generate_invoice(models.TransientModel):
    _name           = "generate.invoice"

    def _default_tahunajaran(self):
       return self.env['res.company'].search([('id','=',1)]).tahun_ajaran_aktif


    tahunajaran_id      = fields.Many2one(comodel_name="cdn.ref_tahunajaran",  string="Tahun Ajaran", default=_default_tahunajaran, readonly=True, store=True)
    komponen_id         = fields.Many2one('cdn.komponen_biaya', 'Komponen Biaya', required=True)
    period_from         = fields.Many2one('cdn.periode_tagihan', 'Bulan Awal', required=True, domain="[('tahunajaran_id','=',tahunajaran_id)]")
    period_to           = fields.Many2one('cdn.periode_tagihan', 'Bulan Akhir', required=True, domain="[('tahunajaran_id','=',tahunajaran_id)]")
    angkatan_id         = fields.Many2one('cdn.ref_tahunajaran', 'Siswa Angkatan', required=True)
    partner_ids         = fields.Many2many('cdn.siswa', 'partner_rel', 'siswa_id', 'partner_id', 'Siswa', required=True, domain="[('bebasbiaya', '=', False), ('tahunajaran_id', '=', angkatan_id)]")
    name                = fields.Float('Harga')

    @api.onchange('komponen_id','name')
    def _onchange_komponen_id(self):
        if self.komponen_id:
            harga = self.env['cdn.biaya_tahunajaran'].search([('tahunajaran_id', '=', self.tahunajaran_id.id), ('name', '=', self.komponen_id.id)], limit=1)
            if not harga:
                return {
                    'value': {'partner_ids': False, 'komponen_id': False, 'name': 0},
                    'warning': {'title': 'Perhatian', 'message': 'Harga komponen belum di tentukan pada tahun ajaran'}
                }

            self.update({'name': harga.nominal})
    
    def create_invoice(self):
        if self.period_from.id > self.period_to.id:
            raise UserError(("Bulan Awal lebih besar daripada bulan akhir !"))
        elif not self.partner_ids:
            raise UserError(("Siswa belum di pilih !"))

        obj_period = self.env['cdn.periode_tagihan']
        obj_invoice = self.env['account.move']
        obj_invoice_line = self.env['account.move.line']

        produk = self.komponen_id.product_id

        # comment by Imam Ms
        # journal_id = obj_invoice.default_get(['journal_id'])['journal_id']
        period_ids = obj_period.search([('id', '>=', self.period_from.id), ('id', '<=', self.period_to.id)])

        #Nomor generator Invoice
        gen_invoice = self.env['ir.sequence'].next_by_code('gen.invoice')

        for period in period_ids:
            for x in self.partner_ids:
                disc_amount = 0; disc_persen = 0
                qty=1
                if x.harga_komponen:
                    disc = self.env['cdn.harga_khusus'].search([('siswa_id', '=', x.id), ('name', '=', self.komponen_id.id)])
                    # print(disc)
                    if disc:
                        disc_amount = disc.disc_amount
                        disc_persen = disc.disc_persen

                # comment by Imam Ms
                # sale_journals       = self.env['account.journal'].search([('type','=','sale')])

                # zid = obj_invoice.create({
                #         'name': '/',
                #         'move_type': 'out_invoice',
                #         'invoice_origin': x.name,
                #         # 'account_id': x.partner_id.property_account_receivable_id.id,
                #         'student': True,
                #         'invoice_payment_term_id': False,
                #         # 'cicil': self.komponen_id.cicil,
                #         'komponen_id': self.komponen_id.id,
                #         'tahunajaran_id': self.tahunajaran_id.id,
                #         'orangtua_id': x.orangtua_id.id,
                #         'ruang_kelas_id': x.ruang_kelas_id.id,
                #         'siswa_id' : x.id,
                #         'partner_id': x.partner_id.id,
                #         'partner_shipping_id': x.partner_id.id,
                #         #'journal_id': 1,
                #         'currency_id': self.env.user.company_id.currency_id.id,
                #         'fiscal_position_id': x.partner_id.property_account_position_id.id,
                #         'invoice_date': period.start_date,
                #         'company_id': self.env.user.company_id.id,
                #         'periode_id': period.id,
                #         'user_id': self.env.uid or False
                #     })

                # obj_invoice_line.create({
                #         'name': produk.partner_ref,
                #         'product_id': produk.id or False,
                #         'discount': disc_persen,
                #         'discount_amount': disc_amount,
                #         'move_id': zid.id,
                #         'account_id': produk.property_account_income_id.id or produk.categ_id.property_account_income_categ_id.id,
                #         'price_unit': self.name - disc_amount,
                #         'quantity': qty,
                #         'product_uom_id': produk.uom_id.id,
                # })

                invoice_vals = {
                    'name': '/',
                    'move_type': 'out_invoice',
                    'invoice_origin': x.name,
                    'student': True,
                    'generate_invoice' : gen_invoice,
                    'invoice_payment_term_id': False,
                    'komponen_id': self.komponen_id.id,
                    'tahunajaran_id': self.tahunajaran_id.id,
                    'orangtua_id': x.orangtua_id.id,
                    'ruang_kelas_id': x.ruang_kelas_id.id,
                    'siswa_id' : x.id,
                    'partner_id': x.partner_id.id,
                    'partner_shipping_id': x.partner_id.id,
                    'currency_id': self.env.user.company_id.currency_id.id,
                    'fiscal_position_id': x.partner_id.property_account_position_id.id,
                    'invoice_date': period.start_date,
                    'company_id': self.env.user.company_id.id,
                    'periode_id': period.id,
                    'user_id': self.env.uid or False
                }

                res = obj_invoice.create(invoice_vals)

                invoice_line_vals = {
                    'name': produk.partner_ref,
                    'product_id' : produk.id or False,
                    'discount': disc_persen,
                    'discount_amount': disc_amount,
                    'account_id': produk.property_account_income_id.id or produk.categ_id.property_account_income_categ_id.id,
                    'price_unit': self.name - disc_amount,
                    'quantity': qty,
                    'product_uom_id': produk.uom_id.id,

                }
                res1 = res.write({'invoice_line_ids' : ([(0,0,invoice_line_vals)])})
        
        action = self.env.ref('pesantren_base.action_tagihan_inherit_view').read()[0]
        action['domain'] = [('generate_invoice','=',gen_invoice)]
        return action
        # return True 