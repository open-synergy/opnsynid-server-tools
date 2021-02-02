# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, _
from openerp.exceptions import Warning as UserError


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
            sequence_date = False
            if configurator.date_field_id:
                sequence_date = getattr(self, configurator.date_field_id.name)

            result = configurator._create_sequence(self, sequence_date)
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
