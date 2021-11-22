# -*- coding: utf-8 -*-
##############################################################################
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-2016 Smile (<http://www.smile.fr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################

{
    'name': 'Backend Theme Inmerzo',
    'version': '14.0.0.1',
    "summary": "Backend Theme for Inmerzo Customers",
    "description": """
        Backend Theme for Inmerzo Customers: Odoo base modules, backend and frontend themes.
    """,
    "category": 'Sales/Sales',
    'license': 'AGPL-3',
    'author': "Todooweb (www.todooweb.com)",
    'website': "https://todooweb.com",
    'contributors': [
        "Equipo Dev <devtodoo@gmail.com>",
        "Edgar Naranjo <edgarnaranjof@gmail.com>",
    ],
    'support': 'devtodoo@gmail.com',
    'depends': [
        'sh_backmate_theme_adv',
        'digest',
        'auth_signup',
        'portal'
    ],
    'data': [
        'data/data.xml',
        'views/asset_backend_views.xml',
        'views/backend_inmerzo_views.xml',
    ],
    'qweb': [
        'static/src/xml/template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
