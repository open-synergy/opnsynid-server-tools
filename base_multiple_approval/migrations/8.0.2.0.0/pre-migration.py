# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    if not version:
        return
    openupgrade.rename_columns(
        cr, {
            "tier_definition_review": [
                ("reviewer_id", None),
                ("reviewer_group_id", None),
            ],
        }
    )
