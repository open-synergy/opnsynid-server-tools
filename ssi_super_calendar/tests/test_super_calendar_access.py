# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSuperCalendarAccess(YamlTransactionCase):
    """Run the YAML scenarios for the access rights of ``super_calendar``."""

    def test_super_calendar_access(self):
        """Run the read-only access scenario for ``super_calendar``."""
        self.run_yaml_scenario("test_data_super_calendar_access.yaml")
