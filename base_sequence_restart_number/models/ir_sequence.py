# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    cron_id = fields.Many2one(
        string="Cron",
        comodel_name="ir.cron",
        readonly=True,
    )

    @api.multi
    def restart_sequence(self):
        for sequence in self:
            sequence.number_next = 1

    @api.multi
    def create_cron(self):
        for sequence in self:
            self._create_cron()

    @api.multi
    def delete_cron(self):
        for sequence in self:
            sequence._delete_cron()

    @api.multi
    def _delete_cron(self):
        self.ensure_one()
        if self.cron_id:
            self.cron_id.unlink()

    @api.multi
    def _create_cron(self):
        self.ensure_one()
        if self.cron_id:
            strWarning = _("Sequence already have a cron")
            raise UserError(strWarning)

        obj_cron = self.env[
            "ir.cron"]
        name = "Sequence: %s" % self.name
        args = "[%s]" % (str(self.id))
        cron = obj_cron.create({
            "name": name,
            "user_id": self.env.user.id,
            "active": True,
            "model": "ir.sequence",
            "function": "restart_sequence",
            "args": args,
        })
        self.cron_id = cron
