# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class BaseTerminateReasonConfigurator(models.Model):
    _name = "base.terminate.reason_config"
    _description = "Base Terminate Reason Configurator"

    name = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
    )
    method_terminate_name = fields.Char(
        string="Method Termination Name"
    )
    terminate_reason_ids = fields.Many2many(
        string="Termination Reason",
        comodel_name="base.terminate.reason",
        relation="terminate_reason_config_rel",
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
