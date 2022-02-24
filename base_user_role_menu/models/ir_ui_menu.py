# Copyright 2022 PT. Simetri Sinergi Indonesia
# Copyright 2022 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrUiMenu(models.Model):
    _inherit = "ir.ui.menu"

    def _clear_non_role_groups(self):
        self.ensure_one()
        application = self.env.ref("base_user_role.ir_module_category_role")
        to_be_preserve_ids = self.groups_id.filtered(
            lambda r: r.category_id.id == application.id
        ).ids
        self.write({"groups_id": [(6, 0, to_be_preserve_ids)]})

    def write(self, values):
        _super = super(IrUiMenu, self)
        result = _super.write(values)

        remove_non_role_groups = self._context.get("remove_non_role_groups", True)
        if remove_non_role_groups:
            context = {"remove_non_role_groups": False}
            for menu in self:
                menu.with_context(context)._clear_non_role_groups()

        return result
