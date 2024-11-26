from odoo import api, fields, models

class SiswaInherit(models.Model):
    _inherit        = 'cdn.siswa'


    def create_data_account(self):
        # Panggil method dari res.partner yang didelegasikan
        self.partner_id.create_data_account()

    def action_view_pos_order(self):
        action = self.env["ir.actions.actions"]._for_xml_id("pesantren_keuangan.pos_order_action_internal")
        action['domain'] = [('partner_id', '=', self.partner_id.id)]
        action['context'] = {'partner_id': self.partner_id.id}
        return action
        
    pos_order_count = fields.Integer(string='POS Orders', compute='_compute_pos_order_count')
    
    @api.depends('partner_id')
    def _compute_pos_order_count(self):
        for siswa in self:
            siswa.pos_order_count = self.env['pos.order'].search_count([('partner_id', '=', siswa.partner_id.id)])
    
    def action_recharge(self):
        """Memanggil action_recharge dari model res.partner"""
        # Mengakses model res.partner
        partner_model = self.env['res.partner']
        # Panggil action_recharge dari res.partner
        return partner_model.action_recharge()