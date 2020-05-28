# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import fields, models, api


class TierDefinitionReview(models.Model):
    _name = "tier.definition.review"
    _description = "List Of Reviewer"

    definition_id = fields.Many2one(
        string="Definition",
        comodel_name="tier.definition",
    )
    company_id = fields.Many2one(
        string="Company",
        related="definition_id.company_id",
        readonly=True,
    )
    review_type = fields.Selection(
        string="Validated by",
        default="individual",
        selection=[
            ("individual", "Specific user"),
            ("group", "Any user in a specific group."),
            ("both", "Both specific user and group."),
            ("python", "Python Expression."),
        ],
        required=True,
    )
    reviewer_ids = fields.Many2many(
        string="Reviewer",
        comodel_name="res.users",
        relation="rel_definition_review_users",
        column1="definition_review_id",
        column2="user_id",
    )
    reviewer_group_ids = fields.Many2many(
        string="Reviewer group",
        comodel_name="res.groups",
        relation="rel_definition_review_groups",
        column1="definition_review_id",
        column2="group_id",
    )
    python_code = fields.Text(
        string="Python Expression",
        help="Python Code for determines User or Group "
             "who can be a reviewer",
        default="# Available Locals:"
                "\n# - env: environment"
                "\n# - rec: current record"
                "\n# Available Return:"
                "\n# - user: List ID of User"
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=1,
    )

    @api.onchange(
        "review_type",
    )
    def onchange_reviewer_id(self):
        self.reviewer_id = False

    @api.onchange(
        "review_type",
    )
    def onchange_reviewer_group_id(self):
        self.reviewer_group_id = False

    @api.onchange(
        "review_type",
    )
    def onchange_python_code(self):
        str_python = """# Available Locals:
# - rec: current record
# - env: environment"
# Available Return:
# - user: List ID of User
"""
        self.python_code = str_python
