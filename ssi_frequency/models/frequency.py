# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import fields, models


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
            ("daily", "Daily")
        ],
        string="Interval Type",
        required=True,
        tracking=True,
    )
    is_exclusive = fields.Boolean(
        string="Exclusive Rule?",
        help="Checking this box will make this an exclusive rule. Exclusive rules prevent the configured days from being a schedule option.",
        default=False,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
    )
    use_bymonthday = fields.Boolean(
        string="Use Day of Month",
        help="When selected you will be able to specify which calendar day of the month the event occurs on.",
    )
    month_day = fields.Integer(
        string="Day of Month",
        tracking=True,
    )
    use_byweekday = fields.Boolean(
        string="Use Days of Week",
        help="When selected you will be able to choose which days of the week the scheduler will include (or exclude if Exclusive rule).",
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
        help="Specify an occurrence number, positive or negative, corresponding to the nth occurrence of the rule inside the frequency period. For example, -1 if combined with a 'Monthly' frequency, and a weekday of (MO, TU, WE, TH, FR), will result in the last work day of every month.",
    )
