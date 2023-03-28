# Copyright 2023 OpenSynergy Indonesia
# Copyright 2023 PT. Simetri Sinergi Indonesia
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, fields, models
from odoo.tools import ormcache


class BaseCustomSystemParameter(models.Model):
    _name = "base.custom_system_parameter"
    _description = "Base Custom System Parameter"
    _rec_name = "key"
    _order = "key"

    _sql_constraints = [("key_uniq", "unique (key)", "Key must be unique.")]

    key = fields.Char(
        string="Key",
        required=True,
        index=True,
    )
    value = fields.Text(
        string="Text",
        required=True,
    )

    @api.model
    def get_param(self, key, default=False):
        return self._get_param(key) or default

    @api.model
    @ormcache(
        "self.env.uid",
        "self.env.su",
        "key",
    )
    def _get_param(self, key):
        params = self.search_read([("key", "=", key)], fields=["value"], limit=1)
        return params[0]["value"] if params else None

    @api.model
    def set_param(self, key, value):

        param = self.search([("key", "=", key)])
        if param:
            old = param.value
            if value is not False and value is not None:
                if str(value) != old:
                    param.write({"value": value})
            else:
                param.unlink()
            return old
        else:
            if value is not False and value is not None:
                self.create({"key": key, "value": value})
            return False

    @api.model_create_multi
    def create(self, vals_list):
        self.clear_caches()
        return super(BaseCustomSystemParameter, self).create(vals_list)

    def write(self, vals):
        self.clear_caches()
        return super(BaseCustomSystemParameter, self).write(vals)

    def unlink(self):
        self.clear_caches()
        return super(BaseCustomSystemParameter, self).unlink()
