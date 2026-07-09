# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, fields, models


class WizardBaseCopyUserOperatingUnit(models.TransientModel):
    _name = "base.copy_user_operating_unit"
    _description = "Wizard Copy User Operating Unit"

    user_id = fields.Many2one(
        string="User",
        comodel_name="res.users",
        required=True,
        help="Source user whose Operating Unit configuration will be copied "
        "to the selected target users.",
    )
    copy_allowed_ou = fields.Boolean(
        string="Copy Allowed Operating Units",
        default=True,
        help="If checked, the Allowed Operating Units of the source user "
        "will be copied to the target users.",
    )
    allowed_ou_mode = fields.Selection(
        string="Allowed OU Mode",
        selection=[
            ("replace", "Replace"),
            ("merge", "Merge"),
        ],
        default="replace",
        help="Replace = target's Allowed Operating Units are overwritten with "
        "the source's. Merge = the source's Allowed Operating Units are added "
        "to the target's existing ones.",
    )
    copy_default_ou = fields.Boolean(
        string="Copy Default Operating Unit",
        default=True,
        help="If checked, the Default Operating Unit of the source user "
        "will be copied to the target users.",
    )

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super(WizardBaseCopyUserOperatingUnit, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        doc = etree.XML(res["arch"])
        for node in doc.xpath("//field[@name='user_id']"):
            active_ids = self._context.get("active_ids")
            domain = "[('id', 'not in', " + str(active_ids) + ")]"
            node.set("domain", domain)
        res["arch"] = etree.tostring(doc)
        return res

    def action_copy_operating_unit(self):
        self.ensure_one()

        obj_user = self.env["res.users"]
        target_ids = self._context.get("active_ids", [])
        targets = obj_user.browse(target_ids)
        source = self.user_id

        if self.copy_allowed_ou:
            source_ou_ids = source.assigned_operating_unit_ids.ids
            if self.allowed_ou_mode == "replace":
                targets.write({"assigned_operating_unit_ids": [(6, 0, source_ou_ids)]})
            else:
                targets.write(
                    {
                        "assigned_operating_unit_ids": [
                            (4, ou_id) for ou_id in source_ou_ids
                        ]
                    }
                )

        if self.copy_default_ou and source.default_operating_unit_id:
            targets.write(
                {"default_operating_unit_id": source.default_operating_unit_id.id}
            )

        return {"type": "ir.actions.act_window_close"}
