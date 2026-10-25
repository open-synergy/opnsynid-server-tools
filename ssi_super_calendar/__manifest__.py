# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Super Calendar",
    "version": "14.0.1.0.2",
    "website": "https://simetri-sinergi.id",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "base",
        "web_tour",
    ],
    "data": [
        "security/ir_model_access/super_calendar.xml",
        "views/super_calendar.xml",
        "views/assets.xml",
    ],
}
