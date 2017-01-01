# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase
from openerp.exceptions import Warning as UserError


class RestartSequenceCase(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(RestartSequenceCase, self).setUp(*args, **kwargs)

        self.obj_sequence = self.env[
            "ir.sequence"]
        self.sequence = self.obj_sequence.create({
            "name": "X Sequence",
        })

    def test_restart_sequence(self):
        self.obj_sequence.next_by_id(
            self.sequence.id)
        self.obj_sequence.next_by_id(
            self.sequence.id)
        self.assertEqual(
            self.sequence.number_next_actual,
            3)
        self.sequence.restart_sequence()
        self.assertEqual(
            self.sequence.number_next_actual,
            1)

    def test_create_sequence(self):
        self.sequence.create_cron()
        self.assertTrue(self.sequence.cron_id)
        with self.assertRaises(UserError):
            self.sequence.create_cron()
        self.sequence.delete_cron()
        self.assertEqual(
            len(self.sequence.cron_id),
            0)
