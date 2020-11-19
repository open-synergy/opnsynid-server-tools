# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import models, fields


class SignatureItem(models.Model):
    _name = "signature.item"
    _description = "Signature Items"

    name = fields.Char(
        string="Item",
        required=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    description = fields.Text(
        string="Note",
    )
