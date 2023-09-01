# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0-standalone.html).

from odoo import models, fields


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
        help="The number of days from today that the scheduler will generate orders for this rule.",
        tracking=True,
    )
    buffer_early = fields.Integer(
        string="Early Buffer",
        help="The allowed number of days before the computed schedule date that an event can be done.",
        tracking=True,
    )
    buffer_late = fields.Integer(
        string="Late Buffer",
        help="The allowed number of days after the computed schedule date that an event can be done.",
        tracking=True,
    )
