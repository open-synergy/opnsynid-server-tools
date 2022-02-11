# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author

{
    "name": "Base Copy User Access",
    "version": "14.0.1.0.0",
    "summary": "Copy access right from another user",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "category": "Generic Modules/Base",
    "website": "https://github.com/OCA/vertical-rental",
    "depends": ["base"],
    "data": [
        "wizards/base_copy_user_access.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
    "license": "AGPL-3",
}
