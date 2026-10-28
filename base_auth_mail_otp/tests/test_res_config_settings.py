# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestResConfigSettings(YamlTransactionCase):
    """Scenario tests for the Email OTP Settings and user exemption."""

    def test_res_config_settings(self):
        """Run the Settings form, validation and access scenarios."""
        self.run_yaml_scenario("test_data_res_config_settings.yaml")
