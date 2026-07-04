# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""
Assertions on the generated arch of ``base.user_groups_view`` cannot be
expressed through the declarative ``odoo-yaml-test`` action/assert DSL
(create/write/call/assert on records) since they inspect an XML string
produced as a side effect of ``res.groups`` CRUD. Following the same
exception granted to onchange tests, these are plain ``TransactionCase``
tests instead.
"""
import re

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestResGroupsView(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Section = self.env["user_group_section"]
        self.Category = self.env["ir.module.category"]
        self.Groups = self.env["res.groups"]

    def _arch(self):
        return self.env.ref("base.user_groups_view").arch

    def _selection_field_id_sets(self, arch):
        """Return, for every generated ``sel_groups_*`` field, the set of
        group ids encoded in its field name."""
        return [
            {int(part) for part in match.group(1).split("_")}
            for match in re.finditer(r'name="sel_groups_([\d_]+)"', arch)
        ]

    def test_category_without_section_excluded_from_generated_arch(self):
        category = self.Category.create({"name": "Test Category No Section"})
        group = self.Groups.create(
            {"name": "Test Group No Section", "category_id": category.id}
        )
        arch = self._arch()
        self.assertNotIn(f'name="in_group_{group.id}"', arch)
        selection_ids = {i for s in self._selection_field_id_sets(arch) for i in s}
        self.assertNotIn(group.id, selection_ids)

    def test_selection_group_placed_under_its_section(self):
        section = self.Section.create({"name": "Test Section Selection", "code": "/"})
        category = self.Category.create(
            {"name": "Test Category Selection", "section_id": section.id}
        )
        user_group = self.Groups.create(
            {"name": "Test User", "category_id": category.id}
        )
        validator_group = self.Groups.create(
            {
                "name": "Test Validator",
                "category_id": category.id,
                "implied_ids": [(4, user_group.id)],
            }
        )
        arch = self._arch()
        self.assertIn("Test Section Selection", arch)
        matching_sets = [
            ids
            for ids in self._selection_field_id_sets(arch)
            if user_group.id in ids and validator_group.id in ids
        ]
        self.assertTrue(
            matching_sets,
            "Expected a sel_groups_* field covering both chained groups.",
        )

    def test_multiple_selection_categories_not_wrapped_in_nested_group(self):
        # Two applications sharing one section must appear directly under
        # a single section separator, not each boxed in its own nested
        # <group string="..."> (core boxes selection-kind applications by
        # their parent category; this module intentionally flattens that
        # away since fields_get() already labels each field by itself).
        section = self.Section.create({"name": "Test Section Flat", "code": "/"})
        category_a = self.Category.create(
            {"name": "Test Category Flat A", "section_id": section.id}
        )
        category_b = self.Category.create(
            {"name": "Test Category Flat B", "section_id": section.id}
        )
        group_a = self.Groups.create(
            {"name": "Test Flat A", "category_id": category_a.id}
        )
        group_b = self.Groups.create(
            {"name": "Test Flat B", "category_id": category_b.id}
        )
        arch = self._arch()
        self.assertEqual(
            arch.count('string="Test Section Flat"'),
            1,
            "Both applications share one section: the section separator "
            "must appear exactly once, not once per application.",
        )
        self.assertNotIn(
            'string="Other"',
            arch,
            "Applications without a parent category must not be boxed "
            "under a nested 'Other' group anymore.",
        )
        selection_ids = {i for s in self._selection_field_id_sets(arch) for i in s}
        self.assertIn(group_a.id, selection_ids)
        self.assertIn(group_b.id, selection_ids)

    def test_boolean_group_placed_under_its_section(self):
        section = self.Section.create({"name": "Test Section Boolean", "code": "/"})
        category = self.Category.create(
            {"name": "Test Category Boolean", "section_id": section.id}
        )
        group_a = self.Groups.create(
            {"name": "Test Boolean A", "category_id": category.id}
        )
        group_b = self.Groups.create(
            {"name": "Test Boolean B", "category_id": category.id}
        )
        arch = self._arch()
        self.assertIn("Test Section Boolean", arch)
        self.assertIn(f'name="in_group_{group_a.id}"', arch)
        self.assertIn(f'name="in_group_{group_b.id}"', arch)

    def test_sections_ordered_by_sequence_not_by_name(self):
        section_low = self.Section.create(
            {"name": "Zzz Section Low Sequence", "code": "/", "sequence": 5}
        )
        section_high = self.Section.create(
            {"name": "Aaa Section High Sequence", "code": "/", "sequence": 50}
        )
        category_low = self.Category.create(
            {"name": "Test Category Order Low", "section_id": section_low.id}
        )
        category_high = self.Category.create(
            {"name": "Test Category Order High", "section_id": section_high.id}
        )
        self.Groups.create({"name": "Test Order Low A", "category_id": category_low.id})
        self.Groups.create({"name": "Test Order Low B", "category_id": category_low.id})
        self.Groups.create(
            {"name": "Test Order High A", "category_id": category_high.id}
        )
        self.Groups.create(
            {"name": "Test Order High B", "category_id": category_high.id}
        )
        arch = self._arch()
        self.assertLess(
            arch.index("Zzz Section Low Sequence"),
            arch.index("Aaa Section High Sequence"),
            "Section with lower sequence must appear before the one with "
            "higher sequence, regardless of alphabetical name order.",
        )

    def test_section_id_write_triggers_view_update(self):
        # A lone group in a category is classified as "selection" kind by
        # res.groups.get_groups_by_application() (order is trivially total
        # with a single element), so it is rendered as sel_groups_<id>.
        section = self.Section.create({"name": "Test Section Write", "code": "/"})
        category = self.Category.create({"name": "Test Category Write"})
        group = self.Groups.create(
            {"name": "Test Group Write", "category_id": category.id}
        )
        before_ids = {i for s in self._selection_field_id_sets(self._arch()) for i in s}
        self.assertNotIn(group.id, before_ids)

        category.write({"section_id": section.id})
        after_ids = {i for s in self._selection_field_id_sets(self._arch()) for i in s}
        self.assertIn(group.id, after_ids)
