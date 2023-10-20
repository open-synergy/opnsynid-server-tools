# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Base Public Holiday",
    "version": "14.0.1.1.0",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "category": "Generic Modules/Base",
    "website": "https://simetri-sinergi.id",
    "external_dependencies": {
        "python": ["icalendar"],
    },
    "depends": [
        "resource",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/import_ics.xml",
        "views/base_public_holidays_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}
