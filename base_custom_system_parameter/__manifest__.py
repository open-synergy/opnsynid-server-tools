# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
# pylint: disable=locally-disabled, manifest-required-author

{
    "name": "Base Custom System Parameter",
    "version": "14.0.1.0.0",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "category": "Generic Modules/Base",
    "website": "https://simetri-sinergi.id",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/base_custom_system_parameter_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
