# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import base64
import logging
import re
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

_logger = logging.getLogger(__name__)
try:
    from icalendar import Calendar
except ImportError:
    _logger.debug("icalendar library missing. Install it via 'pip install icalendar'")


class HrPublicHolidaysImportIcs(models.TransientModel):
    _name = "base_public_holidays.import_ics_wizard"
    _description = "Import ICS"

    ics_file = fields.Binary(string="Selected file", required=True)
    ics_file_name = fields.Char(
        string="File Name",
    )

    def import_ics(self):
        ics = base64.b64decode(self.ics_file)
        lines = []
        for event in Calendar.from_ical(ics).walk("vevent"):
            dtend = event.get("dtend").dt
            dtstart = event.get("dtstart").dt
            day_count = (dtend - dtstart).days
            if day_count > 1:
                for dt in (dtstart + timedelta(n) for n in range(day_count)):
                    extra = {
                        "name": event.get("summary"),
                        "date": dt.strftime(DF),
                    }
                    lines.extend([(0, 0, extra)])
            else:
                extra = {
                    "name": event.get("summary"),
                    "date": dtstart.strftime(DF),
                }
                lines.extend([(0, 0, extra)])
        if lines:
            holidays = self.env["base.public.holiday"].browse(
                self._context.get("active_id", [])
            )
            holidays.write({"line_ids": lines})

    @api.onchange(
        "ics_file_name",
    )
    def _onchange_ics_file_name(self):
        if self.ics_file_name:
            if not re.match(r".*\.ics$", self.ics_file_name):
                msg_err = _("Please select *.ics file")
                raise UserError(msg_err)
