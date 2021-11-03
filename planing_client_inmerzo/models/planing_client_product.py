# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
import datetime

import logging
_logger = logging.getLogger(__name__)


class PlaningClientProduct(models.Model):
    _name = 'planing.client.product'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Planing Client Product'
    _order = 'create_date desc'

    name = fields.Char('Planing Name', index=True, default='/')
    partner_id = fields.Many2one('res.partner', 'Client', index=True, tracking=True)
    type_planing_id = fields.Many2one('type.planing.client', 'Type', index=True, tracking=True, ondelete='restrict')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in', 'In progress'),
        ('done', 'Finished'),
        ('cancel', 'Cancel'),
    ], string='Status', index=True, tracking=True)
    sale_order_count = fields.Integer(compute='_compute_sale_order')
    invoice_count = fields.Integer(compute='_compute_invoices')
    instances_count = fields.Integer(compute='_compute_instances')
    order_ids = fields.One2many('sale.order', 'planing_id', 'Sale Order')
    notes = fields.Text('Description')
    item_ids = fields.One2many('item.type.planing', 'planing_id', 'Item Type')
    module_ids = fields.One2many('item.type.planing', 'client_id', 'Module Type')
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    discount = fields.Float('Discount')
    amount_plan = fields.Float('Amount Plan')
    amount_user = fields.Float('Amount x User', help='Used to calculate amounts related to "Odoo Enterprise"')
    amount_untaxed = fields.Float('Amount Untaxed', compute='_calc_amount_all', tracking=True)
    discount_amount = fields.Float('Discount', compute='_calc_amount_all', tracking=True)
    amount_total = fields.Float('Amount Total', compute='_calc_amount_all', tracking=True)
    count_user = fields.Integer('Qty users', help='Quantity users by Plan')
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', tracking=True)
    instance_ids = fields.One2many('instance.client', 'planing_id', 'Instance client')
    invoice_id = fields.Many2one('account.move', 'Invoice to Cancel', compute='_calculate_invoice_to_cancel', store=False)

    @api.model
    def create(self, vals):
        request = super(PlaningClientProduct, self).create(vals)
        sequence_name = self.env['ir.sequence'].next_by_code('planing.client.product') or "/"
        if request.type_planing_id:
            planing = request.type_planing_id
            if planing:
                request.amount_plan = planing.total_amount
                request.count_user = planing.count_user
                request.amount_user = planing.amount_user
                if planing.item_ids:
                    items = planing.item_ids
                    obj_create_item = self._create_item_type(request, items)
                    if obj_create_item:
                        _logger.info('Item created')
                    item_data = {
                        'modules_id': False,
                        'client_id': request.id,
                        'price': 0,
                    }
                    list_module = [item.modules_id.id for item in items]
                    obj_module_ids = self.env['module.types'].search([('parent_id.id', 'in', list_module)])
                    if obj_module_ids:
                        for module in obj_module_ids:
                            item_data['modules_id'] = module.id
                            item_data['price'] = module.price
                            create_plan = self.env['item.type.planing'].create(item_data)
                            if create_plan:
                                _logger.info('Extra addons created')
                if planing.type_planing == 'standard':
                    request.name = 'PS' + sequence_name
                elif planing.type_planing == 'advance':
                    request.name = 'PA' + sequence_name
                elif planing.type_planing == 'premium':
                    request.name = 'PP' + sequence_name
                else:
                    request.name = 'PB' + sequence_name
            request.state = 'draft'
            request.message_post(body=_("Created Planing: %s by client %s") % (request.name, request.partner_id.name))
        return request

    def _create_item_type(self, request, items):
        ok_process = False
        item_data = {
            'modules_id': False,
            'planing_id': request.id,
            'availability': False,
        }
        for item in items:
            item_data['modules_id'] = item.modules_id.id
            item_data['availability'] = item.availability
            create_plan = self.env['item.type.planing'].create(item_data)
            if create_plan:
                ok_process = True
        if ok_process:
            return True

    @api.depends('module_ids')
    @api.onchange('module_ids')
    def onchange_extra_item(self):
        for record in self:
            if record.module_ids:
                for item in record.module_ids:
                    item.price = item.modules_id.price

    def unlink(self):
        for obj_planing in self:
            if obj_planing.state in ['in', 'done']:
                raise UserError('It´s not possible to delete a plan in "In progress" or "Finished" state.')
        return super(PlaningClientProduct, self).unlink()

    def prepared_in(self):
        for obj_plan in self:
            obj_plan_ids = self.env['planing.client.product'].search([('state', '=', 'in'), ('partner_id', '=', obj_plan.partner_id.id)])
            if obj_plan_ids:
                raise UserError(_("The client %s has an active plan at this time.\n" 
                                  "Resolve conflicts or contact an Administrator:") % obj_plan.partner_id.name)
            else:
                obj_plan.state = 'in'
                self.create_sale_order()

    def create_sale_order(self):
        obj_create = self._create_sale_order()
        if obj_create:
            obj_create.action_confirm()

    def _create_sale_order(self):
        _logger.info('Begin: Creation Sale Order')
        order_obj = self.env['sale.order']
        for record in self:
            if record.order_ids:
                for order in record.order_ids:
                    order.action_cancel()
            order_lines = []
            planing = record.type_planing_id
            if planing and planing.product_id:
                product = planing.product_id
                name_product = product.name
                price_unit = record.amount_total
                taxes = product.taxes_id.ids
                list_name = [module.modules_id.name for module in record.module_ids]
                if list_name:
                    name_product += ' + extra addons ' + str(list_name)
                line_vals = {
                    'price_unit': price_unit,
                    'product_id': product.id,
                    'product_uom': product.uom_id.id,
                    'product_uom_qty': 1,
                    'name': name_product,
                    'tax_id': [(6, 0, taxes)],
                    'currency_id': self.currency_id.id,
                }
                order_lines.append((0, 0, line_vals))
                order_vals = {
                    'partner_id': record.partner_id.id,
                    'date_order': record.create_date,
                    'order_line': order_lines,
                    'pricelist_id': record.partner_id.property_product_pricelist.id,
                    'currency_id': self.currency_id.id,
                    'user_id': self.create_uid.id,
                    'company_id': record.create_uid.company_id.id,
                    'planing_id': record.id,
                    'payment_term_id': record.payment_term_id.id if record.payment_term_id else False,
                    'validity_date': record.create_date,
                    'origin': record.name,
                }
                obj_create = order_obj.create(order_vals)
            else:
                raise UserError(_("Cannot create a Sales Order for the plan %s.\n"
                                  "Resolve conflicts or contact an Administrator:") % record.name)
        return obj_create

    def create_instance(self):
        for record in self:
            ok_process = False
            inst_data = {
                'partner_id': record.partner_id.id,
            }
            create_plan = self.env['instance.client'].create(inst_data)
            if create_plan:
                ok_process = True
            if ok_process:
                return True

    def prepared_done(self):
        for obj_plan in self:
            obj_plan.state = 'done'

    def prepared_cancel(self):
        for obj_plan in self:
            obj_plan.state = 'cancel'

    @api.depends('state')
    def _calculate_invoice_to_cancel(self):
        for planing in self:
            planing.invoice_id = False
            # if planing.state == 'cancel':
            sales = planing.order_ids
            list_line = [sale.order_line for sale in sales if sales and sale.state == 'cancel']
            if list_line:
                list_invoice = [line.invoice_lines.move_id for line in list_line if list_line and line.invoice_lines and line.invoice_lines.move_id.state != 'cancel']
                planing.invoice_id = list_invoice[0].id if list_invoice else False

    def _compute_sale_order(self):
        for obj_planing in self:
            obj_planing.sale_order_count = len(obj_planing.order_ids) if obj_planing.order_ids else 0

    def _compute_invoices(self):
        for obj_planing in self:
            sales = obj_planing.order_ids
            list_line = [sale.order_line for sale in sales if sales]
            list_invoice = [line.invoice_lines.move_id.ids[0] for line in list_line if list_line and line.invoice_lines]
            obj_planing.invoice_count = len(list_invoice) if list_invoice else 0

    def _compute_instances(self):
        for obj_planing in self:
            obj_planing.instances_count = len(obj_planing.instance_ids) if obj_planing.instance_ids else 0

    def action_view_sale(self):
        for obj_planing in self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Sales',
                'res_model': 'sale.order',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'domain': [('id', 'in', obj_planing.order_ids.ids)]
            }

    def action_view_invoice(self):
        for obj_planing in self:
            sales = obj_planing.order_ids
            list_line = [sale.order_line for sale in sales if sales]
            list_invoice = [line.invoice_lines.move_id.ids[0] for line in list_line if list_line and line.invoice_lines]
            return {
                'type': 'ir.actions.act_window',
                'name': 'Invoices',
                'res_model': 'account.move',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'domain': [('id', 'in', list_invoice)]
            }

    def action_view_instance(self):
        for obj_planing in self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Instances',
                'res_model': 'instance.client',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'domain': [('id', 'in', obj_planing.instance_ids.ids)]
            }

    @api.depends('discount', 'item_ids', 'module_ids', 'amount_plan', 'count_user')
    def _calc_amount_all(self):
        for record in self:
            tmp_item = 0
            tmp_module = 0
            val_discount = 0
            val_plan = 0
            if record.amount_plan:
                val_plan = record.amount_plan
            if record.item_ids:
                for item in record.item_ids:
                    tmp_item += item.price
            if record.module_ids:
                for module in record.module_ids:
                    tmp_module += module.price
            record.amount_untaxed = tmp_item + tmp_module + val_plan
            if record.amount_untaxed:
                if record.discount:
                    val_discount = record.amount_untaxed * (record.discount / 100)
            record.discount_amount = val_discount
            record.amount_total = record.amount_untaxed + (record.count_user * record.amount_user) - record.discount_amount

