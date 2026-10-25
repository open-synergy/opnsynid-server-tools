# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged

from .common import create_calendar_row, hour


@tagged("post_install", "-at_install")
class TestSuperCalendarAvailability(YamlTransactionCase):
    """Check ``super_calendar.check_availability``."""

    def setUp(self):
        """Create two partners and one busy period 10:00-12:00 for the first."""
        super().setUp()
        self.partner_a = self.env["res.partner"].create({"name": "Avail A"})
        self.partner_b = self.env["res.partner"].create({"name": "Avail B"})
        self.row = create_calendar_row(
            self.env,
            "res.partner",
            self.partner_a.id,
            hour(10),
            hour(12),
            partner_ids=[self.partner_a.id],
        )

    def _check(self, start, end, partners, exclude_refs=None):
        """Call ``check_availability`` with hours on the fixed day.

        :param start: start hour
        :param end: end hour
        :param partners: ``res.partner`` recordset to check
        :param exclude_refs: optional ``(res_model, res_id)`` list
        :return: the list returned by ``check_availability``
        """
        return self.env["super_calendar"].check_availability(
            hour(start), hour(end), partners.ids, exclude_refs=exclude_refs
        )

    def test_partial_overlap_conflicts(self):
        """Assert a partial overlap returns one entry for the partner.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        list returned by the method).
        """
        result = self._check(11, 13, self.partner_a)
        self.assertEqual(len(result), 1)
        entry = result[0]
        self.assertEqual(entry["partner_id"], self.partner_a.id)
        self.assertEqual(entry["calendar_id"], self.row.id)
        self.assertEqual(entry["label"], "Busy")
        self.assertEqual(entry["res_model"], "res.partner")
        self.assertEqual(entry["res_id"], self.partner_a.id)
        self.assertEqual(entry["date_start"], hour(10))
        self.assertEqual(entry["date_end"], hour(12))

    def test_touching_periods_do_not_conflict(self):
        """Assert a period ending at the start of another does not conflict.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        list returned by the method).
        """
        self.assertEqual(self._check(12, 14, self.partner_a), [])
        self.assertEqual(self._check(8, 10, self.partner_a), [])

    def test_partner_without_intersection_is_free(self):
        """Assert a partner absent from the row has no conflict.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        list returned by the method).
        """
        self.assertEqual(self._check(9, 13, self.partner_b), [])

    def test_empty_partner_list_returns_nothing(self):
        """Assert an empty partner list returns an empty list.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        list returned by the method).
        """
        self.assertEqual(self._check(9, 13, self.env["res.partner"]), [])

    def test_applies_to_all_conflicts_for_any_partner(self):
        """Assert a row that applies to everyone conflicts for each partner.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        list returned by the method).
        """
        holiday = create_calendar_row(
            self.env,
            "res.partner",
            self.partner_b.id,
            hour(14),
            hour(16),
            name="Holiday",
            applies_to_all=True,
        )
        result = self._check(15, 17, self.partner_a | self.partner_b)
        self.assertEqual(len(result), 2)
        self.assertEqual(
            {e["partner_id"] for e in result}, {self.partner_a.id, self.partner_b.id}
        )
        self.assertEqual({e["calendar_id"] for e in result}, {holiday.id})

    def test_exclude_refs_ignores_own_source(self):
        """Assert ``exclude_refs`` removes the rows of the given source.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        list returned by the method).
        """
        result = self._check(
            9,
            13,
            self.partner_a,
            exclude_refs=[("res.partner", self.partner_a.id)],
        )
        self.assertEqual(result, [])

    def test_inactive_rows_are_ignored(self):
        """Assert an archived row does not conflict.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        list returned by the method).
        """
        self.row.active = False
        self.assertEqual(self._check(9, 13, self.partner_a), [])
