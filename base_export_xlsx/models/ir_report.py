# -*- coding: utf-8 -*-
# Copyright 2020 OpenSynergy Indonesia
# Copyright 2020 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openerp import api, fields, models


class IrActionsReportXml(models.Model):
    _inherit = "ir.actions.report.xml"

    report_type = fields.Selection(
        selection_add=[
            ("xlsx", "xlsx")
        ]
    )

    @api.model
    def render_xlsx(self, docids, data):
        Export = self.env["base.export.xlsx"]
        return Export.create_xlsx_report(docids, data)

    @api.model
    def _get_report_from_name(self, report_name):
        _super = super(IrActionsReportXml, self)
        res = _super._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env['ir.actions.report']
        qwebtypes = ['xlsx']
        conditions = [
            ('report_type', 'in', qwebtypes),
            ('report_name', '=', report_name),
        ]
        context = self.env['res.users'].context_get()
        return report_obj.with_context(context).search(conditions, limit=1)
