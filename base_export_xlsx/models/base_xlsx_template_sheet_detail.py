# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import fields, models


class BaseXlsxTemplateSheetDetail(models.Model):
    _name = "base.xlsx.template.sheet.detail"
    _description = "Base Xlsx Template Sheet Detail"

    field_name = fields.Char(
        string="Field",
    )
    template_sheet_id = fields.Many2one(
        string="Template Sheet",
        comodel_name="base.xlsx.template.sheet",
    )
    detail_ids = fields.One2many(
        string="Detail",
        comodel_name="base.xlsx.template.sheet.detail.detail",
        inverse_name="template_sheet_detail_id",
    )
