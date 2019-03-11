# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Base Cancel Reason",
    "version": "8.0.1.0.0",
    "category": "Base",
    "website": "https://opensynergy-indonesia.com/",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/base_cancel_reason.xml",
        "views/base_cancel_reason_configurator.xml",
        "wizards/base_cancel_reason_wizard.xml"
    ],
}
