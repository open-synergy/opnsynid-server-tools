# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import datetime
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

    def _get_domain_states_filter(self, pholidays, start_dt, end_dt, employee_id=None):
        employee = False
        if employee_id:
            employee = self.env["hr.employee"].browse(employee_id)
        states_filter = [("year_id", "in", pholidays.ids)]
        if employee and employee.address_id and employee.address_id.state_id:
            states_filter += [
                "|",
                ("state_ids", "=", False),
                ("state_ids", "=", employee.address_id.state_id.id),
            ]
        else:
            states_filter.append(("state_ids", "=", False))
        states_filter.append(("date", ">=", start_dt))
        states_filter.append(("date", "<=", end_dt))
        return states_filter

    @api.model
    @api.returns("base.public.holiday.line")
    def get_holidays_list(
        self, year=None, start_dt=None, end_dt=None, employee_id=None
    ):
        if not start_dt and not end_dt:
            start_dt = datetime.date(year, 1, 1)
            end_dt = datetime.date(year, 12, 31)

        years = list(range(start_dt.year, end_dt.year + 1))
        holidays_filter = [("year", "in", years)]
        employee = False
        if employee_id:
            employee = self.env["hr.employee"].browse(employee_id)
            if employee.address_id and employee.address_id.country_id:
                holidays_filter.append("|")
                holidays_filter.append(("country_id", "=", False))
                holidays_filter.append(
                    ("country_id", "=", employee.address_id.country_id.id)
                )
            else:
                holidays_filter.append(("country_id", "=", False))
        pholidays = self.search(holidays_filter)
        if not pholidays:
            return self.env["base.public.holiday.line"]

        states_filter = self._get_domain_states_filter(
            pholidays, start_dt, end_dt, employee_id
        )
        hhplo = self.env["base.public.holiday.line"]
        holidays_lines = hhplo.search(states_filter)
        return holidays_lines

    @api.model
    def is_public_holiday(self, selected_date, employee_id=None):
        holidays_lines = self.get_holidays_list(
            year=selected_date.year, employee_id=employee_id
        )
        if holidays_lines:
            hol_date = holidays_lines.filtered(
                lambda r: r.date == fields.Date.from_string(selected_date)
            )
            if hol_date.ids:
                return True
        return False
