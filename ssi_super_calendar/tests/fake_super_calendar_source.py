# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class FakeSuperCalendarSource(models.Model):
    """Fake source model used to exercise ``mixin.super_calendar_source``."""

    _name = "fake.super_calendar.source"
    _inherit = ["mixin.super_calendar_source"]
    _description = "Fake Super Calendar Source"
    _super_calendar_trigger_fields = ["date", "partner_ids"]

    name = fields.Char(string="Name")
    date = fields.Date(string="Date")
    note = fields.Char(string="Note")
    partner_ids = fields.Many2many(comodel_name="res.partner", string="Partners")

    def _get_super_calendar_values(self):
        """Describe the whole ``date`` as one busy day for the partners.

        :return: list with one value dict, or an empty list without date
        """
        self.ensure_one()
        if not self.date:
            return []
        start, end = self._super_calendar_date_range(self.date)
        return [
            {
                "name": self.name,
                "date_start": start,
                "date_end": end,
                "allday": True,
                "applies_to_all": False,
                "partner_ids": self.partner_ids.ids,
            }
        ]
