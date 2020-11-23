# -*- coding: utf-8 -*-
# Copyright 2015 Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2015 Antiun Ingeniería S.L. - Carlos Dauden
# Copyright 2015-2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
{
    "name": "Base Custom Information",
    "summary": "Add custom field in models",
    "category": "Tools",
    "version": "8.0.1.0.0",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/res_groups.xml",
        "views/custom_info_category_view.xml",
        "views/custom_info_option_view.xml",
        "views/custom_info_template_view.xml",
        "views/custom_info_property_view.xml",
        "views/custom_info_value_view.xml",
        "views/menu.xml",
        "views/res_partner_view.xml",
    ],
    "author": "Tecnativa, "
              "Odoo Community Association (OCA), "
              "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "website": "https://simetri-sinergi.id",
    "license": "LGPL-3",
    "application": True,
    "installable": True,
}
