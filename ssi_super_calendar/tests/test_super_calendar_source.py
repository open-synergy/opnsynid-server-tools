# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo_test_helper import FakeModelLoader
from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSuperCalendarSource(YamlTransactionCase):
    """Check ``mixin.super_calendar_source`` on a fake source model."""

    def setUp(self):
        """Register the fake source model and create two partners."""
        super().setUp()
        self.loader = FakeModelLoader(self.env, self.__module__)
        self.loader.backup_registry()
        from .fake_super_calendar_source import FakeSuperCalendarSource

        self.loader.update_registry((FakeSuperCalendarSource,))
        self.addCleanup(self.loader.restore_registry)
        self.partner_a = self.env["res.partner"].create({"name": "Source A"})
        self.partner_b = self.env["res.partner"].create({"name": "Source B"})

    def _rows(self, source):
        """Return the calendar rows of ``source``, inactive ones included.

        :param source: record of the fake source model
        :return: ``super_calendar`` recordset
        """
        return (
            self.env["super_calendar"]
            .with_context(active_test=False)
            .search([("res_model", "=", source._name), ("res_id", "=", source.id)])
        )

    def _create_source(self, partners):
        """Create a fake source record dated 2026-03-02.

        :param partners: ``res.partner`` recordset attached to it
        :return: the new fake source record
        """
        return self.env["fake.super_calendar.source"].create(
            {
                "name": "Source",
                "date": "2026-03-02",
                "partner_ids": [(6, 0, partners.ids)],
            }
        )

    def test_create_makes_a_row(self):
        """Assert creating a source creates its row with the right data.

        Pure Python - trigger P10 (L-09..L-11: the fake model must be
        registered in the registry with Python before any record exists).
        """
        source = self._create_source(self.partner_a | self.partner_b)
        rows = self._rows(source)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows.partner_count, 2)
        self.assertEqual(rows.partner_ids, self.partner_a | self.partner_b)
        self.assertEqual(rows.sudo().name, "Source")
        self.assertTrue(rows.allday)

    def test_write_trigger_field_replaces_row(self):
        """Assert writing a trigger field rebuilds the row.

        Pure Python - trigger P10 (L-09..L-11: the fake model must be
        registered in the registry with Python before any record exists).
        """
        source = self._create_source(self.partner_a)
        old_ids = self._rows(source).ids
        source.write({"partner_ids": [(6, 0, (self.partner_a | self.partner_b).ids)]})
        rows = self._rows(source)
        self.assertEqual(len(rows), 1)
        self.assertNotEqual(rows.ids, old_ids)
        self.assertEqual(rows.partner_count, 2)

    def test_write_other_field_keeps_row(self):
        """Assert writing a non-trigger field leaves the row untouched.

        Pure Python - trigger P10 (L-09..L-11: the fake model must be
        registered in the registry with Python before any record exists).
        """
        source = self._create_source(self.partner_a)
        old_ids = self._rows(source).ids
        source.write({"note": "changed"})
        self.assertEqual(self._rows(source).ids, old_ids)

    def test_unlink_removes_row(self):
        """Assert deleting the source deletes its rows.

        Pure Python - trigger P10 (L-09..L-11: the fake model must be
        registered in the registry with Python before any record exists).
        """
        source = self._create_source(self.partner_a)
        self.assertEqual(len(self._rows(source)), 1)
        rows_domain = [
            ("res_model", "=", source._name),
            ("res_id", "=", source.id),
        ]
        source.unlink()
        self.assertEqual(
            self.env["super_calendar"]
            .with_context(active_test=False)
            .search_count(rows_domain),
            0,
        )

    def test_refresh_rebuilds_row(self):
        """Assert the refresh action rebuilds a row that was removed.

        Pure Python - trigger P10 (L-09..L-11: the fake model must be
        registered in the registry with Python before any record exists).
        """
        source = self._create_source(self.partner_a)
        self._rows(source).unlink()
        self.assertFalse(self._rows(source))
        self.assertTrue(source.action_refresh_super_calendar())
        rows = self._rows(source)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows.partner_ids, self.partner_a)

    def test_date_range_uses_user_timezone(self):
        """Assert the day helper converts the user timezone to UTC.

        Pure Python - trigger P10 (L-09..L-11: the fake model must be
        registered in the registry with Python before any record exists).
        """
        self.env.user.tz = "Asia/Jakarta"
        source = self.env["fake.super_calendar.source"]
        start, end = source._super_calendar_date_range("2026-03-02")
        self.assertEqual(start, datetime(2026, 3, 1, 17, 0, 0))
        self.assertEqual(end, datetime(2026, 3, 2, 17, 0, 0))
        self.env.user.tz = False
        start, end = source._super_calendar_date_range("2026-03-02")
        self.assertEqual(start, datetime(2026, 3, 2, 0, 0, 0))
        self.assertEqual(end, datetime(2026, 3, 3, 0, 0, 0))
