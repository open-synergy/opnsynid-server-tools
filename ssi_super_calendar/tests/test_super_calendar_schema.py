# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestSuperCalendarSchema(YamlTransactionCase):
    """Check the database layout of ``super_calendar``."""

    def test_participants_are_an_indexed_array_column(self):
        """Assert the raw array column and its GIN index exist.

        Pure Python - trigger P1 (L-01: the check reads the catalog
        through SQL, which YAML cannot return or assert).
        """
        cr = self.env.cr
        cr.execute(
            "SELECT udt_name, column_default FROM information_schema.columns "
            "WHERE table_name = 'super_calendar' "
            "AND column_name = 'partner_ids_array'"
        )
        # Odoo drops NOT NULL from non-ORM columns, so only the type and
        # the default are asserted.
        udt_name, column_default = cr.fetchone()
        self.assertEqual(udt_name, "_int4")
        self.assertIn("{}", column_default)
        cr.execute(
            "SELECT indexdef FROM pg_indexes "
            "WHERE tablename = 'super_calendar' "
            "AND indexdef ILIKE '%partner_ids_array%'"
        )
        definitions = [row[0].lower() for row in cr.fetchall()]
        self.assertTrue(any("using gin" in d for d in definitions))

    def test_no_relation_table_for_participants(self):
        """Assert no many2many relation table exists for the partners.

        Pure Python - trigger P1 (L-01: the check reads the catalog
        through SQL, which YAML cannot return or assert).
        """
        cr = self.env.cr
        cr.execute(
            "SELECT tablename FROM pg_tables " "WHERE tablename LIKE '%super_calendar%'"
        )
        self.assertEqual([row[0] for row in cr.fetchall()], ["super_calendar"])

    def test_partner_ids_is_not_stored(self):
        """Assert ``partner_ids`` is a computed field that is not stored.

        Pure Python - trigger P1 (L-01: the check reads field metadata,
        which YAML cannot return or assert).
        """
        field = self.env["super_calendar"]._fields["partner_ids"]
        self.assertFalse(field.store)
        self.assertTrue(field.compute)
