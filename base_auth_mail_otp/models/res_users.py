# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import secrets

from odoo import api, fields, models


class ResUsers(models.Model):
    _name = "res.users"
    _inherit = ["res.users"]

    mail_otp_exempt = fields.Boolean(
        string="Exempt from Email OTP",
        default=False,
        groups="base.group_system",
        help=(
            "Check to let this user log in without the email code. "
            "Without an expiration date the exemption is permanent."
        ),
    )
    mail_otp_exempt_until = fields.Datetime(
        string="Exempt Until",
        groups="base.group_system",
        help=(
            "Optional. When filled and already passed, the exemption "
            "lapses automatically. Use it as a temporary exemption, for "
            "example while the email server is not working."
        ),
    )

    @api.model
    def _mail_otp_generate_code(self):
        """Generate a random 6-digit numeric code.

        Kept as a separate method so that tests and tours can patch it to
        get a deterministic code.

        :return: a string of exactly six digits
        """
        return "%06d" % secrets.randbelow(1000000)

    def _mail_otp_is_exempt(self):
        """Tell whether the user is currently exempt from the email OTP.

        :return: ``True`` when ``mail_otp_exempt`` is set and the optional
            ``mail_otp_exempt_until`` date is empty or in the future
        """
        self.ensure_one()
        user = self.sudo()
        if not user.mail_otp_exempt:
            return False
        until = user.mail_otp_exempt_until
        return not until or until > fields.Datetime.now()

    def _mail_otp_required(self):
        """Tell whether the email OTP applies to the user.

        Applies when the policy is ``all_required``, or ``employee_required``
        and the user is internal (``not share``; Odoo 14.0 has no
        ``_is_internal``), and the user is not exempt.

        :return: ``True`` when the user must enter an email code
        """
        self.ensure_one()
        policy = self.env["mail_otp_challenge"]._mail_otp_get_param("mail_otp_policy")
        if policy == "none":
            return False
        if policy == "employee_required" and self.sudo().share:
            return False
        return not self._mail_otp_is_exempt()

    def _mfa_type(self):
        """Return ``mail_otp`` when the user must enter an email code.

        Another MFA type returned by ``super()`` (for example the
        Authenticator) always wins. The explicit ``totp_enabled`` guard
        covers the case where ``auth_totp`` sits below this module in the
        MRO, so it can answer instead.

        :return: ``mail_otp``, the type of another MFA, or ``None``
        """
        result = super()._mfa_type()
        if result is not None or len(self) != 1:
            return result
        if "totp_enabled" in self._fields and self.sudo().totp_enabled:
            return None
        if self._mail_otp_required():
            return "mail_otp"
        return None

    def _mfa_url(self):
        """Return the URL of the email OTP step when it applies.

        :return: ``/web/login/mail_otp``, the URL of another MFA, or
            ``None``
        """
        result = super()._mfa_url()
        if result is not None:
            return result
        if self._mfa_type() == "mail_otp":
            return "/web/login/mail_otp"
        return None

    def _rpc_api_keys_only(self):
        """Restrict RPC to API keys for users who need the email code.

        :return: ``True`` when the MFA type is ``mail_otp``, otherwise
            the value of ``super()``
        """
        if len(self) == 1 and self._mfa_type() == "mail_otp":
            return True
        return super()._rpc_api_keys_only()
