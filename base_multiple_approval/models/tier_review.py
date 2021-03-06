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
    definition_id = fields.Many2one(
        comodel_name="tier.definition",
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
    reviewer_partner_ids = fields.Many2many(
        string="Review Partners",
        comodel_name="res.partner",
        compute="_compute_reviewer_partner_ids",
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
    def write(self, vals):
        for rec in self:
            if vals.get("status") == "pending":
                rec._send_email_notification()
        return super(TierReview, self).write(vals)

    @api.multi
    @api.depends(
        "reviewer_ids",
    )
    def _compute_reviewer_partner_ids(self):
        for rec in self:
            rec.reviewer_partner_ids =\
                rec._get_reviewer_partner_ids()

    @api.multi
    def _get_reviewer_partner_ids(self):
        self.ensure_one()
        partner_ids = False
        if self.reviewer_ids:
            partner_ids = (self.reviewer_ids.mapped("partner_id"))
        return partner_ids

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

    @api.multi
    def get_context(self):
        self.ensure_one()
        result = {}
        return result

    @api.multi
    def create_mail(self):
        self.ensure_one()
        ctx = self.get_context()
        mail = False
        obj_template = self.env["email.template"]
        obj_mail = self.env["mail.mail"]

        template = self.definition_id.email_template_id
        if template:
            email_dict = obj_template.with_context(ctx).generate_email(
                template_id=template.id, res_id=self.res_id)
            mail = obj_mail.create(email_dict)
        return mail

    @api.multi
    def _send_email_notification(self):
        self.ensure_one()
        mail = self.create_mail()
        if mail:
            mail.write(
                {"recipient_ids": [(6, 0, self.reviewer_partner_ids.ids)]})
            try:
                mail.send()
            except Exception as error:
                raise UserError(_(
                    "Error when sending notification.\n %s") % error)
