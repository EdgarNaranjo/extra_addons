# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
try:
    import docker
except ImportError:
    raise ImportError('This module needs docker. Please install docker on your system. (pip install docker)')
import xmlrpc.client as xmlrpclib
import logging

_logger = logging.getLogger(__name__)


# Datos de acceso API Odoo
# def connect_odoo():
#     print('################################')
#     HOST = '192.160.3.55'
#     PORT = 8069
#     DB = 'test00'
#     USER = 'admin'
#     PASS = '1234'
#
#     URL = 'http://%s:%d' % (HOST, PORT)
#     # Logging in
#     common_proxy = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(URL))
#     common_proxy.version()
#
#     # Returns a user identifier ADMIN
#     _logger.info("[Conectando via API: '%s']" % (URL))
#     print("[Conectando via API: '%s']" % (URL))
#     uid = common_proxy.authenticate(DB, USER, PASS, {})
#     return uid, URL, DB, PASS
#     ########## ########## ########## ##########


client = docker.from_env()
list_container = []
list_container = client.containers.list(all=True)
print(list_container)
# client.containers.run("centos:7", name="Prueba1", tty=True, detach=True, stdin_open=True)


class Partner(models.Model):
    _inherit = "res.partner"

    is_inmerzo = fields.Boolean('Client Inmerzo', help="Check seleccionado activa los planes inmerzo")
    planing_count = fields.Integer(compute='_compute_todo_planing')
    instance_count = fields.Integer(compute='_compute_instance')
    planing_ids = fields.One2many('planing.client.product', 'partner_id', 'Planing Client')
    instance_ids = fields.One2many('instance.client', 'partner_id', 'Instance Client')

    def _compute_todo_planing(self):
        for obj_partner in self:
            obj_partner.planing_count = len(obj_partner.planing_ids) if obj_partner.planing_ids else 0

    def _compute_instance(self):
        for obj_partner in self:
            obj_partner.instance_count = len(obj_partner.instance_ids) if obj_partner.instance_ids else 0

    def action_view_partner_planing(self):
        for obj_partner in self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Planing',
                'res_model': 'planing.client.product',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'domain': [('id', 'in', obj_partner.planing_ids.ids)] 
            }

    def action_view_instance_planing(self):
        for obj_partner in self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Instances',
                'res_model': 'instance.client',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'domain': [('id', 'in', obj_partner.instance_ids.ids)]
            }


class InstanceClient(models.Model):
    _name = 'instance.client'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Instance Client'

    name = fields.Char('Instance Name', index=True, default='/')
    partner_id = fields.Many2one('res.partner', 'Client', index=True, tracking=True, ondelete='restrict')
    planing_id = fields.Many2one('planing.client.product', 'Planing', index=True, tracking=True, ondelete='restrict')
    color = fields.Integer('Color Index', default=0)
    user = fields.Many2one('res.users', 'Technician', index=True, tracking=True, ondelete='restrict')
    docker_id = fields.Many2one('docker.build', 'Docker', index=True, tracking=True, ondelete='restrict')
    state = fields.Selection([
        ('no_assigned', 'Not assigned'),
        ('assigned', 'Assigned'),
    ], string='State', default='no_assigned', tracking=True, help='Status by instance', required=True)
    status = fields.Selection([
        ('no_connect', 'Not running'),
        ('connect', 'Running'),
        ('waiting', 'Paused'),
        ('down', 'Down'),
    ], string='Status server', default='no_connect', tracking=True, help='Status by related docker', required=True)
    size_docker = fields.Char(related='docker_id.size_docker', string='Size Docker', tracking=True)
    url = fields.Char(related='docker_id.url', string='Server', tracking=True)

    @api.model
    def create(self, vals):
        request = super(InstanceClient, self).create(vals)
        list_planing = []
        request.state = 'no_assigned'
        request.status = 'no_connect'
        sequence_name = self.env['ir.sequence'].next_by_code('instance.client') or "/"
        if request.partner_id:
            list_planing = [planing for planing in request.partner_id.planing_ids if request.partner_id.planing_ids and planing.state == 'in']
        if list_planing:
            planing = list_planing[0].type_planing_id
            if planing:
                if planing.type_planing == 'standard':
                    request.name = 'INS-PS' + sequence_name
                elif planing.type_planing == 'advance':
                    request.name = 'INS-PA' + sequence_name
                elif planing.type_planing == 'premium':
                    request.name = 'INS-PP' + sequence_name
                else:
                    request.name = 'INS-PB' + sequence_name
                request.planing_id = list_planing[0].id
        else:
            raise UserError('It´s not possible to create a instance. A client plan in "In progess" status is required.')
        return request

    @api.constrains('status')
    def _check_status_instance(self):
        for record in self:
            if record.status == 'connect':
                record.color = 22
            if record.status == 'waiting':
                record.color = 14
            if record.status == 'down':
                record.color = 9
            else:
                record.color = 28


class DockerBuild(models.Model):
    _name = 'docker.build'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Docker Build'

    name = fields.Char('Name', index=True, default='/')
    size_docker = fields.Char('Size Docker', tracking=True)
    url = fields.Char('Server', tracking=True)
    partner_id = fields.Many2one('res.partner', 'Client', index=True, tracking=True, ondelete='restrict')
    status = fields.Selection([
        ('no_connect', 'Not running'),
        ('connect', 'Running'),
        ('waiting', 'Paused'),
        ('down', 'Down'),
    ], string='Status server', default='no_connect', tracking=True, help='Status by related docker', required=True)

    @api.model
    def create(self, vals):
        request = super(DockerBuild, self).create(vals)
        sequence_name = self.env['ir.sequence'].next_by_code('docker.build') or "/"
        request.name = 'DOCK' + sequence_name
        return request


class DockerPorts(models.Model):
    _name = 'docker.ports'
    _description = 'Docker Ports'

    name = fields.Char('Name Ports', index=True, required=True)
    related_name = fields.Char('Container Ports', tracking=True)
    container_id = fields.Many2one('docker.container', 'Container', index=True, tracking=True, ondelete='restrict')


class DockerVolume(models.Model):
    _name = 'docker.volume'
    _description = 'Docker Volume'

    name = fields.Char('Name Volume', index=True, required=True)
    size_volume = fields.Char('Size Volume', tracking=True)
    container_id = fields.Many2one('docker.container', 'Container', index=True, tracking=True, ondelete='restrict')


class DockerContainer(models.Model):
    _name = 'docker.container'
    _description = 'Docker Container'

    name = fields.Char('Name Container', index=True, default='/')
    volume_ids = fields.One2many('docker.volume', 'container_id', 'Docker Volume')
    ports_ids = fields.One2many('docker.ports', 'container_id', 'Docker Ports')
    image_id = fields.Many2one('docker.image', 'Image', index=True, tracking=True, ondelete='restrict')
    status = fields.Selection([
        ('no_connect', 'Not running'),
        ('connect', 'Running'),
        ('waiting', 'Paused'),
        ('down', 'Down'),
    ], string='Status server', default='no_connect', tracking=True, help='Status by related docker', required=True)
    type_image = fields.Selection([
        ('od', 'Odoo'),
        ('po', 'Postgres'),
    ], string='Type', tracking=True, help='Type image Odoo o Postgres')
    po_db = fields.Char('POSTGRES_DB')
    po_pass = fields.Char('POSTGRES_PASSWORD')
    po_user = fields.Char('POSTGRES_USER')
    pg_data = fields.Char('PGDATA')
    path_route = fields.Char('PATH')
    go_version = fields.Char('GOSU_VERSION')
    lang_id = fields.Char('LANG')
    pg_major = fields.Char('PG_MAJOR')
    pg_version = fields.Char('PG_VERSION')
    o_version = fields.Char('ODOO_VERSION')
    o_rc = fields.Char('ODOO_RC')
    ports = fields.Char('PORTS')

    @api.depends('image_id')
    @api.onchange('image_id')
    def check_type_image(self):
        for record in self:
            if record.image_id:
                if record.image_id.type_image == 'od':
                    record.type_image = 'od'
                if record.image_id.type_image == 'po':
                    record.type_image = 'po'


class DockerImage(models.Model):
    _name = 'docker.image'
    _description = 'Docker Image'

    name = fields.Char('Image', default='/')
    display_name = fields.Char('Name', index=True, required=True)
    size_image = fields.Char('Size', tracking=True)
    tag_image = fields.Many2many('crm.tag', 'rel_tag_image', 'tag_id', 'image_id', 'Tag', tracking=True)
    image_id = fields.Char('Id')
    status = fields.Selection([
        ('not_used', 'Not used'),
        ('used', 'In use'),
    ], string='Status', default='not_used', tracking=True, help='Status by related image')
    type_image = fields.Selection([
        ('od', 'Odoo'),
        ('po', 'Postgres'),
    ], string='Type', tracking=True, help='Type image Odoo o Postgres')
    container_ids = fields.One2many('docker.container', 'image_id', 'Docker Container')
    container_count = fields.Integer(compute='_compute_todo_container')

    @api.model
    def create(self, vals):
        request = super(DockerImage, self).create(vals)
        if request.display_name and request.tag_image:
            request.name = request.display_name + ':' + request.tag_image[0].name
        return request

    def _compute_todo_container(self):
        for obj_partner in self:
            obj_partner.container_count = len(obj_partner.container_ids) if obj_partner.container_ids else 0

    def action_view_container(self):
        for obj_partner in self:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Containers',
                'res_model': 'docker.container',
                'view_mode': 'tree,form',
                'view_type': 'form',
                'domain': [('id', 'in', obj_partner.container_ids.ids)]
            }