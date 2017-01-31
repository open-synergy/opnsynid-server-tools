# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class BaseCase(TransactionCase):
    def setUp(self):
        super(BaseCase, self).setUp()
        # Object
        self.obj_ir_module_category =\
            self.env['ir.module.category']
        self.obj_ir_ui_menu =\
            self.env['ir.ui.menu']
        self.wiz =\
            self.env['base.create_menu_access']
        # Data Menu
        self.menu_root_partner =\
            self.env.ref('base.menu_base_partner')
        self.ACTION_TYPE = (
            'ir.actions.report.xml',
            'ir.actions.act_window',
            'ir.actions.wizard',
            'ir.actions.act_url',
            'ir.actions.server',
            'ir.actions.client',
        )

    def check_child_menu_ids(self, custom_group_id=None):
        value = []
        context = {'ir.ui.menu.full_list': True}
        if self.menu_root_partner:
            if custom_group_id:
                criteria = [
                    ('id', 'child_of', self.menu_root_partner.id),
                    ('id', '<>', self.menu_root_partner.id)
                ]
            else:
                criteria = [
                    ('id', 'child_of', self.menu_root_partner.id),
                    ('id', '<>', self.menu_root_partner.id),
                    ('custom_group_id', '=', False)
                ]
            menu_ids = self.obj_ir_ui_menu.with_context(
                context
            ).search(criteria)
            for menu in menu_ids:
                if menu.action and menu.action.type in self.ACTION_TYPE:
                    value.append(menu.id)
        return {
            'value': value,
            'ids': menu_ids
        }
