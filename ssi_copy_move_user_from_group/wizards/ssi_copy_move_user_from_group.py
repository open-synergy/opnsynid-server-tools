# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class WizardSsiCopyMoveUserFromGroup(models.TransientModel):
    """
    Wizard to copy or move all members of one res.groups record to another
    res.groups record, without touching any other group already assigned to
    the affected users.
    """

    _name = "ssi_copy_move_user_from_group"
    _description = "Copy/Move User From Group"

    group_from_id = fields.Many2one(
        string="Source Group",
        comodel_name="res.groups",
        required=True,
        help="Group whose members will be copied or moved. When opened from "
        "the Group form, this is pre-filled with the current group.",
    )
    group_to_id = fields.Many2one(
        string="Destination Group",
        comodel_name="res.groups",
        required=True,
        domain="[('id', '!=', group_from_id)]",
        help="Group that will receive the members of the source group.",
    )
    user_ids = fields.Many2many(
        string="Affected Users",
        comodel_name="res.users",
        related="group_from_id.users",
        readonly=True,
        help="Preview of the users currently in the source group that will "
        "be affected by the Copy or Move action.",
    )

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        if (
            self.env.context.get("active_model") == "res.groups"
            and self.env.context.get("active_id")
            and "group_from_id" in field_list
        ):
            res["group_from_id"] = self.env.context["active_id"]
        return res

    def _check_group_from_not_equal_group_to(self):
        self.ensure_one()
        if not self._check_group_from_not_equal_group_to_condition():
            error_message = """
Context: Copy/Move users between groups
Database ID: %s
Problem: Source group and destination group are the same
Solution: Select a different destination group
""" % (
                self.id,
            )
            raise UserError(error_message)

    def _check_group_from_not_equal_group_to_condition(self):
        self.ensure_one()
        return self.group_from_id != self.group_to_id

    def _check_group_from_has_users(self):
        self.ensure_one()
        if not self._check_group_from_has_users_condition():
            error_message = """
Context: Copy/Move users between groups
Database ID: %s
Problem: Source group has no members
Solution: Select a source group that has at least one member
""" % (
                self.id,
            )
            raise UserError(error_message)

    def _check_group_from_has_users_condition(self):
        self.ensure_one()
        return bool(self.group_from_id.users)

    def action_copy_users(self):
        for wizard in self.sudo():
            result = wizard._copy_users()
        return result

    def _copy_users(self):
        self.ensure_one()
        self._check_group_from_not_equal_group_to()
        self._check_group_from_has_users()
        self.group_to_id.write(
            {"users": [(4, user.id) for user in self.group_from_id.users]}
        )
        return {"type": "ir.actions.act_window_close"}

    def action_move_users(self):
        for wizard in self.sudo():
            result = wizard._move_users()
        return result

    def _move_users(self):
        self.ensure_one()
        self._check_group_from_not_equal_group_to()
        self._check_group_from_has_users()
        users = self.group_from_id.users
        self.group_to_id.write({"users": [(4, user.id) for user in users]})
        self.group_from_id.write({"users": [(3, user.id) for user in users]})
        return {"type": "ir.actions.act_window_close"}
