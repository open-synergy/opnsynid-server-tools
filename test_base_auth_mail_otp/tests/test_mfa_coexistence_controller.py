# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import http
from odoo.tests import HttpSavepointCase, tagged

PARAM = "base_auth_mail_otp.mail_otp_policy"
PASSWORD = "Tq7#Rk-5nVb!Hy8Wz2"
TOTP_SECRET = base64.b32encode(b"coexistence-test-secret").decode()
TOTP_LOGIN = "mfa_http_totp"
PLAIN_LOGIN = "mfa_http_plain"
TOTP_EMAIL = "mfa_http_totp@example.com"
PLAIN_EMAIL = "mfa_http_plain@example.com"


@tagged("post_install", "-at_install")
class TestMfaCoexistenceController(HttpSavepointCase):
    """Password login step with the real ``auth_totp`` installed."""

    @classmethod
    def setUpClass(cls):
        """Create the users and set the policy to ``employee_required``.

        One internal user gets the Authenticator enabled by writing
        ``totp_secret`` as superuser; the other has none.
        """
        super().setUpClass()
        cls.env["ir.config_parameter"].sudo().set_param(PARAM, "employee_required")
        group_user = cls.env.ref("base.group_user")
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.user_totp = Users.create(
            {
                "name": "Mfa Http Totp",
                "login": TOTP_LOGIN,
                "password": PASSWORD,
                "email": TOTP_EMAIL,
                "groups_id": [(6, 0, [group_user.id])],
            }
        )
        cls.user_totp.sudo().write({"totp_secret": TOTP_SECRET})
        cls.user_plain = Users.create(
            {
                "name": "Mfa Http Plain",
                "login": PLAIN_LOGIN,
                "password": PASSWORD,
                "email": PLAIN_EMAIL,
                "groups_id": [(6, 0, [group_user.id])],
            }
        )

    def _password_login(self, login):
        """Post the password step of the login and return the response.

        :param login: login of the user
        :return: the redirect response, not followed
        """
        self.authenticate(None, None)
        return self.url_open(
            "/web/login",
            data={
                "login": login,
                "password": PASSWORD,
                "csrf_token": http.WebRequest.csrf_token(self),
            },
            allow_redirects=False,
        )

    def _otp_mail_count(self, user):
        """Count the OTP mails queued for a user.

        :param user: ``res.users`` record
        :return: number of ``mail.mail`` made from the OTP template
        """
        return (
            self.env["mail.mail"]
            .sudo()
            .search_count(
                [
                    ("email_to", "ilike", user.email),
                    ("subject", "=", "Your verification code"),
                ]
            )
        )

    def _otp_log_count(self, user, event=None):
        """Count the OTP audit log entries of a user.

        :param user: ``res.users`` record
        :param event: optional event to filter on
        :return: number of ``mail_otp_log`` records
        """
        domain = [("user_id", "=", user.id)]
        if event:
            domain.append(("event", "=", event))
        return self.env["mail_otp_log"].sudo().search_count(domain)

    def test_authenticator_user_is_sent_to_totp(self):
        """Assert the password login of an Authenticator user asks the app.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``).
        """
        response = self._password_login(TOTP_LOGIN)
        self.assertIn(response.status_code, (302, 303))
        self.assertIn("/web/login/totp", response.headers["Location"])
        self.assertNotIn("/web/login/mail_otp", response.headers["Location"])
        challenges = self.env["mail_otp_challenge"].sudo()
        self.assertEqual(
            challenges.search_count([("user_id", "=", self.user_totp.id)]), 0
        )

    def test_user_without_authenticator_is_sent_to_mail_otp(self):
        """Assert the password login of a user without app asks the email.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``).
        """
        response = self._password_login(PLAIN_LOGIN)
        self.assertIn(response.status_code, (302, 303))
        self.assertIn("/web/login/mail_otp", response.headers["Location"])
        self.assertNotIn("/web/login/totp", response.headers["Location"])

    def test_authenticator_login_sends_no_email(self):
        """Assert no OTP email is sent while an Authenticator user logs in.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``).
        """
        self._password_login(TOTP_LOGIN)
        page = self.url_open("/web/login/totp")
        self.assertEqual(page.status_code, 200)
        self.assertEqual(self._otp_mail_count(self.user_totp), 0)
        self.assertEqual(self._otp_log_count(self.user_totp), 0)
        self.assertEqual(self._otp_log_count(self.user_totp, "sent"), 0)
