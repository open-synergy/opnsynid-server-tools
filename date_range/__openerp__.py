# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Date Range",
    "summary": "Manage all kind of date range",
    "version": "8.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://simetri-sinergi.id",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA), "
    "PT. Simetri Sinergi Indonesia",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/date_range_security.xml",
        "views/assets.xml",
        "views/date_range_view.xml",
        "wizard/date_range_generator.xml",
    ],
    "qweb": [
        "static/src/xml/date_range.xml",
    ],
}
