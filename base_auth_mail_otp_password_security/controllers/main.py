# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.password_security.controllers.main import PasswordSecurityHome
from odoo.addons.web.controllers.main import ensure_db


class MailOtpPasswordSecurityHome(PasswordSecurityHome):
    """Move the password expiration check after the full login."""

    @http.route()
    def web_login(self, *args, **kw):
        """Log in without the early password expiration check.

        ``PasswordSecurityHome.web_login`` is skipped on purpose: it
        checks the expiration right after the password step, while an
        OTP session is still partial and the environment user is the
        superuser. The check runs in ``_login_redirect`` instead.

        :return: the login response of the parent controllers
        """
        ensure_db()
        return super(PasswordSecurityHome, self).web_login(*args, **kw)

    def _login_redirect(self, uid, redirect=None):
        """Send the user to a valid reset when the password is expired.

        The check runs only when the session is complete
        (``request.session.uid`` is set), so it never runs while the
        email OTP step is still pending.

        :param uid: id of the user who logged in
        :param redirect: URL to open after login
        :return: the redirect URL, or the reset URL of the user
        """
        res = super()._login_redirect(uid, redirect=redirect)
        session_uid = request.session.uid
        if not session_uid:
            return res
        user = request.env["res.users"].sudo().browse(session_uid)
        if not user._password_has_expired():
            return res
        user.action_expire_password()
        request.session.logout(keep_db=True)
        request.params["login_success"] = False
        return user.partner_id.signup_url
