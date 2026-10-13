# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).
from datetime import date, datetime, time

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
from odoo.exceptions import UserError, ValidationError

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
    """Recurrence rule built on top of ``dateutil.rrule``.

    Each record describes one repeating pattern (interval, weekdays,
    day of month, months and occurrence position). ``_get_rrule``
    turns it into a lazy series of dates.
    """

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

    @api.constrains("interval")
    def _check_interval(self):
        """Reject a non-positive ``interval``.

        A zero interval makes ``rrule`` repeat the same date forever.

        :raises ValidationError: if ``interval`` is lower than 1
        """
        for document in self:
            if document.interval < 1:
                msg_error = _("Repeat Every must be at least 1")
                raise ValidationError(msg_error)

    @api.constrains("use_setpos", "set_pos")
    def _check_set_pos(self):
        """Validate the range of ``set_pos`` when position is used.

        :raises ValidationError: if ``use_setpos`` is set and
            ``set_pos`` is not between -366 and 366 (exclusive)
        """
        for document in self:
            if document.use_setpos:
                if not (-366 < document.set_pos < 366):
                    msg_error = _("Position must be between -366 and 366")
                    raise ValidationError(msg_error)

    @api.constrains("use_bymonthday", "month_day")
    def _check_month_day(self):
        """Validate the range of ``month_day`` when day of month is used.

        :raises ValidationError: if ``use_bymonthday`` is set and
            ``month_day`` is not between 1 and 31
        """
        for document in self:
            if document.use_bymonthday:
                if not (1 <= document.month_day <= 31):
                    msg_error = _("Day of Month must be between 1 and 31")
                    raise ValidationError(msg_error)

    @api.model
    def _normalize_boundary(self, value, end_of_day=False):
        """Convert a ``date`` or ``datetime`` into a naive datetime.

        A plain ``date`` becomes 00:00:00, or 23:59:59.999999 when
        ``end_of_day`` is true, so that an ``until`` date is inclusive
        for the whole day. A ``datetime`` is returned unchanged.

        :param value: ``date`` or ``datetime`` (naive, UTC)
        :param end_of_day: use the last instant of the day for a date
        :return: a ``datetime`` (naive, UTC)
        """
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, time.max if end_of_day else time.min)
        return value

    def _get_rrule(self, dtstart=None, until=None, tz=None):
        """Build the series of dates generated by this rule.

        ``dtstart`` and ``until`` may be naive UTC ``datetime`` values
        or ``date`` values. A ``dtstart`` date means 00:00:00 and an
        ``until`` date means 23:59:59.999999 (inclusive for that day).
        Results are computed in timezone ``tz`` (defaults to the
        context ``tz``, the user ``tz``, then UTC) and converted back
        to naive UTC, so local time is kept across daylight saving
        changes.

        :param dtstart: first possible date (required)
        :param until: last possible date; without it the series never
            ends
        :param tz: timezone name used to compute the series
        :return: a one-shot generator of naive UTC ``datetime`` values
        :raises UserError: if ``dtstart`` is empty (raised on call, not
            on iteration)
        """
        self.ensure_one()
        if not dtstart:
            msg_error = _("Start date is required to compute a frequency")
            raise UserError(msg_error)
        freq = FREQUENCIES[self.interval_type]
        # localize dtstart and until to user timezone
        tz = pytz.timezone(
            tz or self._context.get("tz", None) or self.env.user.tz or "UTC"
        )

        dtstart = self._normalize_boundary(dtstart)
        until = self._normalize_boundary(until, end_of_day=True)
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
        """Build the ``byweekday`` argument for ``rrule``.

        :return: list of weekday constants, or None if not used
        """
        self.ensure_one()
        if not self.use_byweekday:
            return None
        weekdays = ["mo", "tu", "we", "th", "fr", "sa", "su"]
        byweekday = [WEEKDAYS[field] for field in weekdays if self[field]]
        return byweekday

    def _bymonth(self):
        """Build the ``bymonth`` argument for ``rrule``.

        The December flag is the field ``des``.

        :return: list of month numbers (1-12), or None if not used
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
            "des",
        ]
        bymonth = [months.index(field) + 1 for field in months if self[field]]
        return bymonth

    def _bymonthday(self):
        """Build the ``bymonthday`` argument for ``rrule``.

        :return: the day of month, or None if not used
        """
        self.ensure_one()
        if not self.use_bymonthday:
            return None
        return self.month_day

    def _bysetpos(self):
        """Build the ``bysetpos`` argument for ``rrule``.

        :return: the occurrence position, or None if not used or zero
        """
        self.ensure_one()
        if not self.use_setpos or self.set_pos == 0:
            return None
        return self.set_pos
