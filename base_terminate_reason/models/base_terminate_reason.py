# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class BaseTerminateReason(models.Model):
    _name = "base.terminate.reason"
    _description = "Base Terminate Reason"

    name = fields.Char(
        string="Terminate Reason",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    description = fields.Text(
        string="Note",
    )
