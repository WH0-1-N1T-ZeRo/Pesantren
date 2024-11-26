from asyncio.log import logger
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import date

class harga_khusus(models.Model):
    _name               = 'cdn.harga_khusus'
    _description        = 'Harga Khusus / Diskon Keringanan Biaya'

    name                = fields.Many2one(comodel_name='cdn.komponen_biaya', string='Komponen Biaya', required=True)
    siswa_id            = fields.Many2one(comodel_name='cdn.siswa', string='Nama Siswa', required=True)
    price               = fields.Float(string='Harga', compute='_compute_price', store=True)
    partner_id          = fields.Many2one(comodel_name='res.partner', string='Partner ID', related='siswa_id.partner_id', store=True)
    disc_amount         = fields.Integer(string='Diskon Rupiah', default=0)
    disc_persen         = fields.Integer(string='Diskon Persen %', default=0)
    keterangan          = fields.Char(string='Keterangan')

    _sql_constraints    = [('komponen_partner_uniq', 'unique(name, partner_id)', 'Data Komponen Biaya untuk Siswa tersebut sudah pernah dibuat !')]

    @api.depends('name', 'expired_date')  # Pastikan expired_date juga menjadi dependensi
    def _compute_price(self):
        for record in self:
            # Mengecek apakah harga berlaku berdasarkan tanggal kadaluarsa
            if record.expired_date and record.expired_date < date.today():
                record.price = 0  # Set harga menjadi 0 jika sudah kadaluarsa
            else:
                TahunAjaran = self.env.user.company_id.tahun_ajaran_aktif
                Biaya = TahunAjaran.biaya_ids.search([('name', '=', record.name.id)], limit=1)  # Pastikan hanya satu record yang dikembalikan
                if Biaya:
                    record.price = Biaya.nominal
                else:
                    record.price = 0

    state = fields.Selection(
        string='Status',
        selection=[('berlaku', 'Berlaku'), ('expired', 'Kadaluarsa')],
        compute='_compute_state',
        store=True,
    )

    expired_date = fields.Date(
        string='Kadaluarsa',
        required=True,
        default=fields.Date.context_today,
    )

    @api.depends('expired_date')
    def _compute_state(self):
        for record in self:
            if record.expired_date and record.expired_date >= date.today():
                record.state = 'berlaku'
            else:
                record.state = 'expired'

# class periode_tagihan(models.Model):
#     _inherit = 'cdn.periode_tagihan'
    
#     def name_get(self):
#         res = []
#         for field in self:
#             # if self.env.context.get('custom_search', False):
#             res.append((field.id,"{} TA: {}".format(field.name,field.tahunajaran_id.name)))
#             # else:
#                 # res.append((field.id, field.name))
#         return res
    

class account_invoice(models.Model):
    _inherit            = 'account.move'

    def _default_tahunajaran(self):
       return self.env['res.company'].search([('id','=',1)]).tahun_ajaran_aktif

    siswa_id            = fields.Many2one(comodel_name='cdn.siswa', string='Siswa')
    invoice_date         = fields.Date(string='Tgl Tagihan', required=True, default=fields.Date.context_today)
    
    #partner_id          = fields.Many2one('res.partner', 'Partner', related='siswa_id.partner_id', readonly=True, store=True)

    # cicil               = fields.Selection((('credit', 'Cicilan'), ('tunai','Tunai')), 'Pembayaran', default='tunai')
    student             = fields.Boolean('Siswa')
    generate_invoice    = fields.Char(string='Buat Tagihan')
    
    
    orangtua_id         = fields.Many2one(comodel_name='cdn.orangtua', string='Orang Tua', related='siswa_id.orangtua_id', readonly=True, store=True)
    tahunajaran_id      = fields.Many2one(comodel_name="cdn.ref_tahunajaran",  string="Tahun Ajaran", default=_default_tahunajaran, readonly=True, store=True)
    komponen_id         = fields.Many2one(comodel_name='cdn.komponen_biaya', string='Komponen Tagihan', readonly=True,  states={'draft': [('readonly', False)]})
    ruang_kelas_id      = fields.Many2one(comodel_name='cdn.ruang_kelas', string='Ruang Kelas', readonly=True, store=True)
    periode_id          = fields.Many2one(comodel_name='cdn.periode_tagihan', string='Periode Tagihan', readonly=True,  states={'draft': [('readonly', False)]}, domain="[('tahunajaran_id','=',tahunajaran_id)]")
    vendor_id           = fields.Many2one(comodel_name='res.partner', string='Nama Vendor')
    vendor              = fields.Boolean('Vendor', default=False)

    @api.onchange('vendor_id')
    def _onchange_vendor_id(self):
        if self.vendor_id:
            self.siswa_id = False
            self.tahunajaran_id = False
            self.ruang_kelas_id = False
            self.periode_id = False
            self.orangtua_id = False
            self.partner_id = self.vendor_id
        

    # @api.onchange('vendor_id')
    # def _onchange_vendor_id(self):
    #     if self.vendor and self.vendor_id:
    #         self.partner_id = self.vendor_id

    @api.onchange('siswa_id')
    def _onchange_siswa_id(self):
        if self.siswa_id:
            self.partner_id = self.siswa_id.partner_id
            self.ruang_kelas_id = self.siswa_id.ruang_kelas_id

    @api.depends('invoice_line_ids')
    def _add_line(self):
        for record in self:
            record.info_line = ', '.join([line.name for line in record.invoice_line_ids])

    info_line = fields.Char(compute='_add_line', string='Invoice Line')

    _sql_constraints = [('invoice_uniq', 'unique(komponen_id, partner_id, periode_id)', 'Invoice sudah pernah dibuat !')]

    @api.onchange('periode_id')
    def _onchange_periode_id(self):
        if self.periode_id.end_date:
            self.invoice_date_due = self.periode_id.end_date

        
class account_move_line_inherit(models.Model):
    _inherit = 'account.move.line'

    discount_amount = fields.Float(string='Discount Nominal')
    
    
    # @api.onchange('komponen_id')
    # def onchange_komponen_id(self):
    #     if self.komponen_id:
    #         product = []; harga = {}
    #         for o in self.siswa_id.tahunajaran_id.biaya_ids:
    #             harga[o.name.product_id.id] = o.nominal

    #         i = self.komponen_id.product_id
    #         price = i.lst_price
    #         if harga.has_key(i.id):
    #             price = harga[i.id]
    #         product.append({
    #                         'name': i.partner_ref,
    #                         'product_id': i.id,
    #                         'uos_id': i.uom_id.id,
    #                         'price_unit': price,
    #                         'quantity': 1,
    #                         'account_id': i.categ_id.property_account_income_categ_id.id
    #         })

    #         self.update({'invoice_line_ids': product, 'cicil': self.komponen_id.cicil})
    
    

    

    

    

    
