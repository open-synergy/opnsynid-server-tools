# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader
from odoo_yaml_test import YamlTransactionCase

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import new_test_user

from .common import create_calendar_row, hour


@tagged("post_install", "-at_install")
class TestSuperCalendarSourceRef(YamlTransactionCase):
    """Check ``source_ref`` and the action that opens the source."""

    def setUp(self):
        """Create an internal user and one row per kind of source.

        The ``res.partner`` source is readable by internal users; the
        ``ir.config_parameter`` source has no access right for them.
        """
        super().setUp()
        self.user = new_test_user(self.env, "sc_ref_internal", groups="base.group_user")
        self.admin = self.env.ref("base.user_admin")
        self.partner = self.env["res.partner"].create({"name": "Ref P"})
        self.param = self.env["ir.config_parameter"].search([], limit=1)
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
            self.param.id,
            hour(10),
            hour(12),
            partner_ids=[self.partner.id],
            name="Secret Meeting",
        )

    def _as_user(self, row):
        """Return ``row`` browsed with the internal user.

        :param row: ``super_calendar`` record
        :return: the same row with the internal user environment
        """
        return self.env["super_calendar"].with_user(self.user).browse(row.id)

    def test_source_ref_follows_source_access(self):
        """Assert ``source_ref`` is filled only for a readable source.

        Pure Python - trigger P1 (L-01: ``source_ref`` is computed per
        user and the value is read back as a record, not asserted by a
        ``call`` action).
        """
        self.assertEqual(self._as_user(self.row_open).source_ref, self.partner)
        self.assertFalse(self._as_user(self.row_secret).source_ref)
        as_admin = self.env["super_calendar"].with_user(self.admin)
        self.assertEqual(as_admin.browse(self.row_secret.id).source_ref, self.param)
        self.assertEqual(as_admin.browse(self.row_open.id).source_ref, self.partner)

    def test_action_open_source_document(self):
        """Assert the action returns the form of the source document.

        Pure Python - trigger P1 (L-01: the dict returned by the action
        is discarded by the ``call`` action).
        """
        action = self._as_user(self.row_open).action_open_source_document()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "res.partner")
        self.assertEqual(action["res_id"], self.partner.id)
        self.assertEqual(action["target"], "current")

    def test_action_open_source_document_not_readable(self):
        """Assert the action fails when the source is not readable.

        Pure Python - trigger P1 (L-01: the exception message is checked
        together with the state of the record).
        """
        with self.assertRaises(UserError):
            self._as_user(self.row_secret).action_open_source_document()


@tagged("post_install", "-at_install")
class TestSuperCalendarSyncAsInternalUser(YamlTransactionCase):
    """Check the mixin synchronisation run by a non-admin internal user."""

    def setUp(self):
        """Register the fake source model and give it CRUD to users.

        The access rights on the fake model are granted to
        ``base.group_user`` so that an internal user can create, write
        and delete source records.
        """
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()
        from .fake_super_calendar_source import FakeSuperCalendarSource

        self.loader.update_registry((FakeSuperCalendarSource,))
        self.addCleanup(self._restore_registry)
        model = self.env["ir.model"].search(
            [("model", "=", "fake.super_calendar.source")]
        )
        self.env["ir.model.access"].create(
            {
                "name": "fake super calendar source - users",
                "model_id": model.id,
                "group_id": self.env.ref("base.group_user").id,
                "perm_read": True,
                "perm_write": True,
                "perm_create": True,
                "perm_unlink": True,
            }
        )
        self.user = new_test_user(
            self.env, "sc_sync_internal", groups="base.group_user"
        )
        self.partner = self.env["res.partner"].create({"name": "Sync P"})

    def _restore_registry(self):
        """Flush pending recomputations, then restore the registry."""
        self.env["base"].flush()
        self.loader.restore_registry()

    def _rows(self, source):
        """Return the calendar rows of ``source``, read as superuser.

        :param source: record of the fake source model
        :return: ``super_calendar`` recordset
        """
        return (
            self.env["super_calendar"]
            .sudo()
            .with_context(active_test=False)
            .search([("res_model", "=", source._name), ("res_id", "=", source.id)])
        )

    def test_sync_as_internal_user(self):
        """Assert create, write, refresh and unlink work for a user.

        Pure Python - trigger P10 (L-09..L-11: the fake model must be
        registered in the registry with Python before any record exists).
        """
        model = self.env["fake.super_calendar.source"].with_user(self.user)
        source = model.create(
            {
                "name": "Source",
                "date": "2026-03-02",
                "partner_ids": [(6, 0, self.partner.ids)],
            }
        )
        self.assertEqual(len(self._rows(source)), 1)
        old_ids = self._rows(source).ids
        source.write({"date": "2026-03-03"})
        self.assertEqual(len(self._rows(source)), 1)
        self.assertNotEqual(self._rows(source).ids, old_ids)
        self._rows(source).unlink()
        self.assertTrue(source.action_refresh_super_calendar())
        self.assertEqual(len(self._rows(source)), 1)
        source_id = source.id
        source.unlink()
        self.assertEqual(
            self.env["super_calendar"]
            .sudo()
            .with_context(active_test=False)
            .search_count(
                [
                    ("res_model", "=", "fake.super_calendar.source"),
                    ("res_id", "=", source_id),
                ]
            ),
            0,
        )
