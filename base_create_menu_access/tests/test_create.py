# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .base import BaseCase


class TestCreate(BaseCase):
    def create_application(self):
        val = {
            'name': 'Test Application'
        }
        category_id =\
            self.obj_ir_module_category.create(val)
        return category_id

    def test_create_menu_access(self):
        y = []
        # Create Application
        category_id = self.create_application()

        # Create Menu Access
        new = self.wiz.new()
        new.category_id = category_id.id
        new.by_root_menu = True
        new.root_menu_id = self.menu_root_partner.id

        new.onchange_root_menu_id()
        new.create_menu_access()

        child_menu_ids =\
            self.check_child_menu_ids(True)['ids']

        # Search Custom Group Ids
        for child_menu in child_menu_ids:
            if child_menu.custom_group_id:
                y.append(child_menu.custom_group_id.id)

        # Check Custom Group Ids
        self.assertIsNotNone(y)
