# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, api, fields
from base64 import b64encode
from cStringIO import StringIO

import logging
_logger = logging.getLogger(__name__)

try:
    from qrcode import QRCode, constants as qr_constants
except (ImportError, IOError) as err:
    _logger.debug(err)


class BaseQrDocument(models.AbstractModel):
    _name = "base.qr_document"
    _description = "QR Document"

    @api.multi
    def _compute_qr_image(self):

        for document in self:
            qrcode_content = self._get_qrcode_content()
            qr = QRCode(
                version=1,
                error_correction=qr_constants.ERROR_CORRECT_L,
                box_size=5,
                border=4,
            )
            qr.add_data(qrcode_content)
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

    @api.multi
    def _get_qrcode_content(self):
        self.ensure_one()
        criteria = [
            ("name.model", "=", self._name),
        ]
        obj_content = self.env["base.qr_content_policy"]
        content_policy = obj_content.search(criteria)
        if len(content_policy) > 0:
            content = content_policy[0]._get_content(self)
        else:
            content = self._get_standard_content()
        return content

    @api.multi
    def _get_standard_content(self):
        self.ensure_one()
        odoo_url = self.env["ir.config_parameter"].get_param("web.base.url")
        document_url = "/web?#id=%d&view_type=form&model=%s" % (
            self.id,
            self._name,
        )
        full_url = odoo_url + document_url
        return full_url
