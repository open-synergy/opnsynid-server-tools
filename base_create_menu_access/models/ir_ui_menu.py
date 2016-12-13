# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    custom_group_id = fields.Many2one(
        string="Custom Group",
        comodel_name="res.groups"
    )
