# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BasePublicHolidayLine(models.Model):
    _name = "base.public.holiday.line"
    _description = "Public Holidays Lines"
    _order = "date, name desc"

    name = fields.Char(
        string="Name",
        required=True,
    )
    date = fields.Date(string="Date", required=True)
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
        column1="line_id",
        column2="state_id",
    )

    @api.constrains(
        "date",
        "year_id",
    )
    def _check_date_header(self):
        for document in self:
            if fields.Date.from_string(document.date).year != document.year_id.year:
                msg_err = _(
                    "Dates of holidays should be the same year "
                    "as the calendar year they are being assigned to"
                )
                raise UserError(msg_err)

    @api.constrains(
        "date",
        "year_id",
        "state_ids",
    )
    def _check_date_line_no_state(self):
        for document in self:
            domain = [
                ("date", "=", document.date),
                ("year_id", "=", document.year_id.id),
                ("state_ids", "=", False),
            ]
            if self.search_count(domain) > 1:
                msg_err = _(
                    'You can"t create duplicate public holiday ' "per date %s."
                ) % (document.date)
                raise UserError(msg_err)

    @api.constrains(
        "date",
        "year_id",
        "state_ids",
    )
    def _check_date_line_with_state(self):
        for document in self:
            domain = [
                ("date", "=", document.date),
                ("year_id", "=", document.year_id.id),
                ("state_ids", "!=", False),
                ("id", "!=", document.id),
            ]
            holidays = self.search(domain)
            for holiday in holidays:
                if document.state_ids & holiday.state_ids:
                    msg_err = _(
                        'You can"t create duplicate public '
                        "holiday per date %s and one of the "
                        "country states."
                    ) % (document.date)
                    raise UserError(msg_err)
