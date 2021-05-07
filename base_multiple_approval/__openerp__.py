# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Base Multiple Approval",
    "summary": "Implement a validation process based on tiers.",
    "version": "8.0.2.4.1",
    "category": "Tools",
    "website": "https://simetri-sinergi.id",
    "author": "Eficent, Odoo Community Association (OCA), "
              "PT. Simetri Sinergi Indonesia, OpenSynergy Indonesia",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
        "email_template",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/tier_definition_view.xml",
        "views/tier_review_view.xml",
    ],
}
