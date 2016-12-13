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

        # Check Group Ids
        self.assertIn(
            child_menu_ids.custom_group_id.id,
            [x.id for x in child_menu_ids.groups_id])
