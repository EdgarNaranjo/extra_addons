# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class TypePlaningClient(models.Model):
    _name = 'type.planing.client'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Type Planing Client'

    name = fields.Char('Planing Name', index=True, default='/', tracking=True)
    optional_name = fields.Char('Custom name', index=True)
    type_planing = fields.Selection([
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('advance', 'Advance'),
        ('premium', 'Premium'),
    ], string='Type', index=True)
    state = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ], string='Status', index=True)
    item_ids = fields.One2many('item.type.planing', 'type_ids', 'Item Type')
    count_user = fields.Integer('Qty users', help='Quantity users by Plan', tracking=True)
    amount_user = fields.Float('Amount x User', help='Used to calculate amounts related to "Odoo Enterprise"', tracking=True)
    total_amount = fields.Float('Total Amount', tracking=True)
    product_id = fields.Many2one('product.product', 'Product', index=True, tracking=True)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        res = super(TypePlaningClient, self).create(vals)
        res.state = 'active'
        return res

    @api.constrains('type_planing', 'optional_name')
    def _check_name_planing(self):
        for record in self:
            if record.type_planing:
                if record.type_planing == 'standard':
                    record.name = 'Plan Standard'
                elif record.type_planing == 'advance':
                    record.name = 'Plan Advance'
                elif record.type_planing == 'premium':
                    record.name = 'Plan Premium'
                else:
                    record.name = 'Plan Basic'
            if record.optional_name:
                record.name += '-' + record.optional_name

    def do_active(self):
        for record in self:
            record.state = 'active'

    def do_inactive(self):
        for record in self:
            record.state = 'inactive'


class ItemTypePlaning(models.Model):
    _name = 'item.type.planing'
    _description = 'Item Type Planing'
    _rec_name = 'modules_id'

    sequence = fields.Integer(string='Sequence', default=10)
    modules_id = fields.Many2one('module.types', 'Module', index=True)
    type_ids = fields.Many2one('type.planing.client', 'Type Planing', index=True)
    planing_id = fields.Many2one('planing.client.product', 'Planing Client', index=True)
    client_id = fields.Many2one('planing.client.product', 'Planing Product', index=True)
    availability = fields.Integer('Qty available', help='Quantity available by Plan')
    price = fields.Float('Price')
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)


class ModulesTypes(models.Model):
    _name = 'module.types'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Module Types'

    name = fields.Char('Module Name', index=True, tracking=True)
    model_ids = fields.Many2many('ir.module.module', 'rel_module_model', 'module_id', 'model_id', 'Modules')
    price = fields.Float('Price', tracking=True)
    extra_addons = fields.Boolean('Extra', default=False, help='Extra addons module', tracking=True)
    currency_id = fields.Many2one(related="company_id.currency_id", string="Currency", readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    parent_id = fields.Many2one('module.types', 'Parent', tracking=True)
