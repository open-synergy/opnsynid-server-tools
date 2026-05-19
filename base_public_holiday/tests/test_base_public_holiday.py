# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestBasePublicHoliday(YamlTransactionCase):
    def test_base_public_holiday(self):
        self.run_yaml_scenario("test_data_base_public_holiday.yaml")
