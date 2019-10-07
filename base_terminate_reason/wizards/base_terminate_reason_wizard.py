# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields, _
from lxml import etree

from openerp.exceptions import Warning as UserError


class BaseTerminateReasonWizard(models.TransientModel):
    _name = "base.terminate.reason_wizard"
    _description = "Base Termination Wizard"

    terminate_reason_id = fields.Many2one(
        string="Reason",
        comodel_name="base.terminate.reason",
        required=True,
    )

    @api.model
    def fields_view_get(self, view_id=None, view_type="form",
                        toolbar=False, submenu=False):
        res = super(BaseTerminateReasonWizard, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        active_model = self.env.context.get("active_model", "")
        terminate_reason_ids =\
            self._get_terminate_reason_ids(active_model)
        doc = etree.XML(res['arch'])
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

    @api.multi
    def _get_method_terminate_name(self, model):
        obj_terminate_reason_config =\
            self.env["base.terminate.reason_config"]
        criteria = [(
            "name", "=", model
        )]
        terminate_reason_config_id =\
            obj_terminate_reason_config.search(criteria)

        if terminate_reason_config_id:
            return terminate_reason_config_id.method_terminate_name
        else:
            raise UserError(_("Error! No Method Terminate Name Defined"))

    @api.multi
    def action_confirm(self):
        for wiz in self:
            wiz._confirm_terminate()

    @api.multi
    def _confirm_terminate(self):
        self.ensure_one()
        active_ids = self.env.context.get("active_ids", [])
        active_model = self.env.context.get("active_model", "")
        object_id = self.env[active_model].browse(
            active_ids
        )
        method_terminate_name =\
            self._get_method_terminate_name(active_model)
        if method_terminate_name and hasattr(object_id, method_terminate_name):
            method_terminate =\
                getattr(object_id, method_terminate_name)
            method_terminate()
            if hasattr(object_id, "terminate_reason_id"):
                object_id.write(
                    self._prepare_terminate_reason_data()
                )
        else:
            return True

    @api.model
    def _prepare_terminate_reason_data(self):
        result = {
            "terminate_reason_id": self.terminate_reason_id.id
        }
        return result
