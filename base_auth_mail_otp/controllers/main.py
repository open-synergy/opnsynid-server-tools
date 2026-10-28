# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, http
from odoo.exceptions import UserError
from odoo.http import request

from odoo.addons.web.controllers.main import Home

TRUSTED_DEVICE_COOKIE = "mail_otp_td"
SESSION_KEY = "mail_otp_challenge_id"


class MailOtpHome(Home):
    """
    Adds the second login step of the email OTP: the form where the user
    types the code received by email, and the route to request a new one.
    """

    def _mail_otp_pre_user(self):
        """Return the user who passed the password step of the login.

        The user is returned only while the session is still partial
        (``pre_uid``) and the email OTP is the pending second step, so
        that this route can never replace another second factor.

        :return: a ``res.users`` record (sudo), empty when not applicable
        """
        users = request.env["res.users"].sudo()
        pre_uid = request.session.get("pre_uid")
        if not pre_uid:
            return users
        user = users.browse(pre_uid).exists()
        if user and user._mfa_type() == "mail_otp":
            return user
        return users

    def _mail_otp_challenge(self, user):
        """Return the challenge bound to the session for the user.

        :param user: ``res.users`` record
        :return: a ``mail_otp_challenge`` record, empty if none
        """
        challenges = request.env["mail_otp_challenge"].sudo()
        challenge_id = request.session.get(SESSION_KEY)
        if not challenge_id:
            return challenges
        challenge = challenges.browse(challenge_id).exists()
        if challenge and challenge.user_id == user:
            return challenge
        return challenges

    def _mail_otp_new_challenge(self, user):
        """Open a new challenge for the user and email its code.

        :param user: ``res.users`` record
        :return: tuple ``(challenge, error)``; ``error`` is ``False`` when
            the code was sent
        """
        model = request.env["mail_otp_challenge"].sudo()
        if model._mail_otp_hourly_limit_reached(user):
            return model, _("Too many codes were sent. Please try again later.")
        values = model._mail_otp_request_info()
        values["user_id"] = user.id
        challenge = model.create(values)
        try:
            challenge._issue_code()
        except UserError as exc:
            return challenge, exc.args[0]
        request.session[SESSION_KEY] = challenge.id
        return challenge, False

    def _mail_otp_mask_email(self, email):
        """Hide most of an email address for display.

        :param email: the address to mask
        :return: the address with the local part partly replaced by ``*``
        """
        if not email or "@" not in email:
            return ""
        local, _sep, domain = email.partition("@")
        return "%s***@%s" % (local[:1], domain)

    def _mail_otp_render(self, user, challenge, redirect, error=None, notice=None):
        """Render the code form.

        :param user: ``res.users`` record in the second login step
        :param challenge: the current ``mail_otp_challenge`` record
        :param redirect: URL to open after login
        :param error: optional error text to show
        :param notice: optional information text to show
        :return: the rendered response
        """
        model = request.env["mail_otp_challenge"].sudo()
        locked = bool(challenge and challenge.state == "locked")
        return request.render(
            "base_auth_mail_otp.mail_otp_form",
            {
                "error": error,
                "notice": notice,
                "redirect": redirect,
                "can_verify": bool(user.email) and not locked,
                "masked_email": self._mail_otp_mask_email(user.email),
                "trusted_device_active": model._mail_otp_get_param(
                    "mail_otp_trusted_device_active"
                ),
                "trusted_device_days": model._mail_otp_get_param(
                    "mail_otp_trusted_device_days"
                ),
            },
        )

    def _mail_otp_finish(self, user, redirect, challenge, remember=False):
        """Complete the login after a valid code or trusted device.

        :param user: ``res.users`` record that passed the second step
        :param redirect: URL to open after login
        :param challenge: the used challenge, may be empty
        :param remember: ``True`` to register the browser as trusted
        :return: the redirect response, with the trusted device cookie
            when requested and the feature is active
        """
        model = request.env["mail_otp_challenge"].sudo()
        trusted_active = model._mail_otp_get_param("mail_otp_trusted_device_active")
        request.session.pop(SESSION_KEY, None)
        request.session.finalize()
        response = http.redirect_with_hash(
            self._login_redirect(request.session.uid, redirect=redirect)
        )
        if remember and trusted_active:
            token = request.env["mail_otp_trusted_device"]._create_device(user)
            days = model._mail_otp_get_param("mail_otp_trusted_device_days")
            response.set_cookie(
                key=TRUSTED_DEVICE_COOKIE,
                value=token,
                max_age=days * 86400,
                httponly=True,
                samesite="Lax",
                secure=request.httprequest.scheme == "https",
            )
        return response

    @http.route(
        "/web/login/mail_otp",
        type="http",
        auth="public",
        methods=["GET", "POST"],
        sitemap=False,
        website=True,
        multilang=False,
    )
    def web_login_mail_otp(self, redirect=None, **kwargs):
        """Show and process the email OTP step of the login.

        GET reuses a pending challenge of the session without sending a
        new email, or opens a new one (one email). A valid trusted device
        cookie skips the step. POST validates the code and never sends an
        email, whatever the result.

        :param redirect: URL to open after login
        :return: the form, or a redirect when the login is complete
        """
        if request.session.uid:
            return http.redirect_with_hash(
                self._login_redirect(request.session.uid, redirect=redirect)
            )
        user = self._mail_otp_pre_user()
        if not user:
            return http.redirect_with_hash("/web/login")
        model = request.env["mail_otp_challenge"].sudo()
        challenge = self._mail_otp_challenge(user)
        if request.httprequest.method == "POST":
            return self._mail_otp_post(user, challenge, redirect, kwargs)
        trusted_active = model._mail_otp_get_param("mail_otp_trusted_device_active")
        token = request.httprequest.cookies.get(TRUSTED_DEVICE_COOKIE)
        if trusted_active and request.env["mail_otp_trusted_device"]._check_token(
            token, user
        ):
            request.env["mail_otp_log"].sudo()._add_log(
                user, challenge, "success", note="trusted device"
            )
            return self._mail_otp_finish(user, redirect, challenge)
        error = None
        if not user.email:
            error = _("Your account has no email address. Contact the administrator.")
        elif challenge and challenge.state == "locked":
            error = self._mail_otp_message("locked")
        elif not (challenge and challenge._is_usable()):
            challenge, error = self._mail_otp_new_challenge(user)
        return self._mail_otp_render(user, challenge, redirect, error=error)

    def _mail_otp_message(self, result):
        """Return the text shown for a failed validation result.

        :param result: one of ``wrong``, ``locked``, ``expired``, ``used``
        :return: the message text
        """
        messages = {
            "wrong": _("Verification failed, please check the 6-digit code."),
            "locked": _("Too many wrong codes. Sign in again to get a new code."),
            "expired": _("The code has expired. Request a new one."),
            "used": _("This code has already been used. Sign in again."),
        }
        return messages[result]

    def _mail_otp_post(self, user, challenge, redirect, kwargs):
        """Validate the code posted from the form.

        :param user: ``res.users`` in the second login step
        :param challenge: the challenge bound to the session, may be empty
        :param redirect: URL to open after login
        :param kwargs: the posted form values
        :return: the form with an error, or the login redirect
        """
        if not challenge:
            return self._mail_otp_render(
                user, challenge, redirect, error=self._mail_otp_message("expired")
            )
        code = re.sub(r"\s", "", kwargs.get("mail_otp_code") or "")
        result = challenge._check_code(code)
        if result == "ok":
            return self._mail_otp_finish(
                user, redirect, challenge, remember=bool(kwargs.get("remember"))
            )
        return self._mail_otp_render(
            user, challenge, redirect, error=self._mail_otp_message(result)
        )

    @http.route(
        "/web/login/mail_otp/resend",
        type="http",
        auth="public",
        methods=["POST"],
        sitemap=False,
        website=True,
        multilang=False,
    )
    def web_login_mail_otp_resend(self, redirect=None, **kwargs):
        """Email a new code on the same challenge.

        The code and the expiration date are replaced; the wrong attempt
        counter is kept. Refused while the resend delay has not passed or
        when the hourly mail limit is reached.

        :param redirect: URL to open after login
        :return: the form with the result of the request
        """
        if request.session.uid:
            return http.redirect_with_hash(
                self._login_redirect(request.session.uid, redirect=redirect)
            )
        user = self._mail_otp_pre_user()
        if not user:
            return http.redirect_with_hash("/web/login")
        challenge = self._mail_otp_challenge(user)
        error = notice = None
        if not user.email:
            error = _("Your account has no email address. Contact the administrator.")
        elif challenge and challenge.state in ("locked", "used"):
            error = self._mail_otp_message(challenge.state)
        elif challenge:
            error = challenge._resend_error()
            if not error:
                challenge._issue_code()
                notice = _("A new code has been sent.")
        else:
            challenge, error = self._mail_otp_new_challenge(user)
            if not error:
                notice = _("A new code has been sent.")
        return self._mail_otp_render(
            user, challenge, redirect, error=error, notice=notice
        )
