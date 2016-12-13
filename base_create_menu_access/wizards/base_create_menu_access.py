# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.tools import SUPERUSER_ID


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
            criteria = [
                ('id', 'child_of', self.root_menu_id.id),
                ('parent_id', '<>', self.root_menu_id.id),
                ('custom_group_id', '=', False)
            ]
            menu_ids = obj_ir_ui_menu.search(criteria)
            for menu in menu_ids:
                value.append(menu.id)
            self.child_menu_ids = [(6, 0, value)]

        return {}

    @api.multi
    def create_menu_access(self):
        self.ensure_one()
        obj_res_groups = self.env['res.groups']

        if self.child_menu_ids:
            for child_menu in self.child_menu_ids:
                data_group = {
                    'name': child_menu.display_name,
                    'category_id': self.category_id.id,
                    'menu_access': [(6, 0, [child_menu.id])],
                    'users': [(6, 0, [SUPERUSER_ID])]
                }
                group_id = obj_res_groups.create(data_group)
                child_menu.write({
                    'custom_group_id': group_id.id
                })

        return {'type': 'ir.actions.act_window_close'}
