# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools import SUPERUSER_ID

ACTION_TYPE = (
    'ir.actions.report.xml',
    'ir.actions.act_window',
    'ir.actions.wizard',
    'ir.actions.act_url',
    'ir.actions.server',
    'ir.actions.client',
)


class BaseCreateMenuAccess(models.TransientModel):
    _name = 'base.create_menu_access'
    _description = 'Base Create Menu Access Wizard'

    category_id = fields.Many2one(
        string="Application",
        comodel_name="ir.module.category",
        required=True,
        ondelete="restrict"
    )

    root_menu_id = fields.Many2one(
        string="Root Menu",
        comodel_name="ir.ui.menu",
        required=False,
        domain="[('parent_id', '=', False)]"
    )

    child_menu_ids = fields.Many2many(
        string='Menu To Be Given Access Rights',
        comodel_name='ir.ui.menu',
        relation='child_menu_access_rel',
        column1='create_menu_access_id',
        column2='menu_id')

    by_root_menu = fields.Boolean(
        string="By Root Menu",
        default=False
    )

    @api.onchange('root_menu_id')
    def onchange_root_menu_id(self):
        value = []

        obj_ir_ui_menu = self.env['ir.ui.menu']

        if self.root_menu_id:
            context = {'ir.ui.menu.full_list': True}
            criteria = [
                ('id', 'child_of', self.root_menu_id.id),
                ('id', '<>', self.root_menu_id.id)
            ]
            menu_ids = obj_ir_ui_menu.with_context(
                context
            ).search(criteria)
            for menu in menu_ids:
                if menu.action and menu.action.type in ACTION_TYPE:
                    value.append(menu.id)
            self.child_menu_ids = [(6, 0, value)]

        return {}

    @api.multi
    def create_menu_access(self):
        self.ensure_one()
        obj_res_groups = self.env['res.groups']

        if self.child_menu_ids:
            for child_menu in self.child_menu_ids:
                group = child_menu.custom_group_id or False
                if not group and child_menu.action:
                    data_group = {
                        'name': child_menu.display_name,
                        'category_id': self.category_id.id,
                        'users': [(6, 0, [SUPERUSER_ID])]
                    }
                    group = obj_res_groups.create(data_group)
                child_menu.groups_id = [(6, 0, [])]
                if child_menu.action:
                    child_menu.write({
                        'custom_group_id': group.id,
                        'groups_id': [(6, 0, [group.id])],
                    })

        return {'type': 'ir.actions.act_window_close'}
