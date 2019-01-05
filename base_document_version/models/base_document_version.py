# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields


class BaseDocumentVersion(models.AbstractModel):
    _name = "base.document_version"
    _description = "Abstract Model for Document Version"

    revision = fields.Integer(
        string="Version",
        default=0,
        readonly=True,
        copy=False,
    )
    total_revision = fields.Integer(
        string="Total",
        default=0,
        readonly=True,
        copy=False,
    )
    previous_version_id = fields.Many2one(
        string="Previous Version",
        comodel_name=lambda self: self._name,
        select=True,
        readonly=True,
    )
    origin_version_id = fields.Many2one(
        string="Origin Version",
        comodel_name=lambda self: self._name,
        select=True,
        readonly=True,
    )
    version_number = fields.Char(
        string="Version Number",
        readonly=True,
        copy=False,
    )

    @api.multi
    def button_new_revision(self):
        self.ensure_one()
        for document in self:
            document = document.copy(document._prepare_new_version())
            return {
                "name": self._description,
                "type": "ir.actions.act_window",
                "res_model": self._name,
                "view_type": "form",
                "view_mode": "form",
                "res_id": document.id,
            }

    @api.multi
    def _get_version_number(self):
        self.ensure_one()
        total_revision = self.total_revision + 1
        self.write({
            "total_revision": self.total_revision + 1,
        })
        if not self.origin_version_id:
            return str(total_revision)
        else:
            return str(self.version_number) + "." + str(total_revision)

    @api.multi
    def _prepare_new_version(self):
        self.ensure_one()
        origin = self._get_origin_version()
        version_number = self._get_version_number()
        return {
            "previous_version_id": self.id,
            # TODO: Get number beside field name
            "name": origin.name + " Rev." + version_number,
            "origin_version_id": origin.id,
            "version_number": version_number,
            "revision": self.total_revision + 1,
        }

    @api.multi
    def _get_origin_version(self):
        self.ensure_one()
        if not self.origin_version_id:
            return self
        else:
            return self.origin_version_id
