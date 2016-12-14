# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Base Create Menu Access",
    "version": "8.0.2.1.2",
    "summary": "Adds wizard to create menu access",
    "category": "Base",
    "website": "https://opensynergy-indonesia.com",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["base"],
    "data": [
        "views/ir_ui_menu.xml",
        "wizards/base_create_menu_access_view.xml"
    ],
}
