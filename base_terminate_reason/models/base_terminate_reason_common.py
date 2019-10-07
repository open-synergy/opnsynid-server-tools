# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, fields
from lxml import etree


class BaseTerminateReasonCommon(models.AbstractModel):
    _name = "base.terminate.reason_common"
    _description = "Base Terminate Reason Common"

    terminate_reason_id = fields.Many2one(
        string="Terminate Reason",
        comodel_name="base.terminate.reason",
        readonly=True,
        copy=False,
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type="form",
                        toolbar=False, submenu=False):
        res = super(BaseTerminateReasonCommon, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        active_model = self.env.context.get("active_model", "")
        terminate_reason_ids =\
            self._get_terminate_reason_ids(active_model)
        doc = etree.XML(res['arch'])
        if view_type == "search":
            node = doc.xpath("//field[@name='terminate_reason_id']")
            if node:
                the_field = node[0]
                if terminate_reason_ids:
                    domain = "[('id', 'in', %s)]" % terminate_reason_ids
                    the_field.set('domain', domain)
                else:
                    domain = "[('id','=',0)]"
                    the_field.set('domain', domain)
        res["arch"] = etree.tostring(doc)
        return res

    @api.multi
    def _get_terminate_reason_ids(self, model):
        obj_terminate_reason_config =\
            self.env["base.terminate.reason_config"]
        criteria = [(
            "name", "=", model
        )]
        terminate_reason_config_id =\
            obj_terminate_reason_config.search(criteria)

        if terminate_reason_config_id:
            return terminate_reason_config_id.terminate_reason_ids.ids
        else:
            return False
