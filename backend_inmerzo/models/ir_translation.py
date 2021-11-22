# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class IrTranslation(models.Model):
    _inherit = "ir.translation"

    def _update_translation_all(self):
        obj_translation = self.env['ir.translation'].search([('state', '=', 'translated')])
        if obj_translation:
            for obj_trans in obj_translation:
                if obj_trans.lang == 'es_ES' and obj_trans.value.count('Charl') > 0:
                    position = obj_trans.value.index('Charl')
                    if len(obj_trans.value) <= 6:
                        obj_trans.value = obj_trans.value[:position] + 'Chat'
                    else:
                        obj_trans.value = obj_trans.value[:position] + 'Chat' + obj_trans.value[position+6:]
                if obj_trans.lang == 'es_ES' and obj_trans.src.startswith('Invoicing'):
                    if obj_trans.value.startswith('Facturación /'):
                        obj_trans.value = 'Contabilidad'
            odoo_filtered = obj_translation.filtered(lambda e: e.value.count('Odoo') > 0 or e.value.count('odoo') > 0)
            for odoo_filter in odoo_filtered:
                if odoo_filter.value.count('Odoo') > 0:
                    position = odoo_filter.value.index('Odoo')
                else:
                    position = odoo_filter.value.index('odoo')
                odoo_filter.value = odoo_filter.value[:position] + 'inmerzo' + odoo_filter.value[position+4:]


class MailTemplate(models.Model):
    _inherit = "mail.template"

    def _update_template_all(self):
        obj_template = self.env['mail.template'].search([])
        if obj_template:
            obj_template_name = obj_template.filtered(lambda e: e.name and (e.name.count('Odoo') > 0 or e.name.count('odoo') > 0))
            if obj_template_name:
                for obj_name in obj_template_name:
                    if obj_name.name.count('Odoo') > 0:
                        position = obj_name.name.index('Odoo')
                    if obj_name.name.count('odoo') > 0:
                        position = obj_name.name.index('odoo')
                    obj_name.name = obj_name.name[:position] + 'inmerzo' + obj_name.name[position + 4:]
            obj_template_subject = obj_template.filtered(lambda e: e.subject and (e.subject.count('Odoo') > 0 or e.subject.count('odoo') > 0))
            if obj_template_subject:
                for obj_subject in obj_template_subject:
                    if obj_subject.subject.count('Odoo') > 0:
                        position = obj_subject.subject.index('Odoo')
                    if obj_subject.subject.count('odoo') > 0:
                        position = obj_subject.subject.index('odoo')
                    obj_subject.subject = obj_subject.subject[:position] + 'inmerzo' + obj_subject.subject[position + 4:]
            obj_template_body = obj_template.filtered(lambda e: e.body_html and (e.body_html.count('Odoo') > 0 or e.body_html.count('odoo') > 0))
            if obj_template_body:
                for obj_body in obj_template_body:
                    list_position = []
                    if obj_body.body_html.count('Odoo') > 0:
                        list_position = find_all_indexes(obj_body.body_html, 'Odoo')
                    if obj_body.body_html.count('odoo') > 0:
                        list_position += find_all_indexes(obj_body.body_html, 'odoo')
                    if list_position:
                        for position in list_position:
                            obj_body.body_html = obj_body.body_html[:position] + 'inmerzo' + obj_body.body_html[position + 4:]
            obj_template_colour = obj_template.filtered(lambda e: e.body_html and (e.body_html.count('#875A7B;') > 0))
            if obj_template_colour:
                for obj_colour in obj_template_colour:
                    list_position = []
                    if obj_colour.body_html.count('#875A7B;') > 0:
                        list_position = find_all_indexes(obj_colour.body_html, '#875A7B;')
                    if list_position:
                        for position in list_position:
                            obj_colour.body_html = obj_colour.body_html[:position] + '#00a99d;' + obj_colour.body_html[position + 8:]


def find_all_indexes(input_str, search_str):
    l1 = []
    length = len(input_str)
    index = 0
    while index < length:
        i = input_str.find(search_str, index)
        if i == -1:
            return l1
        l1.append(i)
        index = i + 1
    return l1
