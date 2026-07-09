# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author

{
    "name": "Base Copy User Operating Unit",
    "version": "14.0.1.0.0",
    "summary": "Copy Allowed Operating Unit and Default Operating Unit from another user",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "category": "Generic Modules/Base",
    "website": "https://simetri-sinergi.id",
    "depends": [
        "base_copy_user_access",
        "operating_unit",
    ],
    "data": [
        "wizards/base_copy_user_operating_unit.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
    "license": "AGPL-3",
}
