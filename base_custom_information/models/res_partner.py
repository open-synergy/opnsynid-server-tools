# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from openerp import fields, models


class ResPartner(models.Model):
    """Implement custom information for partners.

    Besides adding some visible feature to the module, this is useful for
    testing and example purposes.
    """
    _name = "res.partner"
    _inherit = [_name, "custom.info.mixin"]

    custom_info_template_id = fields.Many2one(context={"default_model": _name})
    custom_info_ids = fields.One2many(context={"default_model": _name})
