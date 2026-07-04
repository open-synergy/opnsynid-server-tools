# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "User Group Section",
    "version": "14.0.1.0.0",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "base",
        "ssi_master_data_mixin",
    ],
    "data": [
        "security/ir.model.access.csv",
        "menu.xml",
        "views/user_group_section_views.xml",
        "views/ir_module_category_views.xml",
        "views/res_users_views.xml",
    ],
}
