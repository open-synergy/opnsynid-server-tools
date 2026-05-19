# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestBaseUserCopyUserRole(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestBaseUserCopyUserRole, self).setUp(*args, **kwargs)
        self.obj_res_users = self.env["res.users"]
        self.obj_wizard = self.env["base.copy_user_role"]
        self.demo_user = self.env.ref("base.user_demo")

    def _prepare_user_data(self):
        return {
            "login": "test_copy_role@test.com",
            "name": "Test Copy Role User",
        }

    def test_copy_user_role(self):
        # Create a new user to be the target
        data = self._prepare_user_data()
        user = self.obj_res_users.create(data)
        self.assertIsNotNone(user)

        # Build context with active_ids pointing to the new user
        ctx = {"active_ids": user.ids}

        # Create wizard with source = demo_user
        wizard = self.obj_wizard.with_context(ctx).create(
            {"user_id": self.demo_user.id}
        )
        self.assertIsNotNone(wizard)

        # Execute copy role
        wizard.with_context(ctx).copy_role()

        # Verify role_line_ids were copied
        src_roles = set(self.demo_user.role_line_ids.mapped("role_id").ids)
        dest_roles = set(user.role_line_ids.mapped("role_id").ids)
        self.assertEqual(src_roles, dest_roles)
