# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Base Copy User Role",
    "version": "14.0.1.0.1",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "category": "Generic Modules/Base",
    "website": "https://simetri-sinergi.id",
    "depends": ["base_user_role"],
    "data": [
        "wizards/base_copy_user_role.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "license": "AGPL-3",
}
