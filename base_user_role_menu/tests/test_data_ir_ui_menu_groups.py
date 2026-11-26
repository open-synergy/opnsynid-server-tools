# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestDataIrUiMenuGroups(YamlTransactionCase):
    """Scenarios for menu group retention in base_user_role_menu."""

    def test_menu_groups_scenarios(self):
        """Run menu group retention scenarios from YAML.

        Covers plain writes and writes made during module data loading.
        """
        self.run_yaml_scenario("test_data_ir_ui_menu_groups.yaml")
