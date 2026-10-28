# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import secrets
from datetime import timedelta

from odoo import api, fields, models


class MailOtpTrustedDevice(models.Model):
    """
    Represents a browser that is trusted to skip the email OTP step.
    The browser keeps a random token in a cookie; only the SHA-256 hash of
    that token is stored here, together with its expiration date.
    """

    _name = "mail_otp_trusted_device"
    _description = "Email OTP Trusted Device"
    _order = "id desc"

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        ondelete="cascade",
        index=True,
        help="User who trusted this device.",
    )
    token_hash = fields.Char(
        string="Token Hash",
        required=True,
        readonly=True,
        index=True,
        help="SHA-256 hash of the token stored in the device cookie.",
    )
    expiration_date = fields.Datetime(
        string="Expiration Date",
        readonly=True,
        help="The device is no longer trusted after this date and time.",
    )
    ip_address = fields.Char(
        string="IP Address",
        readonly=True,
        help="IP address of the login that trusted the device.",
    )
    user_agent = fields.Char(
        string="User Agent",
        readonly=True,
        help="Browser user agent of the login that trusted the device.",
    )
    last_used_date = fields.Datetime(
        string="Last Used Date",
        readonly=True,
        help="Date and time the device last skipped the OTP step.",
    )

    @api.model
    def _hash_token(self, token):
        """Return the SHA-256 hexadecimal digest of a cookie token.

        :param token: the plain cookie token
        :return: hexadecimal digest string
        """
        return hashlib.sha256((token or "").encode("utf-8")).hexdigest()

    @api.model
    def _create_device(self, user):
        """Register the current browser as a trusted device.

        :param user: ``res.users`` who trusts the device
        :return: the plain token to put in the cookie
        """
        token = secrets.token_urlsafe(32)
        days = self.env["mail_otp_challenge"]._mail_otp_get_param(
            "mail_otp_trusted_device_days"
        )
        now = fields.Datetime.now()
        values = self.env["mail_otp_challenge"]._mail_otp_request_info()
        values.update(
            {
                "user_id": user.id,
                "token_hash": self._hash_token(token),
                "expiration_date": now + timedelta(days=days),
                "last_used_date": now,
            }
        )
        self.sudo().create(values)
        return token

    @api.model
    def _check_token(self, token, user):
        """Tell whether a cookie token is a valid device of the user.

        Updates ``last_used_date`` of the device when it is valid.

        :param token: the plain cookie token
        :param user: ``res.users`` that is logging in
        :return: ``True`` when an unexpired device of the user matches
        """
        if not token:
            return False
        device = self.sudo().search(
            [
                ("user_id", "=", user.id),
                ("token_hash", "=", self._hash_token(token)),
                ("expiration_date", ">", fields.Datetime.now()),
            ],
            limit=1,
        )
        if not device:
            return False
        device.write({"last_used_date": fields.Datetime.now()})
        return True
