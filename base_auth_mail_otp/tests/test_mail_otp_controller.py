# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re
from datetime import timedelta
from unittest.mock import patch

from odoo import fields, http
from odoo.tests import HttpSavepointCase, get_db_name, tagged

CODE_PATH = (
    "odoo.addons.base_auth_mail_otp.models.res_users."
    "ResUsers._mail_otp_generate_code"
)
PARAM = "base_auth_mail_otp."
LOGIN = "otp_http_user"
PASSWORD = "otp_http_pass_1"
EMAIL = "otp_http_user@example.com"
FORM_URL = "/web/login/mail_otp"
RESEND_URL = "/web/login/mail_otp/resend"


@tagged("post_install", "-at_install")
class TestMailOtpController(HttpSavepointCase):
    """HTTP flow tests of the email OTP login step."""

    @classmethod
    def setUpClass(cls):
        """Create a user and enable the policy for every user."""
        super().setUpClass()
        cls.params = cls.env["ir.config_parameter"].sudo()
        cls.params.set_param(PARAM + "mail_otp_policy", "all_required")
        cls.params.set_param(PARAM + "mail_otp_max_attempt", "3")
        cls.params.set_param(PARAM + "mail_otp_trusted_device_active", "True")
        cls.user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Otp Http User",
                    "login": LOGIN,
                    "password": PASSWORD,
                    "email": EMAIL,
                    "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
                }
            )
        )

    def setUp(self):
        """Patch the code generator so every code is predictable."""
        super().setUp()
        self.generated = []

        def _fake_code():
            """Return the next predictable code and remember it."""
            code = "%06d" % (123456 + len(self.generated))
            self.generated.append(code)
            return code

        patcher = patch(CODE_PATH, side_effect=_fake_code)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _challenges(self):
        """Return the challenges of the test user."""
        return self.env["mail_otp_challenge"].search([("user_id", "=", self.user.id)])

    def _sent_count(self):
        """Return how many codes were emailed to the test user."""
        return self.env["mail_otp_log"].search_count(
            [("user_id", "=", self.user.id), ("event", "=", "sent")]
        )

    def _csrf(self, response):
        """Read the CSRF token out of a rendered form."""
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        self.assertTrue(match, "No CSRF token in the page")
        return match.group(1)

    def _password_login(self):
        """Post the password and return the redirect response."""
        self.authenticate(None, None)
        return self.url_open(
            "/web/login",
            data={
                "login": LOGIN,
                "password": PASSWORD,
                "csrf_token": http.WebRequest.csrf_token(self),
            },
            allow_redirects=False,
        )

    def _open_form(self):
        """Do the password step, open the code page and return it."""
        response = self._password_login()
        self.assertIn(response.status_code, (302, 303))
        self.assertIn(FORM_URL, response.headers["Location"])
        page = self.url_open(FORM_URL)
        self.assertEqual(page.status_code, 200)
        return page

    def _post_code(self, page, code, **extra):
        """Post a code using the CSRF token of the given page."""
        data = {"csrf_token": self._csrf(page), "mail_otp_code": code}
        data.update(extra)
        return self.url_open(FORM_URL, data=data, allow_redirects=False)

    def _post_resend(self, page):
        """Post the resend form of the given page."""
        return self.url_open(
            RESEND_URL,
            data={"csrf_token": self._csrf(page)},
            allow_redirects=False,
        )

    def _assert_logged_in(self, logged_in):
        """Assert whether the session reaches the web client."""
        response = self.url_open("/web", allow_redirects=False)
        self.assertEqual(response.status_code == 200, logged_in)

    def test_correct_code_logs_in(self):
        """Assert the right code finishes the login with one email only.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``).
        """
        page = self._open_form()
        self.assertEqual(self._sent_count(), 1)
        self._assert_logged_in(False)
        response = self._post_code(page, self.generated[0])
        self.assertIn(response.status_code, (302, 303))
        self._assert_logged_in(True)
        self.assertEqual(self._sent_count(), 1)
        self.assertEqual(self._challenges().state, "used")
        events = (
            self.env["mail_otp_log"]
            .search([("user_id", "=", self.user.id)])
            .mapped("event")
        )
        self.assertIn("success", events)

    def test_render_again_sends_no_mail(self):
        """Assert reopening the page reuses the pending challenge.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``).
        """
        self._open_form()
        self.url_open(FORM_URL)
        self.url_open(FORM_URL)
        self.assertEqual(self._sent_count(), 1)
        self.assertEqual(len(self._challenges()), 1)

    def test_wrong_codes_lock_the_challenge(self):
        """Assert wrong codes send no mail and lock at the maximum.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``).
        """
        page = self._open_form()
        for _attempt in range(3):
            response = self._post_code(page, "000000")
            self.assertEqual(response.status_code, 200)
            page = response
        self.assertEqual(self._challenges().state, "locked")
        self.assertIn("Too many wrong codes", page.text)
        response = self._post_code(page, self.generated[0])
        self.assertEqual(response.status_code, 200)
        self._assert_logged_in(False)
        self.url_open(FORM_URL)
        self.assertEqual(self._sent_count(), 1)

    def test_expired_code_is_rejected(self):
        """Assert a code that passed its validity is refused.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``).
        """
        page = self._open_form()
        self._challenges().write(
            {"expiration_date": fields.Datetime.now() - timedelta(minutes=1)}
        )
        response = self._post_code(page, self.generated[0])
        self.assertEqual(response.status_code, 200)
        self.assertIn("expired", response.text)
        self.assertEqual(self._challenges().state, "expired")
        self._assert_logged_in(False)

    def test_resend_respects_delay_and_hourly_limit(self):
        """Assert resend keeps the challenge and obeys both limits.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``).
        """
        self.params.set_param(PARAM + "mail_otp_resend_delay", "60")
        self.params.set_param(PARAM + "mail_otp_max_mail_per_hour", "2")
        page = self._open_form()
        challenge = self._challenges()
        response = self._post_resend(page)
        self.assertIn("Please wait", response.text)
        self.assertEqual(self._sent_count(), 1)
        challenge.write({"attempt_count": 1})
        challenge.write(
            {"last_sent_date": fields.Datetime.now() - timedelta(seconds=120)}
        )
        old_hash = challenge.code_hash
        response = self._post_resend(response)
        self.assertIn("A new code has been sent", response.text)
        self.assertEqual(self._sent_count(), 2)
        challenge.invalidate_cache()
        self.assertEqual(self._challenges(), challenge)
        self.assertNotEqual(challenge.code_hash, old_hash)
        self.assertEqual(challenge.attempt_count, 1)
        challenge.write(
            {"last_sent_date": fields.Datetime.now() - timedelta(seconds=120)}
        )
        response = self._post_resend(response)
        self.assertIn("Too many codes", response.text)
        self.assertEqual(self._sent_count(), 2)

    def test_user_without_email_cannot_finish(self):
        """Assert a user without email gets an error and no mail.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``).
        """
        self.user.partner_id.write({"email": False})
        page = self._open_form()
        self.assertIn("no email address", page.text)
        self.assertEqual(self._sent_count(), 0)
        self._assert_logged_in(False)

    def test_trusted_device_cookie(self):
        """Assert a trusted device skips the code only while enabled.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``).
        """
        page = self._open_form()
        response = self._post_code(page, self.generated[0], remember="1")
        token = response.cookies.get("mail_otp_td")
        self.assertTrue(token)
        self.assertEqual(
            self.env["mail_otp_trusted_device"].search_count(
                [("user_id", "=", self.user.id)]
            ),
            1,
        )
        self.assertEqual(self._sent_count(), 1)
        # Second login on the same browser: the code is skipped.
        self._password_login()
        self.opener.cookies.set("mail_otp_td", token)
        skipped = self.url_open(FORM_URL, allow_redirects=False)
        self.assertIn(skipped.status_code, (302, 303))
        self.assertEqual(self._sent_count(), 1)
        self._assert_logged_in(True)
        # Feature disabled: the cookie is ignored and a code is mailed.
        self.params.set_param(PARAM + "mail_otp_trusted_device_active", "False")
        self._password_login()
        self.opener.cookies.set("mail_otp_td", token)
        page = self.url_open(FORM_URL)
        self.assertEqual(page.status_code, 200)
        self.assertEqual(self._sent_count(), 2)
        self._assert_logged_in(False)

    def test_rpc_password_refused_and_api_key_accepted(self):
        """Assert XML-RPC refuses the password but accepts an API key.

        Pure Python - trigger P7 (L-19: RPC endpoints need an
        ``HttpCase``).
        """
        db = get_db_name()
        self.assertFalse(
            self.xmlrpc_common.authenticate(db, LOGIN, PASSWORD, {}),
            "Password RPC must be refused for users with the email OTP",
        )
        key = (
            self.env["res.users.apikeys"]
            .with_user(self.user)
            ._generate("rpc", "email otp test")
        )
        self.assertEqual(
            self.xmlrpc_common.authenticate(db, LOGIN, key, {}), self.user.id
        )

    def test_otp_route_needs_the_otp_step(self):
        """Assert the code route is closed to a session without pre_uid.

        Pure Python - trigger P7 (L-19: controller routes need an
        ``HttpCase``).
        """
        self.authenticate(None, None)
        response = self.url_open(FORM_URL, allow_redirects=False)
        self.assertIn(response.status_code, (302, 303))
        self.assertIn("/web/login", response.headers["Location"])
        self.assertEqual(self._sent_count(), 0)
