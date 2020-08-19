# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class BaseCancelReasonConfigurator(models.Model):
    _name = "base.cancel.reason_config"
    _description = "Base Cancel Reason Configurator"

    name = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
    )
    method_cancel_name = fields.Char(
        string="Method Cancel Name"
    )
    cancel_reason_ids = fields.Many2many(
        string="Cancel Reason",
        comodel_name="base.cancel.reason",
        relation="base_reason_config_rel",
        column1="config_id",
        column2="reason_id",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    description = fields.Text(
        string="Note",
    )

    @api.model
    def _get_default_reason_ids(self):
        result = False
        obj_cancel_reason = self.env["base.cancel.reason"]
        criteria = [("default", "=", True)]
        cancel_reason_ids = obj_cancel_reason.search(criteria)
        if cancel_reason_ids:
            result = cancel_reason_ids.ids
        return result

    @api.model
    def create(self, vals):
        _super = super(BaseCancelReasonConfigurator, self)
        res = _super.create(vals)

        cancel_reason_ids = self._get_default_reason_ids()
        if cancel_reason_ids:
            res.write({
                "cancel_reason_ids": [(6, 0, cancel_reason_ids)]
            })

        return res
