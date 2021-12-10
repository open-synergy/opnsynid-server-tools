# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime, timedelta

import pytz
from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

try:
    import numpy as np
    import pandas as pd
except (ImportError, IOError) as err:
    _logger.debug(err)


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    use_date_range = fields.Boolean(
        string="Use subsequences per date_range",
    )
    date_range_ids = fields.One2many(
        string="Subsequences",
        comodel_name="ir.sequence.date_range",
        inverse_name="sequence_id",
    )

    @api.multi
    def write(self, values):
        new_implementation = values.get("implementation")
        for seq in self:
            i = values.get("number_increment", seq.number_increment)
            n = values.get("number_next", seq.number_next)
            if seq.implementation == "standard":
                if new_implementation in ("standard", None):
                    if seq.number_increment != i:
                        seq.date_range_ids._alter_sequence(number_increment=i)
                else:
                    for sub_seq in seq.date_range_ids:
                        sub_seq._drop_sequences()
            else:
                if new_implementation in ("no_gap", None):
                    pass
                else:
                    for sub_seq in seq.date_range_ids:
                        seq_name = "ir_sequence_%03d_%03d" % (seq.id, sub_seq.id)
                        sub_seq._create_sequence(seq_name, i, n)
        return super(IrSequence, self).write(values)

    @api.multi
    def _create_date_range_seq(self, date):
        obj_sequence_range = self.env["ir.sequence.date_range"]
        year = fields.Date.from_string(date).strftime("%Y")
        date_from = "{}-01-01".format(year)
        date_to = "{}-12-31".format(year)
        date_range = obj_sequence_range.search(
            [
                ("sequence_id", "=", self.id),
                ("date_from", ">=", date),
                ("date_from", "<=", date_to),
            ],
            order="date_from desc",
            limit=1,
        )
        if date_range and date_range.date_from:
            dt_from = pd.to_datetime(date_range.date_from)
            date_to = dt_from + timedelta(days=-1)
        date_range = obj_sequence_range.search(
            [
                ("sequence_id", "=", self.id),
                ("date_to", ">=", date_from),
                ("date_to", "<=", date),
            ],
            order="date_to desc",
            limit=1,
        )
        if date_range and date_range.date_to:
            dt_to = pd.to_datetime(date_range.date_to)
            date_from = dt_to + np.timedelta64(1, "D")
        seq_date_range = obj_sequence_range.sudo().create(
            {
                "date_from": date_from,
                "date_to": date_to,
                "sequence_id": self.id,
            }
        )
        return seq_date_range

    @api.multi
    def _next(self):
        _super = super(IrSequence, self)
        if not self.use_date_range:
            return _super._next()
        obj_sequence_range = self.env["ir.sequence.date_range"]
        dt = fields.Date.today()
        if self._context.get("ir_sequence_date"):
            dt = self._context.get("ir_sequence_date")
        seq_date = obj_sequence_range.search(
            [
                ("sequence_id", "=", self.id),
                ("date_from", "<=", dt),
                ("date_to", ">=", dt),
            ],
            limit=1,
        )
        if not seq_date:
            seq_date = self._create_date_range_seq(dt)
        return seq_date.with_context(ir_sequence_date_range=dt)._next()

    def _interpolation_dict_context(self, context=None):
        res = super(IrSequence, self)._interpolation_dict_context(context)
        dict = res.copy()
        range_date = datetime.now(pytz.timezone(context.get("tz") or "UTC"))
        if context.get("ir_sequence_date_range"):
            range_date = fields.Datetime.from_string(
                context.get("ir_sequence_date_range")
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
        for key, value in sequences.iteritems():  # noqa: B301
            dict["range_" + key] = range_date.strftime(value)
        return dict

    @api.multi
    def _get_prefix_suffix(self):
        self.ensure_one()
        d = self._interpolation_dict_context(self._context)
        prefix = self.prefix
        suffix = self.suffix
        if self._context.get("custom_prefix"):
            prefix = self._context.get("custom_prefix")
        if self._context.get("custom_sufix"):
            suffix = self._context.get("custom_suffix")
        try:
            interpolated_prefix = self._interpolate(prefix, d)
            interpolated_suffix = self._interpolate(suffix, d)
        except ValueError:
            msg = _("Invalid prefix or suffix for sequence '%s'")
            raise UserError(msg) % (self.get("name"))
        return interpolated_prefix, interpolated_suffix

    @api.multi
    def get_next_char(self, number_next):
        self.ensure_one()
        interpolated_prefix, interpolated_suffix = self._get_prefix_suffix()
        return (
            interpolated_prefix
            + "%%0%sd" % self.padding % number_next
            + interpolated_suffix
        )
