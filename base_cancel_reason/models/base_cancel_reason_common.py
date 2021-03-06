# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields
from lxml import etree


class BaseCancelReasonCommon(models.AbstractModel):
    _name = "base.cancel.reason_common"
    _description = "Base Cancel Reason Common"

    cancel_reason_id = fields.Many2one(
        string="Cancel Reason",
        comodel_name="base.cancel.reason",
        readonly=True,
        copy=False,
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type="form",
                        toolbar=False, submenu=False):
        res = super(BaseCancelReasonCommon, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        active_model = self.env.context.get("active_model", "")
        cancel_reason_ids =\
            self._get_cancel_reason_ids(active_model)
        doc = etree.XML(res['arch'])
        if view_type == "search":
            node = doc.xpath("//field[@name='cancel_reason_id']")
            if node:
                the_field = node[0]
                if cancel_reason_ids:
                    domain = "[('id', 'in', %s)]" % cancel_reason_ids
                    the_field.set('domain', domain)
                else:
                    domain = "[('id','=',0)]"
                    the_field.set('domain', domain)
        res["arch"] = etree.tostring(doc)
        return res

    @api.multi
    def _get_cancel_reason_ids(self, model):
        obj_cancel_reason_config =\
            self.env["base.cancel.reason_config"]
        criteria = [(
            "name", "=", model
        )]
        cancel_reason_config_id =\
            obj_cancel_reason_config.search(criteria)

        if cancel_reason_config_id:
            return cancel_reason_config_id.cancel_reason_ids.ids
        else:
            return False
