# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Abstract Class for QR Code",
    "version": "8.0.1.2.0",
    "website": "https://opensynergy-indonesia.com/",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base",
    ],
    "external_dependencies": {
        "python": [
            "qrcode",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/base_qr_content_policy_views.xml",
    ],
}
