# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.tools.safe_eval import safe_eval as eval
from openerp.exceptions import Warning as UserError


class SignatureSignee(models.Model):
    _name = "signature.signee"
    _description = "Signature Signee"

    model = fields.Char(
        string="Related Document Model",
        index=True,
    )
    res_id = fields.Integer(
        string="Related Document ID",
        index=True,
    )
    signature_definition_signee_id = fields.Many2one(
        comodel_name="signature.definition.signee",
        ondelete="restrict",
        required=True,
    )
    signature_key = fields.Char(
        related="signature_definition_signee_id.signature_key",
        readonly=True,
    )
    signature_type = fields.Selection(
        related="signature_definition_signee_id.signature_type",
        readonly=True,
    )
    signature_item_id = fields.Many2one(
        related="signature_definition_signee_id.signature_item_id",
        readonly=True,
    )
    signee_id = fields.Many2one(
        string="Signee",
        comodel_name="res.users",
        compute="_compute_signee_id",
        store=True,
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
        "signature_definition_signee_id",
    )
    def _compute_signee_id(self):
        for document in self:
            signee_id = False
            if document.signature_definition_signee_id:
                signature_type = document.signature_type
                user_id =\
                    document.signature_definition_signee_id.signature_user_id
                if user_id:
                    signee_id = user_id.id

                if signature_type == "python":
                    python_code = \
                        document.signature_definition_signee_id.python_code
                    result = document._evaluate_python_code(python_code)
                    if result:
                        if "user" in result:
                            signee_id = result["user"]
                        else:
                            msg_err = "No User defines on python code"
                            raise UserError(_(msg_err))
                document.signee_id = signee_id
