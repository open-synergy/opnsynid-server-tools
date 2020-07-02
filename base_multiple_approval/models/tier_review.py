# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.tools.safe_eval import safe_eval as eval
from openerp.exceptions import Warning as UserError


class TierReview(models.Model):
    _name = "tier.review"

    status = fields.Selection(
        string="Status",
        selection=[
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("rejected", "Rejected"),
            ("approved", "Approved")
        ],
        default="draft",
    )
    model = fields.Char(
        string="Related Document Model",
        index=True,
    )
    res_id = fields.Integer(
        string="Related Document ID",
        index=True,
    )
    definition_review_id = fields.Many2one(
        comodel_name="tier.definition.review",
    )
    review_type = fields.Selection(
        related="definition_review_id.review_type",
        readonly=True,
    )
    reviewer_ids = fields.Many2many(
        string="Reviewers",
        comodel_name="res.users",
        compute="_compute_reviewer_ids",
        store=True,
    )
    sequence = fields.Integer(
        string="Tier"
    )
    date = fields.Datetime(
        string="Date",
        readonly=True,
    )
    user_id = fields.Many2one(
        string="Validated/Rejected By",
        comodel_name="res.users",
        readonly=True,
    )

    @api.multi
    def _get_object(self):
        document_id = self.res_id
        document_model = self.model

        object = self.env[document_model].browse(
            [document_id]
        )[0]
        return object

    @api.multi
    def _get_localdict(self):
        return {
            "rec": self._get_object(),
            "env": self.env,
        }

    @api.multi
    def _evaluate_python_code(self, python_condition):
        localdict = self._get_localdict()
        result = False
        try:
            eval(python_condition,
                 globals_dict=localdict, mode="exec", nocopy=True)
            result = localdict
        except:
            msg_err = "Error when execute python code"
            raise UserError(_(msg_err))

        return result

    @api.multi
    @api.depends(
        "definition_review_id",
    )
    def _compute_reviewer_ids(self):
        for rec in self:
            list_user = []
            if rec.definition_review_id:
                review_type = rec.review_type
                user_ids =\
                    rec.definition_review_id.reviewer_ids
                if user_ids:
                    list_user += user_ids.ids

                group_ids =\
                    rec.definition_review_id.reviewer_group_ids
                if group_ids:
                    for group in group_ids:
                        list_user += group.users.ids

                if review_type == "python":
                    python_code = rec.definition_review_id.python_code
                    result = rec._evaluate_python_code(python_code)
                    if result:
                        if "user" in result:
                            list_user += result["user"]
                        else:
                            msg_err = "No User defines on python code"
                            raise UserError(_(msg_err))
                rec.reviewer_ids = list(set(list_user))
