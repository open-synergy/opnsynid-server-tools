# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSsiCopyMoveUserFromGroup(YamlTransactionCase):
    def test_ssi_copy_move_user_from_group(self):
        self.run_yaml_scenario("test_data_ssi_copy_move_user_from_group.yaml")

    def test_copy_same_source_and_destination_raises_error(self):
        group = self.env["res.groups"].create({"name": "Test Same Group"})
        user = self.env["res.users"].create(
            {
                "name": "Test User Same Group",
                "login": "test_same_group@example.com",
                "groups_id": [(4, group.id)],
            }
        )
        group.write({"users": [(4, user.id)]})
        wizard = self.env["ssi_copy_move_user_from_group"].create(
            {
                "group_from_id": group.id,
                "group_to_id": group.id,
            }
        )
        with self.assertRaises(UserError):
            wizard.action_copy_users()

    def test_action_on_empty_source_group_raises_error(self):
        group_from = self.env["res.groups"].create({"name": "Test Empty Source"})
        group_to = self.env["res.groups"].create({"name": "Test Empty Destination"})
        wizard = self.env["ssi_copy_move_user_from_group"].create(
            {
                "group_from_id": group_from.id,
                "group_to_id": group_to.id,
            }
        )
        with self.assertRaises(UserError):
            wizard.action_copy_users()

    def test_move_between_conflicting_user_type_groups_raises_error(self):
        group_from = self.env["res.groups"].create({"name": "Test Portal Source"})
        portal_group = self.env.ref("base.group_portal")
        user = self.env["res.users"].create(
            {
                "name": "Test Portal User",
                "login": "test_portal_user@example.com",
                "groups_id": [(6, 0, [portal_group.id])],
            }
        )
        group_from.write({"users": [(4, user.id)]})
        internal_group = self.env.ref("base.group_user")
        wizard = self.env["ssi_copy_move_user_from_group"].create(
            {
                "group_from_id": group_from.id,
                "group_to_id": internal_group.id,
            }
        )
        with self.assertRaises(ValidationError):
            wizard.action_move_users()
