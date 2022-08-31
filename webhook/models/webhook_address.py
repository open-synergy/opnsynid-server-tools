# Copyright 2016 Vauxoo - https://www.vauxoo.com/
# Copyright 2022 OpenSynergy Indonesia
# Copyright 2022 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class WebhookAddress(models.Model):
    _name = "webhook.address"

    name = fields.Char(
        string="IP or Network Address",
        required=True,
        help="IP or network address of your consumer webhook:\n"
        "ip address e.g.: 10.10.0.8\n"
        "network address e.g. of: 10.10.0.8/24",
    )
    webhook_id = fields.Many2one(
        string="Webhook",
        comodel_name="webhook",
        required=True,
        ondelete="cascade",
    )
