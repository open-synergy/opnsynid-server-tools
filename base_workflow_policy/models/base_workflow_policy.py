# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields
from openerp.tools.safe_eval import safe_eval as eval


class BaseWorkflowPolicy(models.Model):
    _name = "base.workflow_policy"
    _description = "Workflow Policy"

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
        comodel_name="base.workflow_policy_line",
        inverse_name="workflow_id",
    )


class BaseWorkflowPolicyLine(models.Model):
    _name = "base.workflow_policy_line"
    _description = "Workflow Policy Line"

    workflow_id = fields.Many2one(
        string="Workflow Policy",
        comodel_name="base.workflow_policy",
        required=True,
        ondelete="cascade",
    )
    field_id = fields.Many2one(
        string="Field",
        comodel_name="ir.model.fields"
    )
    python_code = fields.Text(
        string="Python Code",
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
    def get_policy(self, document):
        self.ensure_one()
        result = False
        button_group_ids = []
        user = self.env.user
        group_ids = user.groups_id.ids
        localdict = self._get_localdict(document)

        try:
            eval(self.python_code,
                 localdict, mode="exec", nocopy=True)
            button_group_ids = localdict["result"]
        except:
            button_group_ids = []
        if not button_group_ids:
            result = True
        else:
            if (set(button_group_ids) & set(group_ids)):
                result = True
        return result
