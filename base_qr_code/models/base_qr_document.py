# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields
from qrcode import QRCode, constants as qr_constants
from base64 import b64encode
from cStringIO import StringIO


class BaseQrDocument(models.AbstractModel):
    _name = "base.qr_document"
    _description = "QR Document"

    @api.multi
    def _compute_qr_image(self):
        odoo_url = self.env["ir.config_parameter"].get_param("web.base.url")
        for document in self:
            document_url = "/web?#id=%d&view_type=form&model=%s" % (
                document.id,
                document._name,
            )
            full_url = odoo_url + document_url
            qr = QRCode(
                version=1,
                error_correction=qr_constants.ERROR_CORRECT_L,
                box_size=5,
                border=4,
            )
            qr.add_data(full_url)
            qr.make(fit=True)
            qr_image = qr.make_image()
            temp_file = StringIO()
            qr_image.save(temp_file)
            qr_image = b64encode(temp_file.getvalue())
            document.qr_image = qr_image

    qr_image = fields.Binary(
        string="QR Code",
        compute="_compute_qr_image",
        store=False,
    )
