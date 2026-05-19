# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestTestBaseDuration(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestTestBaseDuration, self).setUp(*args, **kwargs)
        self.obj_duration = self.env["base.duration"]
        self.obj_test = self.env["test.base_duration"]

    def _create_duration(self, name, code, number_of_days):
        return self.obj_duration.create(
            {
                "name": name,
                "code": code,
                "number_of_days": number_of_days,
                "include_weekend": False,
                "include_public_holiday": False,
            }
        )

    def test_create_test_base_duration(self):
        """Test creating test.base_duration record."""
        duration = self._create_duration("Test 5 Days", "T5D", 5)
        record = self.obj_test.create(
            {
                "name": "Test Doc 001",
                "code": "TBD001",
                "duration_id": duration.id,
                "date": "2024-01-01",
            }
        )
        self.assertIsNotNone(record)
        self.assertEqual(record.duration_id.id, duration.id)

    def test_onchange_date_result(self):
        """Test that onchange_date_result computes date_result."""
        duration = self._create_duration("Test 3 Days", "T3D", 3)
        record = self.obj_test.new(
            {
                "name": "Test Doc 002",
                "code": "TBD002",
                "duration_id": duration.id,
                "date": "2024-01-01",
            }
        )
        record.onchange_date_result()
        self.assertIsNotNone(record.date_result)

    def test_get_duration_no_days(self):
        """Test get_duration when number_of_days is 0."""
        duration = self._create_duration("Zero Days", "ZD", 0)
        result = duration.get_duration(date_value="2024-03-15")
        self.assertIsNotNone(result)
