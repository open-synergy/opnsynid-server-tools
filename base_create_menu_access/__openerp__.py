# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Base Create Menu Access",
    "version": "8.0.3.0.0",
    "summary": "Adds wizard to create menu access",
    "category": "Base",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["base"],
    "data": [
        "data/ir_module_category.xml",
        "data/ir_cron.xml",
        "views/ir_ui_menu.xml",
        "wizards/base_create_menu_access_view.xml",
    ],
}
