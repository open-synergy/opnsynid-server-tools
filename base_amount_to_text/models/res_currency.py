# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    amount_to_text_ids = fields.One2many(
        comodel_name='base.amount_to_text',
        inverse_name='currency_id',
        string='Amount To Text'
    )
