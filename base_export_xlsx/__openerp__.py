# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Base Export xlsx",
    "version": "8.0.1.0.0",
    "category": "Base",
    "website": "https://simetri-sinergi.id/",
    "author": "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base",
    ],
    "external_dependencies": {
        "python": [
            "openpyxl",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "menu.xml",
        "wizards/base_export_xlsx_wizard.xml",
        "views/base_xlsx_template_view.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
}
