# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .base import BaseCase


class TestOnChange(BaseCase):
    def test_onchange_parent_menu_id(self):
        with self.env.do_in_onchange():
            new = self.wiz.new()
            new.by_root_menu = True
            new.root_menu_id = self.menu_root_partner.id

            new.onchange_root_menu_id()

            child_menu_ids =\
                self.check_child_menu_ids()['value']

            self.assertEqual(
                child_menu_ids, [x.id for x in new.child_menu_ids])
