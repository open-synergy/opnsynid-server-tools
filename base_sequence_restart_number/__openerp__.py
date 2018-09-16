# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author
{
    "name": "Restart Sequence",
    "version": "8.0.1.0.0",
    "category": "Administration",
    "website": "https://opensynergy-indonesia.com/",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "base_action_rule",
    ],
    "data": [
        "data/ir_actions_server_data.xml",
        "views/ir_sequence_views.xml",
    ],
}
