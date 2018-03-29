# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from lxml import etree


class WizardBaseCopyUserRole(models.TransientModel):
    _name = 'base.copy_user_role'

    user_id = fields.Many2one(
        string='User',
        comodel_name='res.users',
        required=True
        )

    @api.model
    def fields_view_get(
        self, view_id=None, view_type='form', toolbar=False, submenu=False
    ):
        res = super(WizardBaseCopyUserRole, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='user_id']"):
            active_ids = self._context.get('active_ids')
            domain = "[('id', 'not in', " + str(active_ids) + ")]"
            node.set('domain', domain)
        res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def copy_role(self):
        self.ensure_one()

        obj_user = self.env['res.users']

        context = self._context
        record_id = context['active_ids']

        user_src = obj_user.browse(self.user_id.id)

        for data in record_id:
            user_dest = obj_user.browse(data)
            if user_dest.role_line_ids:
                user_dest.role_line_ids.unlink()
            for role_line in user_src.role_line_ids:
                vals = {
                    "role_line_ids": [(0, 0, {
                        "role_id": role_line.role_id.id,
                        "date_from": role_line.date_from,
                        "date_to": role_line.date_to,
                        "is_enabled": role_line.is_enabled
                    })],
                }
                user_dest.write(vals)

        return {'type': 'ir.actions.act_window_close'}
