# Copyright 2019 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Base Print Policy",
    "version": "8.0.1.2.0",
    "category": "Base",
    "website": "https://simetri-sinergi.id",
    "author": "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["base", "report"],
    "data": [
        "security/ir.model.access.csv",
        "views/base_print_policy_view.xml",
        "wizards/base_print_document.xml",
    ],
}
