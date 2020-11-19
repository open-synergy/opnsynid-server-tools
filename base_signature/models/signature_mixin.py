# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError
from openerp.tools.safe_eval import safe_eval


class SignatureMixin(models.AbstractModel):
    _name = "signature.mixin"
    _description = "Signature Mixin"

    signature_definition_id = fields.Many2one(
        string="Signature Template",
        comodel_name="signature.definition",
    )
    signature_signee_ids = fields.One2many(
        string="Signee",
        comodel_name="signature.signee",
        inverse_name="res_id",
        domain=lambda self: [("model", "=", self._name)],
        auto_join=True,
    )

    @api.multi
    def evaluate_signature(self, signature):
        try:
            res = safe_eval(signature.python_code, globals_dict={"rec": self})
        except Exception as error:
            raise UserError(_(
                "Error evaluating signature conditions.\n %s") % error)
        return res

    @api.multi
    def get_signature(self):
        obj_signature_definition = \
            self.env["signature.definition"]
        signature_signee_ids = False
        for rec in self:
            if not rec.signature_definition_id:
                criteria_definition = [
                    ("model", "=", self._name),
                ]
                definition_ids = obj_signature_definition.search(
                    criteria_definition,
                )
                if definition_ids:
                    for definition in definition_ids:
                        if self.evaluate_signature(definition):
                            rec.write({
                                "signature_definition_id": definition.id
                            })
                            break
            else:
                rec.delete_signature()
            signature_signee_ids = rec.create_signature()
        return signature_signee_ids

    @api.multi
    def create_signature(self):
        self.ensure_one()
        obj_sign_def_signee = self.env["signature.definition.signee"]
        obj_sign_signee = created_trs = self.env["signature.signee"]

        criteria = [
            ("signature_id", "=", self.signature_definition_id.id)
        ]
        definition_signee_ids =\
            obj_sign_def_signee.search(
                criteria,
            )
        if definition_signee_ids:
            for signee in definition_signee_ids:
                created_trs += obj_sign_signee.create({
                    "model": self._name,
                    "res_id": self.id,
                    "signature_definition_id": self.signature_definition_id.id,
                    "signature_definition_signee_id": signee.id,
                })
        return created_trs

    @api.multi
    def delete_signature(self):
        self.ensure_one()
        obj_sign_signee = self.env["signature.signee"]

        criteria = [
            ("model", "=", self._name),
            ("res_id", "=", self.id),
        ]
        signee_ids =\
            obj_sign_signee.search(
                criteria,
            )
        if signee_ids:
            signee_ids.unlink()
        return True
