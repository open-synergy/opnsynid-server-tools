# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Base Duration",
    "version": "14.0.1.1.1",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "category": "Generic Modules/Base",
    "website": "https://simetri-sinergi.id",
    "depends": [
        "base_public_holiday",
        "ssi_master_data_mixin",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/base_duration_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}
