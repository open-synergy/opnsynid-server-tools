# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import fields, models, api


class SignatureDefinitionSignee(models.Model):
    _name = "signature.definition.signee"
    _description = "List Of Signee"

    signature_id = fields.Many2one(
        string="Signature",
        comodel_name="signature.definition",
    )
    signature_key = fields.Char(
        string="Signature Key",
        required=True,
    )
    signature_item_id = fields.Many2one(
        string="Signature Item",
        comodel_name="signature.item",
        required=True,
    )
    signature_type = fields.Selection(
        string="Type",
        default="user",
        selection=[
            ("user", "User."),
            ("python", "Python Expression."),
        ],
        required=True,
    )
    signature_user_id = fields.Many2one(
        string="Sign By User",
        comodel_name="res.users",
    )
    python_code = fields.Text(
        string="Python Expression",
        help="Python Code for determines User "
             "who can be a reviewer",
        default="# Available Locals:"
                "\n# - env: environment"
                "\n# - rec: current record"
                "\n# Available Return:"
                "\n# - user: List ID of User"
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    @api.onchange(
        "signature_type",
    )
    def onchange_signature_user_id(self):
        self.signature_user_id = False

    @api.onchange(
        "signature_type",
    )
    def onchange_python_code(self):
        str_python = """# Available Locals:
# - rec: current record
# - env: environment"
# Available Return:
# - user: List ID of User
"""
        self.python_code = str_python
