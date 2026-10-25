# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# HttpSavepointCase - NOT HttpCase. On 14.0 only the savepoint variant
# provides ``cls.env`` in ``setUpClass``.
from odoo.tests import HttpSavepointCase, tagged

from .common import create_calendar_row, hour


@tagged("post_install", "-at_install")
class TestUiSuperCalendar(HttpSavepointCase):
    """Tour tests for the ``super_calendar`` work instructions."""

    @classmethod
    def setUpClass(cls):
        """Create one personal period and one that applies to everyone."""
        super().setUpClass()
        # IK Pre-Condition is prepared here, NOT by clicking through the UI.
        cls.partner = cls.env["res.partner"].create({"name": "Tour Calendar Partner"})
        create_calendar_row(
            cls.env,
            "res.partner",
            cls.partner.id,
            hour(10),
            hour(12),
            partner_ids=[cls.partner.id],
            name="Tour Personal Leave",
        )
        create_calendar_row(
            cls.env,
            "res.partner",
            cls.partner.id,
            hour(14),
            hour(16),
            name="Tour Public Holiday",
            applies_to_all=True,
        )

    def test_view_availability(self):
        """Run the view availability tour for ``super_calendar``.

        IK: docs/super_calendar/01-view-availability.md
        """
        self.start_tour(
            "/web?debug=1",
            "ssi_super_calendar_super_calendar_view_availability",
            login="admin",
        )
