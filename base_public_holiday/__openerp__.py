# Copyright 2015 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Public Holidays",
    "summary": "Manage Public Holidays.",
    "version": "8.0.1.0.0",
    "category": "Base",
    "website": "https://simetri-sinergi.id",
    "author": "Michael Telahun Makonnen <mmakonnen@gmail.com>, "
    "Odoo Community Association (OCA), "
    "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "external_dependencies": {
        "python": ["icalendar"],
    },
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/import_ics.xml",
        "views/base_public_holidays_view.xml",
    ],
    "application": False,
    "installable": True,
}
