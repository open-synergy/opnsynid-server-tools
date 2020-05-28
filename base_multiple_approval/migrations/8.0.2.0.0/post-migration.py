# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, SUPERUSER_ID
from openupgradelib import openupgrade


def migrate(cr, version):
    if not version:
        return
    legacy_reviewer_id =\
        openupgrade.get_legacy_name("reviewer_id")
    legacy_reviewer_group_id =\
        openupgrade.get_legacy_name("reviewer_group_id")
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        openupgrade.m2o_to_x2m(
            cr=cr,
            model=env["tier.definition.review"],
            table="tier_definition_review",
            field="reviewer_ids",
            source_field=legacy_reviewer_id,
        )
        openupgrade.m2o_to_x2m(
            cr=cr,
            model=env["tier.definition.review"],
            table="tier_definition_review",
            field="reviewer_group_ids",
            source_field=legacy_reviewer_group_id,
        )
    openupgrade.drop_columns(
        cr=cr,
        column_spec=[
            ("tier_definition_review", legacy_reviewer_id),
            ("tier_definition_review", legacy_reviewer_group_id),
        ],
    )
