# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval as eval


class BaseSequenceConfigurator(models.Model):
    _name = "base.sequence_configurator"
    _description = "Sequence Configurator"

    model_id = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    note = fields.Text(
        string="Note"
    )
    line_ids = fields.One2many(
        string="Lines",
        comodel_name="base.sequence_configurator_line",
        inverse_name="generator_id",
    )
    fallback_sequence_id = fields.Many2one(
        string="Fallback Sequence",
        comodel_name="ir.sequence",
        required=True,
        company_dependent=True,
    )
    initial_string = fields.Char(
        string="Initial String",
        required=True,
        default="/",
    )
    sequence_field_id = fields.Many2one(
        string="Field",
        comodel_name="ir.model.fields",
        required=True,
    )

    @api.multi
    def _create_sequence(self, document):
        result = False
        for line in self.line_ids:
            if not line.check_condition(document):
                continue

            result = line.create_sequence(document)
        if not result:
            result = self._create_fallback_sequence()
        return result

    @api.multi
    def _create_fallback_sequence(self):
        self.ensure_one()
        result = False
        sequence = self.fallback_sequence_id
        if sequence:
            result = sequence.next_by_id()
        return result

    @api.onchange("model_id")
    def onchange_sequence_field_id(self):
        self.sequence_field_id = False


class BaseSequenceConfiguratorLine(models.Model):
    _name = "base.sequence_configurator_line"
    _description = "Sequence Configurator Line"
    _order = "sequence, id"

    generator_id = fields.Many2one(
        string="Generator",
        comodel_name="base.sequence_configurator",
        required=True,
        ondelete="cascade",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=5,
        required=True,
    )
    domain = fields.Text(
        string="Condition",
        required=True,
        default="result = True",
    )
    sequence_computation_code = fields.Text(
        string="Sequence Computation Code",
        required=True,
        default="result = False",
    )

    def _get_localdict(self, document):
        self.ensure_one()
        return {
            "env": self.env,
            "document": document,
        }

    @api.multi
    def check_condition(self, document):
        self.ensure_one()
        result = False
        localdict = self._get_localdict(document)
        try:
            eval(self.domain,
                 localdict, mode="exec", nocopy=True)
            result = localdict["result"]
        except:
            result = False
        return result

    @api.multi
    def _get_sequence_id(self, document):
        self.ensure_one()
        result = False
        localdict = self._get_localdict(document)
        try:
            eval(self.sequence_computation_code,
                 localdict, mode="exec", nocopy=True)
            result = localdict["result"]
        except:
            raise UserError(_("Error on get sequence"))
        return result

    @api.model
    def create_sequence(self, document):
        self.ensure_one()
        sequence_id = self._get_sequence_id(document)
        result = False
        if sequence_id:
            sequence = self.env["ir.sequence"].browse([sequence_id])[0]
            result = sequence.next_by_id()
        return result
