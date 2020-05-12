# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class TierDefinition(models.Model):
    _name = "tier.definition"
    _order = "sequence"

    @api.model
    def _get_tier_validation_model_names(self):
        res = []
        return res

    name = fields.Char(
        string="Name",
    )
    model_id = fields.Many2one(
        string="Referenced Model",
        comodel_name="ir.model",
    )
    model = fields.Char(
        related="model_id.model",
        index=True,
        store=True,
    )
    python_code = fields.Text(
        string="Tier Definition Expression",
        help="Write Python code that defines when this tier confirmation "
             "will be needed. The result of executing the expresion must be "
             "a boolean.",
        default="""# Available locals:\n#  - rec: current record""",
    )
    sequence = fields.Integer(
        default=1,
    )
    active = fields.Boolean(
        default=True,
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        default=lambda self: self.env["res.company"]._company_default_get(
            "tier.definition"),
    )
    definition_review_ids = fields.One2many(
        string="Reviewer(s)",
        comodel_name="tier.definition.review",
        inverse_name="definition_id",
    )
    validate_sequence = fields.Boolean(
        string="Validate by Sequence",
        help="Validation by reviewer must be done by sequence.",
    )
    special_validation = fields.Boolean(
        string="Special Validation",
        help="This validation can only be selected manually. ",
    )

    @api.onchange(
        "model_id"
    )
    def onchange_model_id(self):
        return {"domain": {
            "model_id": [
                ("model", "in", self._get_tier_validation_model_names())]}}
