# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


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
