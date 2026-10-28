# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.http import request
from odoo.tools import config

SESSION_KEY = "mail_otp_passkey_login"


class ResUsers(models.Model):
    _name = "res.users"
    _inherit = ["res.users"]

    def _check_credentials(self, password, env):
        """Mark the web session when the passkey was the credential used.

        ``super()`` raises ``AccessDenied`` for a wrong credential, so no
        mark is written in that case. Any other successful credential
        clears a mark left by an earlier passkey login, so a session can
        never carry the bypass over to a password login.

        :param password: the secret typed at the login form
        :param env: the user agent environment given by Odoo
        """
        super()._check_credentials(password, env)
        if not request:
            return
        passkey = config.get("auth_admin_passkey_password", False)
        if password and passkey and password == passkey:
            request.session[SESSION_KEY] = True
        else:
            request.session.pop(SESSION_KEY, None)

    def _mail_otp_passkey_session(self):
        """Tell whether the current web session was opened with the passkey.

        :return: ``True`` when a request exists and its session is marked
        """
        return bool(request and request.session.get(SESSION_KEY))

    def _mfa_type(self):
        """Return no MFA type for a session opened with the passkey.

        :return: ``None`` for a passkey session, otherwise ``super()``
        """
        if self._mail_otp_passkey_session():
            return None
        return super()._mfa_type()

    def _mfa_url(self):
        """Return no second step URL for a session opened with the passkey.

        An empty result lets ``odoo.http`` finalize the session at once.

        :return: ``None`` for a passkey session, otherwise ``super()``
        """
        if self._mail_otp_passkey_session():
            return None
        return super()._mfa_url()
