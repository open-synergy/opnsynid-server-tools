# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields
from openerp.tools.safe_eval import safe_eval as eval


class BasePrintDocument(models.TransientModel):
    _name = "base.print.document"
    _description = "Base Print Document"

    @api.model
    def _compute_allowed_print_action_ids(self):
        result = []
        obj_print_policy =\
            self.env["base.print.policy"]
        active_model = self.env.context.get("active_model", "")
        criteria = [
            ("report_action_id.model", "=", active_model)
        ]
        print_policy_ids = obj_print_policy.search(criteria)
        if print_policy_ids:
            for print_policy in print_policy_ids:
                policy =\
                    self.get_print_policy(
                        print_policy.python_condition)
                if policy:
                    result.append(print_policy.report_action_id.id)
        return result

    allowed_print_action_ids = fields.Many2many(
        string="Allowed Print Action",
        comodel_name="ir.actions.report.xml",
        default=lambda self: self._compute_allowed_print_action_ids(),
        relation="rel_print_document_2_action_report",
        column1="wizard_id",
        column2="report_action_id",
    )

    report_action_id = fields.Many2one(
        string="Report Template",
        comodel_name="ir.actions.report.xml",
        required=True,
    )

    @api.multi
    def _get_object(self):
        active_id = self.env.context.get("active_id", False)
        active_model = self.env.context.get("active_model", "")
        # TODO: Assert when invalid active_id or active_model
        object = self.env[active_model].browse(
            [active_id]
        )[0]
        return object

    @api.multi
    def _get_localdict(self):
        return {
            "record": self._get_object()
        }

    @api.multi
    def get_print_policy(self, python_condition):
        localdict = self._get_localdict()

        try:
            eval(python_condition,
                 localdict, mode="exec", nocopy=True)
            result = localdict["result"]
        except:
            result = True

        return result

    @api.multi
    def action_print(self):
        object = self._get_object()
        return self.env["report"].get_action(
            object, self.report_action_id.report_name)
