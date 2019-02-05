# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from .common import setup_test_model
from odoo.exceptions import UserError
from .sequence_configurator_tester import SequenceConfigurationTester


@common.at_install(False)
@common.post_install(True)
class BaseSequenceConfigurationTest(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(BaseSequenceConfigurationTest, cls).setUpClass()

        setup_test_model(cls.env, [SequenceConfigurationTester])

        cls.test_model = cls.env[SequenceConfigurationTester._name]

        cls.tester_model = cls.env["ir.model"].search([
            ("model", "=", "sequence.configuration.tester")])

        # Access record:
        cls.env["ir.model.access"].create({
            "name": "sequence.configuration.tester",
            "model_id": cls.tester_model.id,
            "perm_read": 1,
            "perm_write": 1,
            "perm_create": 1,
            "perm_unlink": 1,
        })

        obj_field = cls.env["ir.model.fields"]
        sequence_field = obj_field.search([
            ("model_id", "=", cls.tester_model.id),
            ("name", "=", "name"),
        ])

        obj_sequence = cls.env["ir.sequence"]
        fallback_sequence = obj_sequence.create({
            "name": "Fallback Sequence",
            "prefix": "FALL/",
            "padding": 3,
        })

        test_sequence = obj_sequence.create({
            "name": "Test Sequence",
            "prefix": "TEST/",
            "padding": 3,
        })

        obj_config = cls.env["base.sequence_configurator"]
        cls.sequence_configurator = obj_config.create({
            "model_id": cls.tester_model.id,
            "active": True,
            "initial_string": "/",
            "sequence_field_id": sequence_field[0].id,
            "fallback_sequence_id": fallback_sequence.id,
        })

        obj_config_line = cls.env["base.sequence_configurator_line"]
        cls.line = obj_config_line.create({
            "generator_id": cls.sequence_configurator.id,
            "sequence": 1,
            "domain": "result = True",
            "sequence_computation_code": "result = %s" % (test_sequence.id)
        })

    def test_01_normal(self):
        test_data = self.test_model.create({
            "name": "/",
        })

        self.assertEqual(
            test_data.name,
            "TEST/001",
        )

    def test_02_overide_sequence_field(self):
        test_data = self.test_model.create({
            "name": "Weks",
        })

        self.assertEqual(
            test_data.name,
            "Weks",
        )

    def test_03_no_configuration_line(self):
        self.line.unlink()
        test_data = self.test_model.create({
            "name": "/",
        })

        self.assertEqual(
            test_data.name,
            "FALL/001",
        )

    def test_04_error_configuration_line(self):
        self.line.write({
            "sequence_computation_code": "result = ab",
        })

        with self.assertRaises(UserError):
            self.test_model.create({
                "name": "/",
            })

    def test_05_configuration_line_not_found(self):
        self.line.write({
            "domain": "result = False",
        })
        test_data = self.test_model.create({
            "name": "/",
        })

        self.assertEqual(
            test_data.name,
            "FALL/002",
        )

    def test_06_no_configuration(self):
        self.sequence_configurator.unlink()
        with self.assertRaises(UserError):
            self.test_model.create({
                "name": "/",
            })
