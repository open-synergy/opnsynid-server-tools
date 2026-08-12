# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree
from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestUserGroupM2m(YamlTransactionCase):
    """Pure Python tests for the ``res.users`` access rights m2m field.

    The whole suite is written in plain Python instead of the usual
    YAML scenario approach. Every assertion here either reads the
    string ``arch`` returned by ``fields_view_get()`` (trigger P1,
    L-01/L-02: ``action: call`` discards the return value and the
    ``actual`` side of a YAML ``assert`` is always a dotted
    ``getattr`` on a record, so an arch string can never be the
    subject of an assertion) or needs the reified field name
    (``in_group_<id>``) built at runtime (trigger P10, L-09: the
    ``EVAL:`` sandbox whitelist does not expose ``str``).
    """

    def setUp(self):
        """Create two throwaway groups and one test user."""
        super().setUp()
        self.group_a = self.env["res.groups"].create(
            {"name": "SSI User Group M2M Test Group A"}
        )
        self.group_b = self.env["res.groups"].create(
            {"name": "SSI User Group M2M Test Group B"}
        )
        self.user = self.env["res.users"].create(
            {
                "name": "SSI User Group M2M Test User",
                "login": "ssi_user_group_m2m_test_user",
                "groups_id": [(6, 0, [self.env.ref("base.group_user").id])],
            }
        )

    def test_fields_view_get_access_rights_page(self):
        """Assert the ``res.users`` form arch on the access rights page.

        Trigger P1 (L-01, L-02): the composed arch string is only
        available as the return value of ``fields_view_get()``, which
        a YAML ``call`` step would discard, and a YAML ``assert``
        cannot target a raw string.

        Positive: the page ``access_rights`` contains a ``groups_id``
        field rendered with ``widget="many2many"``.
        Negative: the same page still contains at least one reified
        field (``in_group_*`` or ``sel_groups_*``), proving the core
        checkbox/selection block was not replaced.
        """
        result = self.env["res.users"].fields_view_get(view_type="form")
        arch = etree.fromstring(result["arch"])
        page = arch.xpath("//page[@name='access_rights']")
        self.assertTrue(page, "page[@name='access_rights'] not found in arch")
        m2m_fields = page[0].xpath(
            ".//field[@name='groups_id' and @widget='many2many']"
        )
        self.assertTrue(
            m2m_fields,
            "groups_id many2many field not found in access_rights page",
        )
        reified_fields = [
            field
            for field in page[0].xpath(".//field[@name]")
            if field.get("name").startswith("in_group_")
            or field.get("name").startswith("sel_groups_")
        ]
        self.assertTrue(
            reified_fields,
            "reified group fields were removed from access_rights page",
        )

    def test_write_groups_id_precedence_over_reified_checkbox(self):
        """Assert ``groups_id`` wins over a simultaneous reified write.

        Trigger P10 (L-09): the reified field name (``in_group_<id>``)
        must be assembled from the group id at runtime with plain
        string formatting, which the ``EVAL:`` sandbox does not
        support (no ``str``).

        Positive: writing ``groups_id`` with a ``(4, id)`` command adds
        the target group to ``user.groups_id``.
        Negative: writing ``groups_id`` and ``in_group_<id>`` of a
        second group in the same call only applies ``groups_id`` —
        ``res.users._remove_reified_groups()`` silently drops the
        reified key whenever ``groups_id`` is also present. This locks
        in that core behaviour so it stays documented instead of being
        found by a user in production.
        """
        self.user.write({"groups_id": [(4, self.group_a.id)]})
        self.assertIn(self.group_a, self.user.groups_id)

        reified_field_name = "in_group_%d" % self.group_b.id
        self.user.write(
            {
                "groups_id": [(4, self.group_a.id)],
                reified_field_name: True,
            }
        )
        self.assertNotIn(self.group_b, self.user.groups_id)
