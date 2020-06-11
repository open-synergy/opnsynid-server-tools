# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError, ValidationError
from openerp.tools.safe_eval import safe_eval


class TierValidation(models.AbstractModel):
    _name = "tier.validation"

    _state_field = "state"
    _state_from = ["draft"]
    _state_to = ["confirmed"]
    _cancel_state = "cancel"

    # TODO: step by step validation?

    review_ids = fields.One2many(
        string="Validations",
        comodel_name="tier.review",
        inverse_name="res_id",
        domain=lambda self: [("model", "=", self._name)],
        auto_join=True,
    )
    validated = fields.Boolean(
        string="Validated",
        compute="_compute_validated_rejected",
        search="_search_validated",
    )
    need_validation = fields.Boolean(
        string="Need Validation",
        compute="_compute_need_validation",
    )
    rejected = fields.Boolean(
        string="Rejected",
        compute="_compute_validated_rejected",
    )
    definition_id = fields.Many2one(
        string="Definition",
        comodel_name="tier.definition",
    )
    reviewer_ids = fields.Many2many(
        string="Reviewers",
        comodel_name="res.users",
        compute="_compute_reviewer_ids",
        search="_search_reviewer_ids",
    )
    reviewer_partner_ids = fields.Many2many(
        string="Review Partners",
        comodel_name="res.partner",
        compute="_compute_reviewer_partner_ids",
    )

    @api.multi
    @api.depends(
        "review_ids"
    )
    def _compute_reviewer_ids(self):
        for rec in self:
            rec.reviewer_ids = rec.review_ids.filtered(
                lambda r: r.status == "pending").mapped("reviewer_ids")

    @api.multi
    @api.depends(
        "reviewer_ids",
        "definition_id",
        "definition_id.validate_sequence",
    )
    def _compute_reviewer_partner_ids(self):
        for rec in self:
            if rec.definition_id.validate_sequence:
                rec.reviewer_partner_ids =\
                    rec._get_reviewer_partner_ids_by_sequence()
            else:
                rec.reviewer_partner_ids =\
                    rec._get_reviewer_partner_ids()

    @api.multi
    def _get_reviewer_partner_ids(self):
        self.ensure_one()
        partner = False
        if self.review_ids:
            filter_review_ids =\
                self.review_ids.filtered(lambda r: r.status in ("pending"))
            partner =\
                filter_review_ids.mapped("reviewer_ids").mapped("partner_id")
        return partner

    @api.multi
    def _get_reviewer_partner_ids_by_sequence(self):
        self.ensure_one()
        partner = False
        if self.review_ids:
            filter_review_ids =\
                self.review_ids.filtered(lambda r: r.status in ("pending"))
            sorted_review_ids =\
                filter_review_ids.sorted(key=lambda s: s.sequence)[0]
            partner =\
                sorted_review_ids.mapped("reviewer_ids").mapped("partner_id")
        return partner

    @api.model
    def _search_validated(self, operator, value):
        assert operator in ("=", "!="), "Invalid domain operator"
        assert value in (True, False), "Invalid domain value"
        pos = self.search([
            (self._state_field, "in", self._state_from)]).filtered(
            lambda r: r.review_ids and r.validated == value)
        return [("id", "in", pos.ids)]

    @api.model
    def _search_reviewer_ids(self, operator, value):
        reviews = self.env["tier.review"].search([
            ("model", "=", self._name),
            ("reviewer_ids", operator, value),
            ("status", "=", "pending")])
        return [("id", "in", list(set(reviews.mapped("res_id"))))]

    @api.multi
    def _compute_validated_rejected(self):
        for rec in self:
            rec.validated = self._calc_reviews_validated(rec.review_ids)
            rec.rejected = self._calc_reviews_rejected(rec.review_ids)

    @api.model
    def _calc_reviews_validated(self, reviews):
        """Override for different validation policy."""
        if not reviews:
            return False
        return not any([s != "approved" for s in reviews.mapped("status")])

    @api.model
    def _calc_reviews_rejected(self, reviews):
        """Override for different rejection policy."""
        return any([s == "rejected" for s in reviews.mapped("status")])

    @api.multi
    def _compute_need_validation(self):
        obj_tier_definition = self.env["tier.definition"]
        for rec in self:
            criteria = [
                ("model", "=", self._name),
                ("special_validation", "=", False),
            ]
            tiers = obj_tier_definition.search(criteria)
            valid_tiers = any([rec.evaluate_tier(tier) for tier in tiers])
            rec.need_validation = not rec.review_ids and valid_tiers and \
                getattr(rec, self._state_field) in self._state_from

    @api.multi
    def evaluate_tier(self, tier):
        try:
            res = safe_eval(tier.python_code, globals_dict={"rec": self})
        except Exception as error:
            raise UserError(_(
                "Error evaluating tier validation conditions.\n %s") % error)
        return res

    @api.model
    def _get_under_validation_exceptions(self):
        """Extend for more field exceptions."""
        fields = [
            "message_last_post",
            "message_follower_ids",
        ]
        return fields

    @api.multi
    def _check_allow_write_under_validation(self, vals):
        """Allow to add exceptions for fields that are allowed to be written
        even when the record is under validation."""
        exceptions = self._get_under_validation_exceptions()
        for val in vals:
            if val not in exceptions:
                return False
        return True

    @api.multi
    def write(self, vals):
        for rec in self:
            if (getattr(rec, self._state_field) in self._state_from and
                    vals.get(self._state_field) in self._state_to):
                if rec.need_validation:
                    # try to validate operation
                    reviews = rec.request_validation()
                    rec._validate_tier(reviews)
                    if not self._calc_reviews_validated(reviews):
                        raise ValidationError(_(
                            "This action needs to be validated for at least "
                            "one record. \nPlease request a validation."))
                if rec.review_ids and not rec.validated:
                    raise ValidationError(_(
                        "A validation process is still open for at least "
                        "one record."))
            if (rec.review_ids and getattr(rec, self._state_field) in
                    self._state_from and not vals.get(self._state_field) in
                    (self._state_to + [self._cancel_state]) and not
                    self._check_allow_write_under_validation(vals)):
                raise ValidationError(_("The operation is under validation."))
        if vals.get(self._state_field) in self._state_from:
            self.mapped("review_ids").unlink()
            self.mapped("reviewer_partner_ids").unlink()
            self.definition_id = False
        return super(TierValidation, self).write(vals)

    @api.multi
    def _validate_tier(self, tiers=False):
        self.ensure_one()
        tier_reviews = tiers or self.review_ids
        user_reviews = tier_reviews.filtered(
            lambda r: r.status in ("pending") and
            (self.env.user.id in r.reviewer_ids.ids))
        if self.definition_id.validate_sequence:
            if not self._check_validate_by_sequence(user_reviews):
                return
        user_reviews.write({
            "status": "approved",
            "date": fields.Datetime.now(),
            "user_id": self.env.user.id,
        })

    @api.multi
    def _check_validate_by_sequence(self, user_reviews):
        result = False
        if user_reviews.sequence == 1:
            result = True
        else:
            prev_reviews = self.review_ids.filtered(
                lambda r: r.status in ("pending") and
                r.sequence == (user_reviews.sequence - 1))
            if not prev_reviews:
                result = True
        return result

    @api.multi
    def validate_tier(self):
        for rec in self:
            rec._validate_tier()

    @api.multi
    def reject_tier(self):
        for rec in self:
            user_reviews = rec.review_ids.filtered(
                lambda r: r.status in ("pending") and
                (self.env.user.id in r.reviewer_ids.ids))
            if rec.definition_id.validate_sequence:
                if not rec._check_validate_by_sequence(user_reviews):
                    return
            user_reviews.write({
                "status": "rejected",
                "date": fields.Datetime.now(),
                "user_id": self.env.user.id,
            })

    @api.multi
    def request_validation(self):
        td_obj = self.env["tier.definition"]
        reviewer_ids = False
        for rec in self:
            if getattr(rec, self._state_field) in self._state_from:
                if rec.definition_id:
                    if self.evaluate_tier(rec.definition_id):
                        rec.write({"definition_id": rec.definition_id.id})
                    else:
                        rec.write({"definition_id": False})
                if not rec.definition_id:
                    criteria_definition = [
                        ("model", "=", self._name),
                        ("special_validation", "=", False),
                    ]
                    definition_ids = td_obj.search(
                        criteria_definition,
                        order="sequence desc",
                    )
                    if definition_ids:
                        for definition in definition_ids:
                            if self.evaluate_tier(definition):
                                rec.write({"definition_id": definition.id})
                                break
                reviewer_ids = rec.create_reviewer()
        return reviewer_ids

    @api.multi
    def create_reviewer(self):
        self.ensure_one()
        td_reviewer_obj = self.env["tier.definition.review"]
        tr_obj = created_trs = self.env["tier.review"]
        sequence = 0

        criteria_reviewer = [
            ("definition_id", "=", self.definition_id.id)
        ]
        reviewer_ids =\
            td_reviewer_obj.search(
                criteria_reviewer,
                order="sequence"
            )
        if reviewer_ids:
            for reviewer in reviewer_ids:
                sequence += 1
                created_trs += tr_obj.create({
                    "model": self._name,
                    "res_id": self.id,
                    "definition_review_id": reviewer.id,
                    "sequence": sequence,
                })
        return created_trs

    @api.multi
    def restart_validation(self):
        for rec in self:
            if getattr(rec, self._state_field) in self._state_from:
                rec.mapped("review_ids").unlink()
