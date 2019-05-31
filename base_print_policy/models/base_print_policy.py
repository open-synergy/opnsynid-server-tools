# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class BasePrintPolicy(models.Model):
    _name = "base.print.policy"
    _description = "Base Print Policy"

    name = fields.Char(
        string="Name",
        required=True
    )
    report_action_id = fields.Many2one(
        comodel_name="ir.actions.report.xml",
        string="Report",
        required=True
    )
    model = fields.Char(
        string="Model",
        related="report_action_id.model",
        store=False,
        readonly=True
    )
    python_condition = fields.Text(
        string="Condition",
        help="The result of executing the expresion must be "
             "a boolean.",
        default="""# Available locals:\n#  - record: current record""",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    description = fields.Text(
        string="Note",
    )
