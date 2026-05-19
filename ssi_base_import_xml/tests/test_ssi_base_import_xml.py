# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSsiBaseImportXml(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestSsiBaseImportXml, self).setUp(*args, **kwargs)
        self.obj_wizard = self.env["base_import_xml"]

    def _encode_xml(self, xml_str):
        return base64.b64encode(xml_str.encode("utf-8")).decode("utf-8")

    def test_import_create_partner(self):
        """Test importing a new partner record via XML."""
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <record id="test_partner_xml_001" model="res.partner">
            <field name="name">Test XML Import Partner</field>
        </record>
    </data>
</odoo>"""
        wizard = self.obj_wizard.create(
            {
                "model_name": "res.partner",
                "file_data": self._encode_xml(xml_content),
                "file_name": "test_import.xml",
            }
        )
        wizard.action_import()
        self.assertIn("Created: 1", wizard.error_message)

    def test_import_update_existing_partner(self):
        """Test importing XML that updates an existing record."""
        xml_create = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <record id="test_upd_partner_001" model="res.partner">
            <field name="name">Original Name</field>
        </record>
    </data>
</odoo>"""
        wizard = self.obj_wizard.create(
            {
                "model_name": "res.partner",
                "file_data": self._encode_xml(xml_create),
                "file_name": "test_create.xml",
            }
        )
        wizard.action_import()
        self.assertIn("Created: 1", wizard.error_message)

        # Now update via same xml_id
        xml_update = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <record id="test_upd_partner_001" model="res.partner">
            <field name="name">Updated Name</field>
        </record>
    </data>
</odoo>"""
        wizard2 = self.obj_wizard.create(
            {
                "model_name": "res.partner",
                "file_data": self._encode_xml(xml_update),
                "file_name": "test_update.xml",
            }
        )
        wizard2.action_import()
        self.assertIn("Updated: 1", wizard2.error_message)

    def test_import_invalid_xml(self):
        """Test importing malformed XML returns error message."""
        invalid_xml = "this is not xml at all"
        wizard = self.obj_wizard.create(
            {
                "model_name": "res.partner",
                "file_data": self._encode_xml(invalid_xml),
                "file_name": "invalid.xml",
            }
        )
        wizard.action_import()
        self.assertIn("Error parsing XML", wizard.error_message)

    def test_import_without_model_name(self):
        """Test importing without model_name returns error."""
        xml_content = """<?xml version="1.0" encoding="utf-8"?>
<odoo><data></data></odoo>"""
        wizard = self.obj_wizard.create(
            {
                "file_data": self._encode_xml(xml_content),
                "file_name": "test.xml",
            }
        )
        wizard.action_import()
        self.assertIn("unknown", wizard.error_message)
