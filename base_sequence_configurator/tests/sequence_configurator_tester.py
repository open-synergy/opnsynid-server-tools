# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SequenceConfigurationTester(models.Model):
    _name = "sequence.configuration.tester"
    _inherit = [
        "base.sequence_document",
    ]

    name = fields.Char(
        string="# Document",
        required=True,
    )

    @api.model
    def create(self, values):
        _super = super(SequenceConfigurationTester, self)
        result = _super.create(values)
        sequence = result._create_sequence()
        result.write({
            "name": sequence,
        })
        return result
