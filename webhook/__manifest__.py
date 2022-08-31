# Copyright 2016 Vauxoo - https://www.vauxoo.com/
# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Webhook",
    "version": "11.0.1.0.0",
    "author": "Vauxoo, Odoo Community Association (OCA),"
    "OpenSynergy Indonesia, PT. Simetri Sinergi Indonesia",
    "category": "Server Tools",
    "website": "https://simetri-sinergi.id",
    "license": "AGPL-3",
    "depends": [
        "web",
    ],
    "external_dependencies": {
        "python": [
            "ipaddress",
            "requests",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/webhook_views.xml",
    ],
    "demo": [
        "demo/webhook_demo.xml",
    ],
    "installable": True,
    "auto_install": False,
}
