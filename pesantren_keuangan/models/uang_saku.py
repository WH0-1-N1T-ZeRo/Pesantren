from odoo import api, fields, models


class UangSaku(models.Model):
    _name           = 'cdn.uang_saku'
    _description    = 'Uang Saku Santri'
    _order          = 'tgl_transaksi desc'

    name            = fields.Char(string='Name', readonly=True)
    tgl_transaksi   = fields.Datetime(string='Tgl Transaksi', required=True, default=fields.Datetime.now, widget="date")
    siswa_id        = fields.Many2one(comodel_name='res.partner', string='Siswa Partner', required=True, domain=[('jns_partner', '=', 'siswa')])
    siswa           = fields.Many2one(comodel_name='cdn.siswa',compute='_compute_siswa',string='Siswa',store=True)
    va_saku         = fields.Char(string='No. VA Saku', related='siswa_id.va_saku', readonly=True, store=True)
    saldo_awal      = fields.Float(string='Saldo Awal', readonly=True, store=True, compute='_compute_saldo_awal')

    jns_transaksi   = fields.Selection(string='Jenis Transaksi', selection=[
        ('masuk', 'Uang Masuk'),
        ('keluar', 'Uang Keluar'),
    ], required=True, default='masuk')
    amount_in       = fields.Float(string='Nominal Masuk')
    amount_out      = fields.Float(string='Nominal Keluar')

    validasi_id     = fields.Many2one(comodel_name='res.users', string='Validasi', readonly=True)
    validasi_time   = fields.Datetime(string='Tgl Validasi', readonly=True)
    keterangan      = fields.Text(string='Keterangan', states={'confirm': [('readonly', True)]})

    state           = fields.Selection(string='State', selection=[
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
    ], default='draft', readonly=True)
    
    orangtua_id = fields.Many2one(
        comodel_name='cdn.orangtua',
        string='Orang Tua',
        related='siswa.orangtua_id',
        readonly=True,
        store=True
    )

    # override
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('cdn.uang_saku') or 'New'
        result = super(UangSaku, self).create(vals)
        return result

    # actions
    def action_confirm(self):
        for rec in self:
            rec.state = 'confirm'
            rec.validasi_id = self.env.user.id
            rec.validasi_time = fields.Datetime.now()
            rec.siswa_id.write({
                'saldo_uang_saku': rec.siswa_id.calculate_saku(),
            })
        

    # compute
    @api.depends('siswa_id')
    def _compute_saldo_awal(self):
        for record in self:
            record.saldo_awal = record.siswa_id.calculate_saku(self.validasi_time)
    @api.depends('siswa_id')
    def _compute_siswa(self):
        for record in self:
            Siswa = self.env['cdn.siswa'].search([('partner_id','=',record.siswa_id.id)]) # siswa_id is partner_id
            if Siswa:
                record.siswa = Siswa[0].id
            else:
                record.siswa = False

    