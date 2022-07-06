# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TestBaseDuration(models.Model):
    _name = "test.base_duration"
    _description = "Test Base Duration"

    name = fields.Char(
        string="# Document",
        default="/",
    )
    code = fields.Char(
        string="Code",
        default="000",
    )
    duration_id = fields.Many2one(
        string="Duration",
        comodel_name="base.duration",
    )
    date = fields.Date(
        string="Date",
    )
    date_result = fields.Date(
        string="Date Result",
    )
    note = fields.Text(
        string="Note",
    )

    @api.onchange(
        "duration_id",
        "date",
    )
    def onchange_date_result(self):
        if self.duration_id:
            self.date_result = self.duration_id.get_duration(self.date)
