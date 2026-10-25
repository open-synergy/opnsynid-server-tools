# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged
from odoo.tests.common import new_test_user

from .common import create_calendar_row, hour


@tagged("post_install", "-at_install")
class TestSuperCalendarPrivacy(YamlTransactionCase):
    """Check that the label depends on the right to read the source."""

    def setUp(self):
        """Create an internal user and one row per kind of source.

        The ``res.partner`` source is readable by internal users; the
        ``ir.config_parameter`` source has no access right for them.
        """
        super().setUp()
        self.user = new_test_user(self.env, "sc_internal", groups="base.group_user")
        self.admin = self.env.ref("base.user_admin")
        self.partner = self.env["res.partner"].create({"name": "Privacy P"})
        param = self.env["ir.config_parameter"].search([], limit=1)
        self.row_open = create_calendar_row(
            self.env,
            "res.partner",
            self.partner.id,
            hour(10),
            hour(12),
            partner_ids=[self.partner.id],
            name="Open Meeting",
        )
        self.row_secret = create_calendar_row(
            self.env,
            "ir.config_parameter",
            param.id,
            hour(10),
            hour(12),
            partner_ids=[self.partner.id],
            name="Secret Meeting",
        )

    def test_display_name_follows_source_access(self):
        """Assert the display name is hidden without source access.

        Pure Python - trigger P1 (L-01: ``name_get`` and the display name
        are return values, which the ``call`` action discards).
        """
        as_user = self.env["super_calendar"].with_user(self.user)
        self.assertEqual(as_user.browse(self.row_open.id).display_name, "Open Meeting")
        self.assertEqual(
            as_user.browse(self.row_secret.id).display_name, "Not available"
        )
        as_admin = self.env["super_calendar"].with_user(self.admin)
        self.assertEqual(
            as_admin.browse(self.row_secret.id).display_name, "Secret Meeting"
        )

    def test_check_availability_same_count_for_every_user(self):
        """Assert the conflicts found do not depend on the caller's rights.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        list returned by the method).
        """
        args = (hour(9), hour(13), [self.partner.id])
        by_admin = (
            self.env["super_calendar"].with_user(self.admin).check_availability(*args)
        )
        by_user = (
            self.env["super_calendar"].with_user(self.user).check_availability(*args)
        )
        self.assertEqual(len(by_admin), 2)
        self.assertEqual(len(by_user), len(by_admin))
        hidden = [e for e in by_user if e["calendar_id"] == self.row_secret.id]
        self.assertEqual(len(hidden), 1)
        self.assertEqual(hidden[0]["label"], "Not available")
        self.assertFalse(hidden[0]["res_model"])
        self.assertFalse(hidden[0]["res_id"])
        self.assertEqual(hidden[0]["partner_id"], self.partner.id)
        self.assertEqual(hidden[0]["date_start"], hour(10))
        self.assertEqual(hidden[0]["date_end"], hour(12))
        shown = [e for e in by_user if e["calendar_id"] == self.row_open.id]
        self.assertEqual(shown[0]["label"], "Open Meeting")
        self.assertEqual(shown[0]["res_model"], "res.partner")
        secret_admin = [e for e in by_admin if e["calendar_id"] == self.row_secret.id]
        self.assertEqual(secret_admin[0]["label"], "Secret Meeting")
