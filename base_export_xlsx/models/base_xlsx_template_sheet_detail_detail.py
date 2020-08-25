# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp.tools.safe_eval import safe_eval
from datetime import datetime as dt
from openerp import api, fields, models
from dateutil.parser import parse
import logging
_logger = logging.getLogger(__name__)


class BaseXlsxTemplateSheetDetailDetail(models.Model):
    _name = "base.xlsx.template.sheet.detail.detail"
    _description = "Base Xlsx Template Sheet Detail Detail"

    template_sheet_detail_id = fields.Many2one(
        string="#Template Sheet",
        comodel_name="base.xlsx.template.sheet.detail",
    )
    cell = fields.Char(
        string="Cell",
    )
    field_name = fields.Char(
        string="Field",
    )
    field_cond = fields.Char(
        string="Field Cond.",
    )
    style = fields.Char(
        string="Style",
    )

    @api.model
    def isfloat(self, input_val):
        try:
            float(input_val)
            return True
        except ValueError:
            return False

    @api.model
    def isinteger(self, input_val):
        try:
            int(input_val)
            return True
        except ValueError:
            return False

    @api.model
    def isdatetime(self, input_val):
        try:
            if len(input_val) == 10:
                dt.strptime(input_val, '%Y-%m-%d')
            elif len(input_val) == 19:
                dt.strptime(input_val, '%Y-%m-%d %H:%M:%S')
            else:
                return False
            return True
        except ValueError:
            return False

    @api.model
    def str_to_number(self, input_val):
        if isinstance(input_val, str):
            if ' ' not in input_val:
                if self.isdatetime(input_val):
                    return parse(input_val)
                elif self.isinteger(input_val):
                    if not (len(input_val) > 1 and input_val[:1] == "0"):
                        return int(input_val)
                elif self.isfloat(input_val):
                    if not (input_val.find(".") > 2 and input_val[:1] == "0"):
                        return float(input_val)
        return input_val

    @api.multi
    def set_detail(self, sheet, data, index):
        self.ensure_one()
        obj_xlsx_template = self.env["base.export.xlsx"]
        field_data = obj_xlsx_template.get_field_data(
            self.field_name,
            data,
        )
        eval_cond = self.field_cond or 'value or ""'
        eval_context = \
            obj_xlsx_template.get_eval_context(self._name, self, field_data)
        value = safe_eval(eval_cond, eval_context)
        if value is not None:
            col, row = obj_xlsx_template.split_row_col(self.cell)
            row_line = row + index
            index_line = '%s%s' % (col, row_line)
            sheet[index_line] = self.str_to_number(value)
        if self.style:
            styles = obj_xlsx_template.get_styles()
            obj_xlsx_template.set_style(
                sheet[index_line], self.style, styles)
