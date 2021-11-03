# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    planing_id = fields.Many2one('planing.client.product', 'Planing Client Product', index=True)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.planing_id and not self.planing_id.instance_ids:
            self.planing_id.create_instance()
        return res


class ProductProduct(models.Model):
    _inherit = 'product.product'

    recurring_ok = fields.Boolean('Can be Recurring', default=False)

    @api.model
    def create(self, vals):
        request = super(ProductProduct, self).create(vals)
        if request.type == 'service':
            obj_tax_ids = self.env['account.tax'].search([('type_tax_use', '=', 'sale'), ('tax_group_id.name', '=', 'IVA 21%'), ('name', 'like', 'Serv')], limit=1)
            if obj_tax_ids:
                request.taxes_id = obj_tax_ids.ids
        return request
