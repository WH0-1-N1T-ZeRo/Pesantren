# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class pesantren_base(models.Model):
#     _name = 'pesantren_base.pesantren_base'
#     _description = 'pesantren_base.pesantren_base'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
