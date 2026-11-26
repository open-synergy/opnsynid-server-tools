# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSuperCalendarMenu(YamlTransactionCase):
    """Check the Calendar app menu opens the Super Calendar."""

    def test_calendar_menu_opens_super_calendar(self):
        """Assert the Calendar menu is re-pointed and otherwise intact.

        Pure Python - trigger P1 (L-02: the check compares a Reference
        field value, which YAML cannot assert).
        """
        menu = self.env.ref("calendar.mail_menu_calendar")
        self.assertEqual(
            menu.action, self.env.ref("ssi_super_calendar.super_calendar_action")
        )
        self.assertFalse(menu.parent_id)
        self.assertIn(self.env.ref("base.group_user"), menu.groups_id)
        self.assertTrue(menu.web_icon.startswith("calendar,"))

    def test_old_technical_menu_is_removed(self):
        """Assert the old Technical menu is gone and the core action stays.

        Pure Python - trigger P1 (L-02: the check reads the result of
        ``env.ref`` with ``raise_if_not_found=False``, which YAML cannot
        assert).
        """
        self.assertIsNone(
            self.env.ref(
                "ssi_super_calendar.super_calendar_menu", raise_if_not_found=False
            )
        )
        self.assertTrue(self.env.ref("calendar.action_calendar_event"))
