# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class UserGroupSection(models.Model):
    """
    Represents a named section under which application groups
    (ir.module.category) are bucketed on the user Access Rights tab.
    Applications whose category is not assigned to any section are shown
    separately in the "Other Groups" tab instead.
    """

    _name = "user_group_section"
    _inherit = ["mixin.master_data"]
    _description = "User Group Section"
    _order = "sequence, name"

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help=(
            "Determines the order in which this section, and the "
            "application groups assigned to it, appear on the user "
            "Access Rights tab. Lower values appear first."
        ),
    )
