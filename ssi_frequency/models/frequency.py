# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).
import pytz
from dateutil.rrule import (
    DAILY,
    FR,
    MO,
    MONTHLY,
    SA,
    SU,
    TH,
    TU,
    WE,
    WEEKLY,
    YEARLY,
    rrule,
)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

WEEKDAYS = {
    "mo": MO,
    "tu": TU,
    "we": WE,
    "th": TH,
    "fr": FR,
    "sa": SA,
    "su": SU,
}
FREQUENCIES = {
    "yearly": YEARLY,
    "monthly": MONTHLY,
    "weekly": WEEKLY,
    "daily": DAILY,
}


class FrequencyRule(models.Model):
    _name = "frequency"
    _description = "Frequency Rule"
    _inherit = ["mixin.master_data"]

    interval = fields.Integer(
        string="Repeat Every",
        help="The number of intervals between events",
        default=1,
        required=True,
        tracking=True,
    )
    interval_type = fields.Selection(
        selection=[
            ("yearly", "Yearly"),
            ("monthly", "Monthly"),
            ("weekly", "Weekly"),
            ("daily", "Daily"),
        ],
        string="Interval Type",
        required=True,
        tracking=True,
    )
    is_exclusive = fields.Boolean(
        string="Exclusive Rule?",
        help="""Checking this box will make this an exclusive rule.
                Exclusive rules prevent the configured days
                from being a schedule option.""",
        default=False,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
    )
    use_bymonthday = fields.Boolean(
        string="Use Day of Month",
        help="""When selected you will be able to specify
                which calendar day of the month the event occurs on.""",
    )
    month_day = fields.Integer(
        string="Day of Month",
        tracking=True,
    )
    use_byweekday = fields.Boolean(
        string="Use Days of Week",
        help="""When selected you will be able to choose which days of the week
                the scheduler will include (or exclude if Exclusive rule).""",
    )
    mo = fields.Boolean(
        string="Monday",
        default=False,
    )
    tu = fields.Boolean(
        string="Tuesday",
        default=False,
    )
    we = fields.Boolean(
        string="Wednesday",
        default=False,
    )
    th = fields.Boolean(
        string="Thursday",
        default=False,
    )
    fr = fields.Boolean(
        string="Friday",
        default=False,
    )
    sa = fields.Boolean(
        string="Saturday",
        default=False,
    )
    su = fields.Boolean(
        string="Sunday",
        default=False,
    )
    use_bymonth = fields.Boolean(
        string="Use Months",
    )
    jan = fields.Boolean(
        string="January",
        default=False,
    )
    feb = fields.Boolean(
        string="February",
        default=False,
    )
    mar = fields.Boolean(
        string="March",
        default=False,
    )
    apr = fields.Boolean(
        string="April",
        default=False,
    )
    may = fields.Boolean(
        string="May",
        default=False,
    )
    jun = fields.Boolean(
        string="June",
        default=False,
    )
    jul = fields.Boolean(
        string="July",
        default=False,
    )
    aug = fields.Boolean(
        string="August",
        default=False,
    )
    sep = fields.Boolean(
        string="September",
        default=False,
    )
    oct = fields.Boolean(
        string="October",
        default=False,
    )
    nov = fields.Boolean(
        string="November",
        default=False,
    )
    des = fields.Boolean(
        string="December",
        default=False,
    )
    use_setpos = fields.Boolean(
        string="Use Position",
    )
    set_pos = fields.Integer(
        string="By Position",
        help="""Specify an occurrence number, positive or negative,
                corresponding to the nth occurrence of the rule inside the frequency period.
                For example, -1 if combined with a 'Monthly' frequency,
                and a weekday of (MO, TU, WE, TH, FR),
                will result in the last work day of every month.""",
    )

    @api.constrains(
        "set_pos",
    )
    def _check_set_pos(self):
        for document in self:
            if document.use_setpos:
                if not (-366 < document.set_pos < 366):
                    msgError = _("Position must be between -366 and 366")
                    raise UserError(msgError)

    @api.constrains(
        "month_day",
    )
    def _check_month_day(self):
        for document in self:
            if document.use_bymonthday:
                if not (1 <= document.month_day <= 31):
                    msgError = _("Day of Month must be between 1 and 31")
                    raise UserError(msgError)

    def _get_rrule(self, dtstart=None, until=None, tz=None):
        self.ensure_one()
        freq = FREQUENCIES[self.interval_type]
        # localize dtstart and until to user timezone
        tz = pytz.timezone(
            tz or self._context.get("tz", None) or self.env.user.tz or "UTC"
        )

        if dtstart:
            dtstart = pytz.timezone("UTC").localize(dtstart).astimezone(tz)
        if until:
            until = pytz.timezone("UTC").localize(until).astimezone(tz)
            # We force until in the starting timezone to avoid incoherent results
            until = tz.normalize(until.replace(tzinfo=dtstart.tzinfo))

        return (
            # Replace original timezone with current date timezone
            # without changing the time and force it back to UTC,
            # this will keep the same final time even in case of
            # daylight saving time change
            #
            # for instance recurring weekly
            # from 2022-03-21 15:00:00+01:00 to 2022-04-11 15:30:00+02:00
            # will give:
            #
            # utc naive -> datetime timezone aware
            # 2022-03-21 14:00:00 -> 2022-03-21 15:00:00+01:00
            # 2022-03-28 13:00:00 -> 2022-03-28 15:00:00+02:00
            date.replace(tzinfo=tz.normalize(date).tzinfo)
            .astimezone(pytz.UTC)
            .replace(tzinfo=None)
            for date in rrule(
                freq,
                interval=self.interval,
                dtstart=dtstart,
                until=until,
                byweekday=self._byweekday(),
                bymonth=self._bymonth(),
                bymonthday=self._bymonthday(),
                bysetpos=self._bysetpos(),
            )
        )

    def _byweekday(self):
        """
        Checks day of week booleans and builds the value for rrule parameter
        @returns: {list} byweekday: list of WEEKDAY values used for rrule
        """
        self.ensure_one()
        if not self.use_byweekday:
            return None
        weekdays = ["mo", "tu", "we", "th", "fr", "sa", "su"]
        byweekday = [WEEKDAYS[field] for field in weekdays if self[field]]
        return byweekday

    def _bymonth(self):
        """
        Checks month booleans and builds the value for rrule parameter
        @returns: {list} bymonth: list of integers used for rrule
        """
        self.ensure_one()
        if not self.use_bymonth:
            return None
        months = [
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
        ]
        bymonth = [months.index(field) + 1 for field in months if self[field]]
        return bymonth

    def _bymonthday(self):
        self.ensure_one()
        if not self.use_bymonthday:
            return None
        return self.month_day

    def _bysetpos(self):
        self.ensure_one()
        if not self.use_setpos or self.set_pos == 0:
            return None
        return self.set_pos
