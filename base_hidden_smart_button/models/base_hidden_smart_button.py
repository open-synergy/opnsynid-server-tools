# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields

class HiddenSmartButton(models.Model):
    _name = "base.hidden_smart_button"
    _description = "Hidden Smart Button"

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    name = fields.Char(
        string="Button Name",
        required=True,
    )
    view_id = fields.Many2one(
        string="View",
        comodel_name="ir.ui.view",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    user_ids = fields.Many2many(
        string="Users",
        comodel_name="res.users",
        relation="rel_hidden_smart_button_2_user",
        column1="hidden_id",
        column2="user_id",
    )
    groups_ids = fields.Many2many(
        string="Groups",
        comodel_name="res.groups",
        relation="rel_hidden_smart_button_2_group",
        column1="hidden_id",
        column2="group_id",
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default = lambda self: self._default_company_id(),
    )
