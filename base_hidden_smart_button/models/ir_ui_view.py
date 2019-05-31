# -*- coding: utf-8 -*-
# Copyright 2016 Ignacio Ibeas <ignacio@acysos.com>
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, models
from openerp.exceptions import Warning as UserError
from openerp.osv import orm
import json
import logging
_logger = logging.getLogger(__name__)


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    @api.multi
    def _check_hidden_smart_button(self, view_id, button_name):
        obj_hidden = self.env["base.hidden_smart_button"]
        criteria = [
            ("view_id", "=", view_id),
            ("button_name", "=", button_name),
            ("company_id", "=", self.env.user.company_id.id)
        ]
        hidden_button = obj_hidden.search(criteria)
        if hidden_button:
            if not hidden_button.user_ids and not hidden_field.group_ids:
                return True
            if self.env.user in hidden_button.user_ids:
                return True
            for group in hidden_button.group_ids:
                if group in self.env.user.groups_id:
                    return True
        return False

    @api.model
    def postprocess_and_fields(self, model, node, view_id):
        result = super(IrUiView, self).postprocess_and_fields(
            model, node, view_id)
        _logger.info(node.tag)
        if node.tag == "button":# and node.get("class").find("oe_stat_button"):
            raise UserError("a")
            if self._check_hidden_smart_button(view_id, node.get("name")):
                modifiers = json.loads(node.get("modifiers"))
                modifiers["invisible"] = True
                orm.transfer_modifiers_to_node(modifiers, node)
        return result
