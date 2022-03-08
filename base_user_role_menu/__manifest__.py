# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Manage Menu Access Based on Roles",
    "version": "14.0.1.0.0",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "category": "Generic Modules/Base",
    "website": "https://simetri-sinergi.id",
    "depends": ["base_user_role"],
    "data": [
        "data/ir_actions_server_data.xml",
        "views/ir_ui_menu_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
