# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import fields, models


class BaseXlsxTemplate(models.Model):
    _name = "base.xlsx.template"
    _description = "Base Xlsx Template"

    name = fields.Char(
        string="Name",
    )
    file_name = fields.Char(
        string='File Name',
    )
    file = fields.Binary(
        string="File Content",
    )
    model_id = fields.Many2one(
        string="Resource Model",
        comodel_name="ir.model",
    )
    template_sheet_ids = fields.One2many(
        string="Sheet Name",
        comodel_name="base.xlsx.template.sheet",
        inverse_name="template_id",
    )
    python_condition = fields.Text(
        string="Condition",
        help="The result of executing the expresion must be "
             "a boolean.",
        default="""# Available locals:\n#  - record: current record""",
    )
    group_ids = fields.Many2many(
        string="Allowed Groups",
        comodel_name="res.groups",
        rel="rel_base_xlsx_template_group",
        col1="template_id",
        col2="group_id",
    )
    description = fields.Text(
        string="Notes",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
