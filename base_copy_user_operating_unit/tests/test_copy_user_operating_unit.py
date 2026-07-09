# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree
from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestCopyUserOperatingUnit(YamlTransactionCase):
    def test_copy_user_operating_unit(self):
        self.run_yaml_scenario("test_data_copy_user_operating_unit.yaml")

    def test_fields_view_get_domain(self):
        obj_user = self.env["res.users"]
        obj_wizard = self.env["base.copy_user_operating_unit"]

        target = obj_user.create(
            {
                "login": "test_ou_fields_view_get@test.com",
                "name": "Target Fields View Get",
            }
        )

        wizard = obj_wizard.with_context(active_ids=target.ids).create(
            {"user_id": self.env.ref("base.user_demo").id}
        )

        view = wizard.with_context(active_ids=target.ids).fields_view_get()

        doc = etree.XML(view["arch"])
        for node in doc.xpath("//field[@name='user_id']"):
            domain = node.get("domain")
            expected_domain = "[('id', 'not in', " + str(target.ids) + ")]"
            self.assertEqual(domain, expected_domain)
