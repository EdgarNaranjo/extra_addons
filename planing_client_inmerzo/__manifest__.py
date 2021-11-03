# -*- coding: utf-8 -*-
##############################################################################
#
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
#
##############################################################################

{
    "name": "Planing Client Inmerzo",
    "version": "14.1.1.1",
    "summary": "Planing Client Inmerzo",
    "description": """
        Planing Client Inmerzo: Basic, Medium, Premium. Images and Dockers by users.
    """,
    "category": 'Sales/Sales',
    'license': 'AGPL-3',
    'author': "Todooweb (www.todooweb.com)",
    'website': "https://todooweb.com/",
    'contributors': [
        "Equipo Dev <devtodoo@gmail.com>",
        "Edgar Naranjo <edgarnaranjof@gmail.com>",
    ],
    'support': 'devtodoo@gmail.com',
    "depends": [
        'base',
        'sale',
        'account',
        'sales_team',
        # 'hr',
        # 'crm',
        # 'hr_attendance',
        # 'hr_contract',
        # 'hr_expense',
        # 'hr_holidays',
        # 'mrp',
        # 'point_of_sale',
        # 'hr_contract',
        # 'project',
        'sale_management',
        'stock',
    ],
    "data": [
        "security/planing_client_security.xml",
        "security/ir.model.access.csv",
        "views/planing_client_views.xml",
        "views/res_partner_views.xml",
        "views/type_planing_client_views.xml",
        "views/product_product_views.xml",
        # "views/docker_host_view.xml",
        # "views/docker_image_view.xml",
        # "views/docker_registry_view.xml",
        # "wizard/docker_host_stats_view.xml",
        # "wizard/docker_registry_cleaning_view.xml",
        "data/planing_client_data.xml",
        # "data/docker_host.xml",
        # "data/docker_registry.xml",
        # "data/ir_cron.xml",
    ],
    "demo": [
        # "demo/docker_image.xml",
    ],
    "qweb": [],
    "auto_install": False,
    "installable": True,
    "application": True,
    "external_dependencies": {
        'python': ['docker', 'requests'],
    },
}
    
