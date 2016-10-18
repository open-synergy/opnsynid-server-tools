# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models, api
from openerp.tools.safe_eval import safe_eval as eval


class BaseAmountToText(models.Model):

    _name = 'base.amount_to_text'
    _description = 'Base Amount To Text'

    lang_id = fields.Many2one(
        comodel_name='res.lang',
        string='Languange',
        ondelete='cascade')
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        ondelete='cascade')
    python_amount2text = fields.Text(
        string='Amount To Text')

    @api.multi
    def amount_to_text(self, value):
        val = {}
        self.ensure_one()
        val = "-"
        if self.python_amount2text:
            try:
                localdict = {'value': value}
                eval(self.python_amount2text, localdict,
                     mode='exec', nocopy=True)
                val = localdict['result']
            except:
                pass
        return val

    @api.model
    def get(
            self, value, currency, lang=False):
        user = self.env.user
        if not lang:
            criteria = [
                ("code", "=", user.partner_id.lang)
            ]
            lang = self.env["res.lang"].search(
                criteria, limit=1)
        att = self.search([
            ("lang_id", "=", lang.id),
            ("currency_id", "=", currency.id),
        ], limit=1)
        if not att:
            return "-"
        return att.amount_to_text(value)
