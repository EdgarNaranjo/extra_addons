# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import api, fields, models, tools, SUPERUSER_ID, _

_logger = logging.getLogger(__name__)


class IrTranslation(models.Model):
    _inherit = "ir.translation"
    _description = 'Translation'

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
