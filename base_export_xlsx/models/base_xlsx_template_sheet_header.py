# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import api, fields, models
from openerp.tools.safe_eval import safe_eval


class BaseXlsxTemplateSheetHeader(models.Model):
    _name = "base.xlsx.template.sheet.header"
    _description = "Base Xlsx Template Sheet Header"

    template_sheet_id = fields.Many2one(
        string="Template Sheet",
        comodel_name="base.xlsx.template.sheet",
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

    @api.multi
    def set_header(self, sheet, data):
        self.ensure_one()
        obj_xlsx_template = self.env["base.export.xlsx"]
        field_data = obj_xlsx_template.get_field_data(
            self.field_name,
            data
        )
        eval_cond = self.field_cond or 'value or ""'
        eval_context = \
            obj_xlsx_template.get_eval_context(self._name, self, field_data)
        value = safe_eval(eval_cond, eval_context)
        if value is not None:
            sheet[self.cell] = value
        if self.style:
            styles = obj_xlsx_template.get_styles()
            obj_xlsx_template.set_style(
                sheet[self.cell], self.style, styles)
