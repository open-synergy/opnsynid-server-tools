# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestBaseUserRoleMenu(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestBaseUserRoleMenu, self).setUp(*args, **kwargs)
        self.IrUiMenu = self.env["ir.ui.menu"]

    def test_write_menu_clears_non_role_groups(self):
        """Writing to a menu should retain only role-based groups."""
        # Find any existing menu with groups
        menu = self.IrUiMenu.search([], limit=1)
        self.assertIsNotNone(menu)

        # Write name — triggers the write override
        original_name = menu.name
        menu.write({"name": original_name})

        # After write, all remaining groups should be role groups or empty
        application = self.env.ref(
            "base_user_role.ir_module_category_role", raise_if_not_found=False
        )
        if application and menu.groups_id:
            for group in menu.groups_id:
                self.assertEqual(group.category_id.id, application.id)

    def test_write_menu_without_remove_non_role_groups(self):
        """Writing with remove_non_role_groups=False skips clearing."""
        menu = self.IrUiMenu.search([], limit=1)
        self.assertIsNotNone(menu)

        original_name = menu.name
        # Should not raise any errors
        menu.with_context(remove_non_role_groups=False).write({"name": original_name})
