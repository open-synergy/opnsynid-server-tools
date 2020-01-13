# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, SUPERUSER_ID, _
from openerp.tools.safe_eval import safe_eval as eval
from openerp.exceptions import Warning as UserError


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
                allowed_print = self._check_allowed_print(print_policy)
                if allowed_print:
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

    print_by_download = fields.Boolean(
        string="Print By Download"
    )

    @api.multi
    @api.onchange(
        "report_action_id",
    )
    def onchange_print_by_download(self):
        if self.report_action_id:
            self.print_by_download = True
            user = self.env.user
            group_ids = user.groups_id.ids
            print_policy_ids =\
                self._get_print_policy()
            if print_policy_ids:
                if print_policy_ids.download_group_ids:
                    download_group_ids =\
                        print_policy_ids.download_group_ids.ids
                    if (set(download_group_ids) & set(group_ids)):
                        self.print_use_escpos = True
                    else:
                        self.print_by_download = False
        else:
            self.print_by_download = False

    @api.multi
    def _get_print_policy(self):
        self.ensure_one()
        obj_print_policy =\
            self.env["base.print.policy"]
        criteria = [
            ("report_action_id", "=", self.report_action_id.id)
        ]
        print_policy_ids = obj_print_policy.search(criteria)
        return print_policy_ids

    @api.multi
    def _check_allowed_print(self, object):
        user = self.env.user
        if user.id == SUPERUSER_ID:
            result = True
        else:
            if object.group_ids:
                user_group_ids = user.groups_id.ids
                if (set(object.group_ids.ids) & set(user_group_ids)):
                    result = True
                else:
                    result = False
            else:
                result = True
        return result

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
        report_action = self.env["report"].get_action(
            object, self.report_action_id.report_name)
        return report_action
