# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime
import pytz
from openerp import models, api, fields, _
from openerp.exceptions import Warning as UserError
from openerp.tools.safe_eval import safe_eval as eval


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
    date_field_id = fields.Many2one(
        string="Field Date",
        comodel_name="ir.model.fields",
    )

    @api.multi
    def _create_sequence(self, document, sequence_date):
        result = False
        for line in self.line_ids:
            if not line.check_condition(document):
                continue
            sequence = line.create_sequence(document, sequence_date)

            if line.prefix_suffix_computation:
                result = line._get_prefix_suffix_computation(
                    document, sequence, sequence_date
                )
                break
            else:
                result = sequence
                break

        if not result:
            result = self._create_fallback_sequence()

        return result

    @api.multi
    def _create_fallback_sequence(self):
        self.ensure_one()
        result = False
        sequence = self.fallback_sequence_id
        if sequence:
            result = self.env["ir.sequence"].next_by_id(sequence.id)
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
    prefix_suffix_computation = fields.Boolean(
        string="Prefix Suffix Computation",
    )
    prefix_computation_code = fields.Text(
        string="Prefix Computation Code",
        required=True,
        default="prefix = ''",
    )
    suffix_computation_code = fields.Text(
        string="Suffix Computation Code",
        required=True,
        default="suffix = ''",
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
    def _get_sequence(self, document):
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

    def _get_prefix(self, document):
        self.ensure_one()
        result = False
        localdict = self._get_localdict(document)
        try:
            eval(
                self.prefix_computation_code,
                localdict,
                mode="exec",
                nocopy=True,
            )
            result = localdict["prefix"]
        except Exception as error:
            raise UserError(_("Error on get prefix.\n %s") % error)
        return result

    def _get_suffix(self, document):
        self.ensure_one()
        result = False
        localdict = self._get_localdict(document)
        try:
            eval(
                self.suffix_computation_code,
                localdict,
                mode="exec",
                nocopy=True,
            )
            result = localdict["suffix"]
        except Exception as error:
            raise UserError(_("Error on get suffix.\n %s") % error)
        return result

    def _interpolate(self, s, d):
        return (s % d) if s else ""

    def _interpolation_dict(self, date=None, date_range=None):
        self.ensure_one()
        now = range_date = effective_date = datetime.now(
            pytz.timezone(self._context.get("tz") or "UTC")
        )
        if date or self._context.get("ir_sequence_date"):
            effective_date = fields.Datetime.from_string(
                date or self._context.get("ir_sequence_date")
            )
        if date_range or self._context.get("ir_sequence_date_range"):
            range_date = fields.Datetime.from_string(
                date_range or self._context.get("ir_sequence_date_range")
            )

        sequences = {
            "year": "%Y",
            "month": "%m",
            "day": "%d",
            "y": "%y",
            "doy": "%j",
            "woy": "%W",
            "weekday": "%w",
            "h24": "%H",
            "h12": "%I",
            "min": "%M",
            "sec": "%S",
        }
        res = {}
        for key, format in sequences.items():
            res[key] = effective_date.strftime(format)
            res["range_" + key] = range_date.strftime(format)
            res["current_" + key] = now.strftime(format)

        return res

    def _get_prefix_suffix_computation(self, document, sequence, date):
        self.ensure_one()
        result = False
        prefix = self._get_prefix(document)
        suffix = self._get_suffix(document)

        d = self._interpolation_dict(date_range=date)

        try:
            interpolated_prefix = self._interpolate(prefix, d)
            interpolated_suffix = self._interpolate(suffix, d)
        except Exception as error:
            msg = _("Error on convert prefix and suffix.\n %s")
            raise UserError(msg) % (error)

        result = interpolated_prefix + sequence + interpolated_suffix
        return result

    @api.model
    def create_sequence(self, document, sequence_date):
        self.ensure_one()
        obj_sequence = self.env["ir.sequence"]
        sequence = self._get_sequence(document)
        result = False
        if sequence:
            ctx = {
                "ir_sequence_date": sequence_date,
            }
            result = \
                obj_sequence.with_context(ctx).next_by_id(sequence.id)
        return result
