# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).
from dateutil.rrule import rruleset

from odoo import fields, models


class FrequencyRuleSet(models.Model):
    _name = "frequency_set"
    _description = "Frequency Rule Set"
    _inherit = ["mixin.master_data"]

    fsm_frequency_ids = fields.Many2many(
        "frequency",
        string="Frequency Rules",
        tracking=True,
    )
    schedule_days = fields.Integer(
        string="Days Ahead to Schedule",
        default=30,
        help="""The number of days from today that the scheduler
                will generate orders for this rule.""",
        tracking=True,
    )
    buffer_early = fields.Integer(
        string="Early Buffer",
        help="""The allowed number of days before the computed
                schedule date that an event can be done.""",
        tracking=True,
    )
    buffer_late = fields.Integer(
        string="Late Buffer",
        help="""The allowed number of days after the computed
              schedule date that an event can be done.""",
        tracking=True,
    )

    def _get_rruleset(self, dtstart=None, until=None, tz=None):
        self.ensure_one()
        rset = rruleset()
        for rule in self.fsm_frequency_ids:
            if not rule.is_exclusive:
                rset.rrule(rule._get_rrule(dtstart, until, tz))
            else:
                rset.exrule(rule._get_rrule(dtstart, tz=tz))
        return rset
