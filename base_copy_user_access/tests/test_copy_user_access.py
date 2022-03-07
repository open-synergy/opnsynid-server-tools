# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from lxml import etree

from odoo.tests.common import TransactionCase


class TestCopyUserAccess(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestCopyUserAccess, self).setUp(*args, **kwargs)

        # Objects
        self.obj_res_users = self.env["res.users"]
        self.obj_wizard = self.env["base.copy_user_access"]

        # Data
        self.demo_user = self.env.ref("base.user_demo")

    def _prepare_user_data(self):
        data = {"login": "test_user@test.com", "name": "test lagi", "password": "a"}

        return data

    def test_copy_user_access(self):
        # Create New User
        data = self._prepare_user_data()
        user = self.obj_res_users.create(data)
        # Check create new user
        self.assertIsNotNone(user)

        # Fill Context
        context = self.obj_res_users.context_get()
        ctx = context.copy()
        ctx.update({"active_ids": user.ids})

        # Create Wizard
        wizard = self.obj_wizard.with_context(ctx).create(
            {"user_id": self.demo_user.id}
        )

        # Check fields_view_get
        view = wizard.fields_view_get()

        doc = etree.XML(view["arch"])
        for node in doc.xpath("//field[@name='user_id']"):
            domain = node.get("domain")
            test_domain = "[('id', 'not in', " + str(user.ids) + ")]"
            self.assertEquals(domain, test_domain)

        # Check group_ids(new_user) with group_ids(demo_user)
        wizard.with_context(ctx).copy_access_right()
        self.assertEquals(set(self.demo_user.groups_id.ids), set(user.groups_id.ids))
