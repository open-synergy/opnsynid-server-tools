# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, _
from odoo.exceptions import UserError


class BaseSequenceDocument(models.AbstractModel):
    _name = "base.sequence_document"
    _description = "Sequence Document"

    @api.multi
    def _create_sequence(self):
        self.ensure_one()
        configurator = self._get_configurator()
        if not configurator:
            raise UserError(_("No sequence configurator. Please create one"))

        result = configurator.initial_string

        if getattr(self, configurator.sequence_field_id.name) == result:
            result = configurator._create_sequence(self)
        else:
            result = getattr(self, configurator.sequence_field_id.name)

        return result

    @api.multi
    def _get_configurator(self):
        self.ensure_one()
        result = False
        obj_configurator = self.env["base.sequence_configurator"]
        domain = [
            ("model_id.model", "=", self._name),
        ]
        configurators = obj_configurator.search(domain)
        if len(configurators) > 0:
            result = configurators[0]
        return result
