# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
from datetime import timedelta
from unittest.mock import patch

from odoo import fields, http
from odoo.tests import HttpSavepointCase, tagged

CODE_PATH = (
    "odoo.addons.base_auth_mail_otp.models.res_users."
    "ResUsers._mail_otp_generate_code"
)
PARAM = "base_auth_mail_otp."
PASSWORD = "Otp#Glue-6tBs!Wd5"
FORM_URL = "/web/login/mail_otp"
CODE = "123456"


@tagged("post_install", "-at_install")
class TestLoginPasswordExpiration(HttpSavepointCase):
    """HTTP login tests of the password expiration after the email OTP."""

    @classmethod
    def setUpClass(cls):
        """Create users and enable the policy and password expiration."""
        super().setUpClass()
        params = cls.env["ir.config_parameter"].sudo()
        params.set_param(PARAM + "mail_otp_policy", "all_required")
        cls.env.company.sudo().password_expiration = 30
        cls.expired_user = cls._create_user("otp_pwd_expired", 60)
        cls.fresh_user = cls._create_user("otp_pwd_fresh", 0)
        cls.exempt_user = cls._create_user("otp_pwd_exempt", 60)
        cls.exempt_user.mail_otp_exempt = True
        cls.root_partner = cls.env.ref("base.partner_root")

    @classmethod
    def _create_user(cls, login, age_days):
        """Create an internal user with a password of the given age.

        :param login: login and base of the email of the new user
        :param age_days: age in days of the password
        :return: the new ``res.users`` record
        """
        user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": login,
                    "login": login,
                    "password": PASSWORD,
                    "email": "%s@example.com" % login,
                    "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
                }
            )
        )
        user.password_write_date = fields.Datetime.now() - timedelta(days=age_days)
        return user

    def setUp(self):
        """Patch the code generator so the code is predictable."""
        super().setUp()
        patcher = patch(CODE_PATH, return_value=CODE)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _csrf(self, response):
        """Read the CSRF token out of a rendered form.

        :param response: the response of a rendered page
        :return: the CSRF token
        """
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        self.assertTrue(match, "No CSRF token in the page")
        return match.group(1)

    def _password_login(self, user):
        """Post the password of the user and return the response.

        :param user: ``res.users`` record to log in
        :return: the redirect response of ``/web/login``
        """
        self.authenticate(None, None)
        return self.url_open(
            "/web/login",
            data={
                "login": user.login,
                "password": PASSWORD,
                "csrf_token": http.WebRequest.csrf_token(self),
            },
            allow_redirects=False,
        )

    def _post_code(self, user):
        """Do the password step, then post the right code.

        :param user: ``res.users`` record to log in
        :return: the response of the code form
        """
        response = self._password_login(user)
        self.assertIn(response.status_code, (302, 303))
        self.assertIn(FORM_URL, response.headers["Location"])
        page = self.url_open(FORM_URL)
        self.assertEqual(page.status_code, 200)
        return self.url_open(
            FORM_URL,
            data={"csrf_token": self._csrf(page), "mail_otp_code": CODE},
            allow_redirects=False,
        )

    def _assert_logged_in(self, logged_in):
        """Assert whether the session reaches the web client.

        :param logged_in: expected state of the session
        """
        response = self.url_open("/web", allow_redirects=False)
        self.assertEqual(response.status_code == 200, logged_in)

    def _assert_valid_reset(self, response, user):
        """Assert the redirect leads to a valid reset of the user.

        :param response: the redirect response to check
        :param user: ``res.users`` record owning the reset token
        """
        self.assertIn(response.status_code, (302, 303))
        match = re.search(r"token=([^&#]+)", response.headers["Location"])
        self.assertTrue(match, "No reset token in the redirect")
        # The HTTP request wrote the token through SQL in another thread,
        # so any value cached earlier in this test environment is stale.
        user.partner_id.invalidate_cache()
        partner = self.env["res.partner"]._signup_retrieve_partner(
            match.group(1), check_validity=True
        )
        self.assertEqual(partner, user.partner_id)

    def test_otp_user_expired_password_goes_to_valid_reset(self):
        """Assert the code step comes first, then the valid reset.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``) with P6 (L-15: the code generator is patched).
        """
        response = self._password_login(self.expired_user)
        self.assertIn(response.status_code, (302, 303))
        self.assertIn(FORM_URL, response.headers["Location"])
        self.assertFalse(self.expired_user.partner_id.signup_token)
        response = self._post_code(self.expired_user)
        self._assert_valid_reset(response, self.expired_user)
        self._assert_logged_in(False)

    def test_otp_user_fresh_password_reaches_web(self):
        """Assert a fresh password leads to the web client after the code.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``) with P6 (L-15: the code generator is patched).
        """
        response = self._post_code(self.fresh_user)
        self.assertIn(response.status_code, (302, 303))
        self.assertIn("/web", response.headers["Location"])
        self.assertNotIn("token=", response.headers["Location"])
        self._assert_logged_in(True)

    def test_exempt_user_expired_password_goes_to_valid_reset(self):
        """Assert an exempt user with an expired password gets a reset.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``).
        """
        response = self._password_login(self.exempt_user)
        self._assert_valid_reset(response, self.exempt_user)
        self._assert_logged_in(False)

    def test_superuser_partner_gets_no_signup_token(self):
        """Assert no login prepares a signup token for the superuser.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``) with P6 (L-15: the code generator is patched).
        """
        self._post_code(self.expired_user)
        self._password_login(self.exempt_user)
        self._post_code(self.fresh_user)
        self.root_partner.invalidate_cache()
        self.assertFalse(self.root_partner.signup_token)
