# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrModuleCategory(models.Model):
    _name = "ir.module.category"
    _inherit = ["ir.module.category"]

    section_id = fields.Many2one(
        string="User Group Section",
        comodel_name="user_group_section",
        help=(
            "Section under which this application's groups are grouped on "
            "the user Access Rights tab, ordered by the section's "
            "sequence. Leave empty to show this application's groups in "
            "the separate 'Other Groups' tab instead."
        ),
    )

    def write(self, values):
        res = super().write(values)
        if "section_id" in values:
            self.env["res.groups"]._update_user_groups_view()
        return res
