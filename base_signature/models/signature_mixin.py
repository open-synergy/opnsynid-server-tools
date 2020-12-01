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
        domain=lambda self: [("model", "=", self._name)],
    )
    signature_signee_ids = fields.One2many(
        string="Signee",
        comodel_name="signature.signee",
        inverse_name="res_id",
        domain=lambda self: [("model", "=", self._name)],
        auto_join=True,
    )

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        x2many_field = "signature_signee_ids"
        if x2many_field in field_onchange:
            subfields = getattr(self, x2many_field)._fields.keys()
            for subfield in subfields:
                field_onchange.setdefault(
                    u"{}.{}".format(x2many_field, subfield), u"",
                )
        return super(SignatureMixin, self).onchange(
            values, field_name, field_onchange,
        )

    @api.multi
    def evaluate_signature(self, signature):
        try:
            res = safe_eval(signature.python_code, globals_dict={"rec": self})
        except Exception as error:
            raise UserError(_(
                "Error evaluating signature conditions.\n %s") % error)
        return res

    @api.onchange(
        "signature_definition_id",
    )
    def _onchange_signature_definition_id(self):
        tmpls = self.get_definition_templates()
        props_good = tmpls.mapped("signature_signee_ids")
        props_enabled = \
            self.mapped(
                "signature_signee_ids.signature_definition_signee_id")
        to_add = props_good - props_enabled
        to_remove = props_enabled - props_good
        values = self.signature_signee_ids
        values = values.filtered(
            lambda r: r.signature_definition_signee_id not in to_remove)
        for prop in to_add.sorted():
            newvalue = self.signature_signee_ids.new({
                "model": self._name,
                "res_id": self.id,
                "signature_definition_id": self.signature_definition_id.id,
                "signature_definition_signee_id": prop.id,
            })
            values += newvalue
        self.signature_signee_ids = values
        if self.get_definition_templates() != tmpls:
            self._onchange_signature_definition_id()

    @api.multi
    def get_definition_templates(self):
        return self.mapped("signature_definition_id")

    @api.multi
    def button_update_signature(self):
        self.ensure_one()
        self._onchange_signature_definition_id()
