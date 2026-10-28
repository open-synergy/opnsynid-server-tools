# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo import http
from odoo.tests import HttpSavepointCase, get_db_name, tagged
from odoo.tools import config

PARAM = "base_auth_mail_otp."
LOGIN = "otp_passkey_user"
PASSWORD = "Wq7#Lm-2xRt!Zk9vNb"
PASSKEY = "Pk#Adm-7wRt!Qz4xHd"
FORM_URL = "/web/login/mail_otp"


@tagged("post_install", "-at_install")
class TestAdminPasskey(HttpSavepointCase):
    """HTTP flow tests of the administrator passkey with the email OTP."""

    @classmethod
    def setUpClass(cls):
        """Create a user, enable the policy and configure the passkey."""
        super().setUpClass()
        cls.params = cls.env["ir.config_parameter"].sudo()
        cls.params.set_param(PARAM + "mail_otp_policy", "all_required")
        cls.user = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Otp Passkey User",
                    "login": LOGIN,
                    "password": PASSWORD,
                    "email": "otp_passkey_user@example.com",
                    "groups_id": [(6, 0, [cls.env.ref("base.group_user").id])],
                }
            )
        )

    def setUp(self):
        """Configure the passkey for the duration of one test."""
        super().setUp()
        patcher = patch.dict(config.options, {"auth_admin_passkey_password": PASSKEY})
        patcher.start()
        self.addCleanup(patcher.stop)

    def _challenges(self):
        """Return the email OTP challenges of the test user."""
        return self.env["mail_otp_challenge"].search([("user_id", "=", self.user.id)])

    def _login(self, password, fresh_session=True):
        """Post the login form and return the redirect response.

        :param password: the secret typed in the password field
        :param fresh_session: when ``True`` start from an anonymous session
        """
        if fresh_session:
            self.authenticate(None, None)
        return self.url_open(
            "/web/login",
            data={
                "login": LOGIN,
                "password": password,
                "csrf_token": http.WebRequest.csrf_token(self),
            },
            allow_redirects=False,
        )

    def _assert_logged_in(self, logged_in):
        """Assert whether the session reaches the web client.

        :param logged_in: the expected state of the session
        """
        response = self.url_open("/web", allow_redirects=False)
        self.assertEqual(response.status_code == 200, logged_in)

    def test_passkey_login_skips_otp(self):
        """Assert the passkey login reaches the web client with no code.

        Pure Python - trigger P7 (L-19: login routes need an ``HttpCase``).
        """
        response = self._login(PASSKEY)
        self.assertIn(response.status_code, (302, 303))
        self.assertNotIn(FORM_URL, response.headers["Location"])
        self._assert_logged_in(True)
        self.assertFalse(self._challenges())
        self.assertFalse(
            self.env["mail_otp_log"].search_count([("user_id", "=", self.user.id)])
        )

    def test_password_login_still_asks_otp(self):
        """Assert the real password of the same user still asks for a code.

        Pure Python - trigger P7 (L-19: login routes need an ``HttpCase``).
        """
        response = self._login(PASSWORD)
        self.assertIn(response.status_code, (302, 303))
        self.assertIn(FORM_URL, response.headers["Location"])
        self._assert_logged_in(False)

    def test_password_login_after_passkey_login_asks_otp(self):
        """Assert a passkey login leaves no bypass for the next login.

        The second login reuses the very same session, with the real
        password of the user.

        Pure Python - trigger P7 (L-19: login routes need an ``HttpCase``).
        """
        self._login(PASSKEY)
        self._assert_logged_in(True)
        response = self._login(PASSWORD, fresh_session=False)
        self.assertIn(response.status_code, (302, 303))
        self.assertIn(FORM_URL, response.headers["Location"])

    def test_wrong_password_is_refused(self):
        """Assert a secret that is not the password nor the passkey fails.

        Pure Python - trigger P7 (L-19: login routes need an ``HttpCase``).
        """
        response = self._login("not_the_password")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Wrong login/password", response.text)
        self._assert_logged_in(False)
        self.assertFalse(self._challenges())

    def test_rpc_password_refused(self):
        """Assert XML-RPC refuses the real password of a covered user.

        Pure Python - trigger P7 (L-19: RPC endpoints need an
        ``HttpCase``).
        """
        self.assertFalse(
            self.xmlrpc_common.authenticate(get_db_name(), LOGIN, PASSWORD, {}),
            "Password RPC must stay refused for users with the email OTP",
        )
