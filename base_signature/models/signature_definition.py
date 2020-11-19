# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class SignatureDefinition(models.Model):
    _name = "signature.definition"
    _description = "Signature Definition"
    _order = "sequence, id"

    @api.model
    def _get_signature_validation_model_names(self):
        res = []
        return res

    name = fields.Char(
        string="Name",
        required=True,
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
        string="Signature Definition Expression",
        help="Write Python code that defines when this signature "
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
    signature_signee_ids = fields.One2many(
        string="Signee",
        comodel_name="signature.definition.signee",
        inverse_name="signature_id",
    )

    @api.onchange(
        "model_id"
    )
    def onchange_model_id(self):
        model = self._get_signature_validation_model_names()
        return {"domain": {
            "model_id": [
                ("model", "in", model)]}}
