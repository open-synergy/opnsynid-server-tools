# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# Copyright 2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError


class CustomInfoTemplate(models.Model):
    """Defines custom properties expected for a given database object."""
    _description = "Custom information template"
    _name = "custom.info.template"
    _order = "model_id, name"
    _sql_constraints = [
        ("name_model",
         "UNIQUE (name, model_id)",
         "Another template with that name exists for that model."),
    ]

    name = fields.Char(
        required=True,
        translate=True
    )
    model = fields.Char(
        string="Model technical name",
        inverse="_inverse_model",
        compute="_compute_model",
        search="_search_model",
    )
    model_id = fields.Many2one(
        string="Model",
        comodel_name="ir.model",
        ondelete="restrict",
        required=True,
        auto_join=True,
    )
    property_ids = fields.One2many(
        string="Properties",
        comodel_name="custom.info.property",
        inverse_name="template_id",
        oldname="info_ids",
    )

    @api.multi
    @api.depends(
        "model_id",
    )
    def _compute_model(self):
        for document in self:
            document.model = document.model_id.model

    @api.multi
    def _inverse_model(self):
        obj_ir_model = self.env["ir.model"]
        for document in self:
            criteria = [("model", "=", document.model)]
            document.model_id = obj_ir_model.search(criteria)

    @api.model
    def _search_model(self, operator, value):
        obj_ir_model = self.env["ir.model"]
        criteria = [("model", operator, value)]
        models = obj_ir_model.search(criteria)
        return [("model_id", "in", models.ids)]

    @api.onchange(
        "model",
    )
    def _onchange_model(self):
        self._inverse_model()

    @api.multi
    @api.constrains(
        "model_id",
    )
    def _check_model(self):
        """Avoid error when updating base module and a submodule extends a
        model that falls out of this one's dependency graph.
        """
        for document in self:
            with self.env.norecompute():
                oldmodels = \
                    document.mapped("property_ids.info_value_ids.model")
                if oldmodels and document.model not in oldmodels:
                    raise ValidationError(
                        _("You cannot change the model because it is in use.")
                    )

    @api.multi
    def check_access_rule(self, operation):
        """You access a template if you access its model."""
        for document in self:
            model = self.env[document.model_id.model or document.model]
            model.check_access_rights(operation)
            model.check_access_rule(operation)
        return super(CustomInfoTemplate, self).check_access_rule(operation)
