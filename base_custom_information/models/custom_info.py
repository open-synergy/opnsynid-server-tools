# -*- coding: utf-8 -*-
# Copyright 2015 Sergio Teruel <sergio.teruel@tecnativa.com>
# Copyright 2015 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from openerp import api, fields, models


class CustomInfoMixin(models.AbstractModel):
    """Models that inherit from this one will get custom information for free!

    They will probably want to declare a default model in the context of the
    :attr:`custom_info_template_id` field.

    See example in :mod:`res_partner`.
    """
    _description = "Inheritable abstract model to add custom info in any model"
    _name = "custom.info.mixin"

    custom_info_template_id = fields.Many2one(
        string="Custom Information Template",
        comodel_name="custom.info.template",
        domain=lambda self: [("model", "=", self._name)],
    )
    custom_info_ids = fields.One2many(
        string="Custom Properties",
        comodel_name="custom.info.value",
        inverse_name="res_id",
        domain=lambda self: [("model", "=", self._name)],
        auto_join=True,
    )

    @api.multi
    def onchange(self, values, field_name, field_onchange):
        x2many_field = "custom_info_ids"
        if x2many_field in field_onchange:
            subfields = getattr(self, x2many_field)._fields.keys()
            for subfield in subfields:
                field_onchange.setdefault(
                    u"{}.{}".format(x2many_field, subfield), u"",
                )
        return super(CustomInfoMixin, self).onchange(
            values, field_name, field_onchange,
        )

    @api.onchange(
        "custom_info_template_id",
    )
    def _onchange_custom_info_template_id(self):
        tmpls = self.all_custom_info_templates()
        props_good = tmpls.mapped("property_ids")
        props_enabled = self.mapped("custom_info_ids.property_id")
        to_add = props_good - props_enabled
        to_remove = props_enabled - props_good
        values = self.custom_info_ids
        values = values.filtered(lambda r: r.property_id not in to_remove)
        for prop in to_add.sorted():
            newvalue = self.custom_info_ids.new({
                "property_id": prop.id,
                "res_id": self.id,
                "value": prop.default_value,
            })
            newvalue._inverse_value()
            newvalue._compute_value()
            values += newvalue
        self.custom_info_ids = values
        if self.all_custom_info_templates() != tmpls:
            self._onchange_custom_info_template_id()

    @api.multi
    def unlink(self):
        """Remove linked custom info this way, as can't be handled
        automatically.
        """
        info_values = self.mapped('custom_info_ids')
        res = super(CustomInfoMixin, self).unlink()
        if res:
            info_values.unlink()
        return res

    @api.multi
    @api.returns(
        "custom.info.value",
    )
    def get_custom_info_value(self, properties):
        """Get ``custom.info.value`` records for the given property."""
        return self.env["custom.info.value"].search([
            ("model", "=", self._name),
            ("res_id", "in", self.ids),
            ("property_id", "in", properties.ids),
        ])

    @api.multi
    def all_custom_info_templates(self):
        """Get all custom info templates involved in these owners."""
        return (self.mapped("custom_info_template_id") |
                self.mapped("custom_info_ids.value_id.template_id"))

    @api.multi
    def button_update_info(self):
        self.ensure_one()
        obj_custom_info_val = self.env["custom.info.value"]
        if self.custom_info_template_id:
            custom_info_prop_ids = self.mapped("custom_info_ids.property_id")
            tmpls = self.all_custom_info_templates()
            template_prop_ids = tmpls.mapped("property_ids")
            to_update = template_prop_ids - custom_info_prop_ids
            for prop in to_update.sorted():
                newvalue = obj_custom_info_val.create({
                    "model": self._name,
                    "property_id": prop.id,
                    "res_id": self.id,
                    "value": prop.default_value,
                })
                newvalue._inverse_value()
                newvalue._compute_value()
        return True
