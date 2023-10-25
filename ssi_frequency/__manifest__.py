# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Frequency",
    "version": "14.0.1.0.0",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": True,
    "depends": [
        "base",
        "ssi_master_data_mixin",
    ],
    "data": [
        "security/ir.model.access.csv",
        "menu.xml",
        "views/frequency_views.xml",
        "views/frequency_set_views.xml",
    ],
    "demo": [
        "demo/frequency_demo.xml",
    ],
}
