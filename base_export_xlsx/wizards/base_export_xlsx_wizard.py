# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import models, fields, api, SUPERUSER_ID, _
from openerp.exceptions import Warning as UserError
from openerp.tools.safe_eval import safe_eval as eval


class BaseExportXlsxWizard(models.TransientModel):
    _name = "base.export.xlsx.wizard"

    name = fields.Char(
        string="File Name",
        readonly=True,
        size=500,
    )
    data = fields.Binary(
        string="File",
        readonly=True,
    )

    @api.model
    def _compute_allowed_template_ids(self):
        result = []
        obj_xlsx_template =\
            self.env["base.xlsx.template"]
        active_model = self.env.context.get("active_model", "")
        criteria = [
            ("model_id.model", "=", active_model)
        ]
        template_ids = obj_xlsx_template.search(criteria)
        if template_ids:
            for template in template_ids:
                allowed_print = self._check_allowed_print(template)
                if allowed_print:
                    condition =\
                        self.check_python_cond(
                            template.python_condition)
                    if condition:
                        result.append(template.id)
        return result

    allowed_template_ids = fields.Many2many(
        string="Allowed Template",
        comodel_name="base.xlsx.template",
        default=lambda self: self._compute_allowed_template_ids(),
        relation="rel_wizard_2_xlsx_template",
        column1="wizard_id",
        column2="template_id",
    )

    template_id = fields.Many2one(
        string="Template",
        comodel_name="base.xlsx.template",
        required=True,
    )
    res_id = fields.Integer(
        string="Resource ID",
        readonly=True,
        required=True,
    )
    res_model = fields.Char(
        string="Resource Model",
        readonly=True,
        required=True,
        size=500,
    )
    state = fields.Selection(
        string="Status",
        selection=[
            ("choose", "Choose"),
            ("get", "Get")
        ],
        default="choose",
    )

    @api.model
    def default_get(self, fields):
        _super = super(BaseExportXlsxWizard, self)
        defaults = _super.default_get(fields)
        res_model = self._context.get("active_model", False)
        res_id = self._context.get("active_id", False)
        obj_xlsx_template = self.env["base.xlsx.template"]
        template_ids = self._compute_allowed_template_ids()
        templates = obj_xlsx_template.search([("id", "in", template_ids)])
        if templates:
            for template in templates:
                if not template.file:
                    raise UserError(_("No file in %s") % (template.name,))
            defaults["template_id"] = templates[0].id
        else:
            raise UserError(_("No template found"))
        defaults["res_id"] = res_id
        defaults["res_model"] = res_model
        return defaults

    @api.model
    def _check_allowed_print(self, object):
        user = self.env.user
        if user.id == SUPERUSER_ID:
            result = True
        else:
            if object.group_ids:
                user_group_ids = user.groups_id.ids
                if (set(object.group_ids.ids) & set(user_group_ids)):
                    result = True
                else:
                    result = False
            else:
                result = True
        return result

    @api.model
    def _get_object(self):
        active_id = self.env.context.get("active_id", False)
        active_model = self.env.context.get("active_model", "")
        object = self.env[active_model].browse(
            [active_id]
        )[0]
        return object

    @api.model
    def _get_localdict(self):
        return {
            "record": self._get_object(),
            "env": self.env,
        }

    @api.model
    def check_python_cond(self, python_condition):
        localdict = self._get_localdict()

        try:
            eval(python_condition,
                 localdict, mode="exec", nocopy=True)
            result = localdict["result"]
        except:  # noqa: E722
            result = False

        return result

    @api.multi
    def action_export(self):
        self.ensure_one()
        obj_export_xlsx = self.env["base.export.xlsx"]
        data, name = obj_export_xlsx.create_xlsx_report(
            self.template_id, self.res_model, self.res_id)

        self.write({"state": "get", "data": data, "name": name})
        return {
            "type": "ir.actions.act_window",
            "res_model": "base.export.xlsx.wizard",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }
