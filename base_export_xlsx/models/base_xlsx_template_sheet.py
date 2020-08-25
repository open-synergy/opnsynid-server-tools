# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import fields, models


class BaseXlsxTemplateSheet(models.Model):
    _name = "base.xlsx.template.sheet"
    _description = "Base Xlsx Template Sheet"

    name = fields.Char(
        string="Name",
    )
    template_id = fields.Many2one(
        string="Template",
        comodel_name="base.xlsx.template",
    )
    template_sheet_header_ids = fields.One2many(
        string="Sheet Header",
        comodel_name="base.xlsx.template.sheet.header",
        inverse_name="template_sheet_id",
    )
    template_sheet_detail_ids = fields.One2many(
        string="Sheet Detail",
        comodel_name="base.xlsx.template.sheet.detail",
        inverse_name="template_sheet_id",
    )
