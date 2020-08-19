# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class BaseCancelReason(models.Model):
    _name = "base.cancel.reason"
    _description = "Base Cancel Reason"

    name = fields.Char(
        string="Cancel Reason",
        required=True,
    )
    type = fields.Selection(
        string="Type",
        selection=[
            ("fixed", "Fixed"),
            ("not_fixed", "Need more explanation"),
        ],
        default="fixed",
    )
    default = fields.Boolean(
        string="Create as Default",
        default=False,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    description = fields.Text(
        string="Note",
    )
