# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openerp import models, fields, api
from openerp.tools import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    custom_group_id = fields.Many2one(
        string="Custom Group",
        comodel_name="res.groups"
    )

    @api.multi
    def _check_custom_group(self):
        self.ensure_one()
        result = False
        if self.custom_group_id:
            result = self.custom_group_id
        return result

    @api.multi
    def _prepare_data_group(self):
        self.ensure_one()
        category_id = self.env.ref(
            "base_create_menu_access.custom_menu_access_module_category_data"
        )
        value = {
            "name": self.display_name,
            "category_id": category_id.id,
            "users": [(6, 0, [SUPERUSER_ID])]
        }
        return value

    @api.multi
    def set_menu_access(self):
        self.ensure_one()
        obj_res_groups = self.env["res.groups"]
        group = self._check_custom_group()

        if self.action:
            if group:
                custom_group_id = group
            else:
                data_group = self._prepare_data_group()
                custom_group_id = obj_res_groups.create(data_group)
            self.write({
                "custom_group_id": custom_group_id.id,
                "groups_id": [(6, 0, [custom_group_id.id])],
            })

    @api.model
    def cron_update_menu_access(self):
        logging.info(u"Update menu access")

        menu_setting =\
            self.env.ref("base.menu_administration")

        criteria_root = [
            ("parent_id", "=", False),
            ("id", "<>", menu_setting.id)
        ]
        root_menu_ids = self.search(criteria_root)

        for root_menu in root_menu_ids:
            context = {"ir.ui.menu.full_list": True}
            criteria_child = [
                ("id", "child_of", root_menu.id),
                ("id", "<>", root_menu.id),
                ("custom_group_id", "<>", False)
            ]
            menu_ids = self.with_context(
                context
            ).search(criteria_child)
            for menu in menu_ids:
                menu.set_menu_access()
