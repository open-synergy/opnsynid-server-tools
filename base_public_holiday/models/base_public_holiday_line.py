# -*- coding: utf-8 -*-
# Copyright 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# Copyright 2014 initOS GmbH & Co. KG <http://www.initos.com>
# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
from openerp.exceptions import Warning as UserError


class BasePublicHolidayLine(models.Model):
    _name = "base.public.holiday.line"
    _description = "Public Holidays Lines"
    _order = "date, name desc"

    name = fields.Char(
        string="Name",
        required=True,
    )
    date = fields.Date(
        string="Date",
        required=True
    )
    year_id = fields.Many2one(
        string="Calendar Year",
        comodel_name="base.public.holiday",
        required=True,
    )
    variable = fields.Boolean(
        string="Date may change",
    )
    state_ids = fields.Many2many(
        string="Related States",
        comodel_name="res.country.state",
        realation="base_public_holiday_state_rel",
        column1="line_id",
        column2="state_id",
    )

    @api.multi
    @api.constrains(
        "date",
        "state_ids",
    )
    def _check_date_state(self):
        self.ensure_one()
        if fields.Date.from_string(self.date).year != self.year_id.year:
            raise UserError(
                "Dates of holidays should be the same year "
                "as the calendar year they are being assigned to"
            )
        if self.state_ids:
            domain = [
                ("date", "=", self.date),
                ("year_id", "=", self.year_id.id),
                ("state_ids", "!=", False),
                ("id", "!=", self.id),
            ]
            holidays = self.search(domain)
            for holiday in holidays:
                if self.state_ids & holiday.state_ids:
                    raise UserError("You can\"t create duplicate public "
                                    "holiday per date %s and one of the "
                                    "country states." % self.date)
        domain = [
            ("date", "=", self.date),
            ("year_id", "=", self.year_id.id),
            ("state_ids", "=", False),
        ]
        if self.search_count(domain) > 1:
            raise UserError("You can\"t create duplicate public holiday "
                            "per date %s." % self.date)
        return True
