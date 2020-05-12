# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import fields, models


class TierDefinitionReview(models.Model):
    _name = "tier.definition.review"

    definition_id = fields.Many2one(
        comodel_name="tier.definition",
    )
    company_id = fields.Many2one(
        related="definition_id.company_id",
        readonly=True,
    )
    review_type = fields.Selection(
        string="Validated by",
        default="individual",
        selection=[
            ("individual", "Specific user"),
            ("group", "Any user in a specific group.")
        ],
    )
    reviewer_id = fields.Many2one(
        string="Reviewer",
        comodel_name="res.users",
    )
    reviewer_group_id = fields.Many2one(
        string="Reviewer group",
        comodel_name="res.groups",
    )
    active = fields.Boolean(
        default=True,
    )
    sequence = fields.Integer(
        default=1,
    )
