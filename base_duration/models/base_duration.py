# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, FR, MO, SA, SU, TH, TU, WE, rrule

from odoo import fields, models


class BaseDuration(models.Model):
    _name = "base.duration"
    _inherit = [
        "mixin.master_data",
    ]
    _description = "Base Duration"

    relative_delta_year = fields.Integer(
        string="Year",
        default=0,
    )
    relative_delta_month = fields.Integer(
        string="Month",
        default=0,
    )
    relative_delta_day = fields.Integer(
        string="Day",
        default=0,
    )
    relative_delta_years = fields.Integer(
        string="Years",
        default=0,
    )
    relative_delta_months = fields.Integer(
        string="Months",
        default=0,
    )
    relative_delta_weeks = fields.Integer(
        string="Weeks",
        default=0,
    )
    relative_delta_days = fields.Integer(
        string="Days",
        default=0,
    )
    relative_delta_weekday = fields.Integer(
        string="Weekday",
        default=0,
    )
    number_of_days = fields.Integer(
        string="Number of Days",
        required=True,
        default=0,
    )
    include_weekend = fields.Boolean(
        string="Include Weekend",
        default=False,
    )
    include_public_holiday = fields.Boolean(
        string="Include Public Holiday",
        default=True,
    )

    # flake8: noqa: C901
    def get_duration(self, date_value=False, country_id=False, state_id=False):
        def _get_rrule(dt_start, count, weekend):
            if weekend:
                byweekday = (MO, TU, WE, TH, FR, SA, SU)
            else:
                byweekday = (MO, TU, WE, TH, FR)
            return rrule(
                DAILY,
                dtstart=dt_start,
                byweekday=byweekday,
                count=count + 1,
            )

        self.ensure_one()
        date_value = date_value or fields.Date.context_today(self)
        # message_error = "%s %s" % (self.relative_delta_months, self.relative_delta_days)
        # raise UserError(message_error)
        params = {}
        if self.relative_delta_year:
            params["year"] = self.relative_delta_year
        if self.relative_delta_month:
            params["month"] = self.relative_delta_month
        if self.relative_delta_day:
            params["day"] = self.relative_delta_day
        if self.relative_delta_years:
            params["years"] = self.relative_delta_years
        if self.relative_delta_months:
            params["months"] = self.relative_delta_months
        if self.relative_delta_weeks:
            params["weeks"] = self.relative_delta_weeks
        if self.relative_delta_days:
            params["days"] = self.relative_delta_days
        if self.relative_delta_weekday:
            params["weekday"] = self.relative_delta_weekday
        if params:
            date_value = date_value + relativedelta(**params)
        result = fields.Date.from_string(date_value)

        if self.number_of_days > 0:
            dt_start = result
            count = self.number_of_days
            if self.include_weekend:
                weekend = True
            else:
                weekend = False

            rr_date = _get_rrule(dt_start, count, weekend)
            result = rr_date[-1].date()

            if self.include_public_holiday:
                obj_public_holiday = self.env["base.public.holiday"]
                for date in list(rr_date):
                    if obj_public_holiday.is_public_holiday(date):
                        count += 1
                rr_date = _get_rrule(dt_start, count, weekend)
                result = rr_date[-1].date()

        return result
