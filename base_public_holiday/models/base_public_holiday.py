# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BasePublicHoliday(models.Model):
    _name = "base.public.holiday"
    _description = "Public Holidays"
    _rec_name = "year"
    _order = "year"

    display_name = fields.Char(
        string="Name",
        compute="_compute_display_name",
        readonly=True,
        store=True,
    )
    year = fields.Integer(
        string="Calendar Year",
        required=True,
        default=date.today().year,
    )
    line_ids = fields.One2many(
        string="Holiday Dates",
        comodel_name="base.public.holiday.line",
        inverse_name="year_id",
    )
    country_id = fields.Many2one(
        string="Country",
        comodel_name="res.country",
    )

    @api.constrains(
        "year",
        "country_id",
    )
    def _check_year(self):
        self.ensure_one()
        if self.country_id:
            domain = [
                ("year", "=", self.year),
                ("country_id", "=", self.country_id.id),
                ("id", "!=", self.id),
            ]
        else:
            domain = [
                ("year", "=", self.year),
                ("country_id", "=", False),
                ("id", "!=", self.id),
            ]
        if self.search_count(domain):
            msg_err = _(
                "You can't create duplicate public holiday " "per year and/or country"
            )
            raise UserError(msg_err)
        return True

    @api.depends(
        "year",
        "country_id",
    )
    def _compute_display_name(self):
        self.ensure_one()
        if self.country_id:
            self.display_name = "%s (%s)" % (self.year, self.country_id.name)
        else:
            self.display_name = self.year

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.display_name))
        return result

    @api.model
    @api.returns("base.public.holiday.line")
    def get_holidays_list(self, year, country_id=None, state_id=None):
        holidays_filter = [
            ("year", "=", year),
        ]
        if country_id:
            holidays_filter.append(("country_id", "=", country_id))
        else:
            holidays_filter.append(("country_id", "=", False))

        pholidays = self.search(holidays_filter)
        if not pholidays:
            return list()

        states_filter = [
            ("year_id", "in", pholidays.ids),
        ]
        if state_id:
            states_filter += [
                "|",
                ("state_ids", "=", False),
                ("state_ids", "=", state_id),
            ]
        else:
            states_filter.append(("state_ids", "=", False))

        hhplo = self.env["base.public.holiday.line"]
        holidays_lines = hhplo.search(states_filter)
        return holidays_lines

    @api.model
    def is_public_holiday(self, selected_date, country_id=None, state_id=None):
        holidays_lines = self.get_holidays_list(
            selected_date.year, country_id=country_id, state_id=state_id
        )
        if holidays_lines and len(
            holidays_lines.filtered(
                lambda r: r.date == fields.Date.from_string(selected_date)
            )
        ):
            return True
        return False
