# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo_yaml_test import YamlTransactionCase

from odoo.tests import tagged

PARAM = "base_auth_mail_otp.mail_otp_policy"
TOTP_SECRET = base64.b32encode(b"coexistence-test-secret").decode()


@tagged("post_install", "-at_install")
class TestMfaCoexistenceModel(YamlTransactionCase):
    """MFA type and URL of ``res.users`` with the real ``auth_totp``."""

    def setUp(self):
        """Create an internal user with and one without Authenticator.

        The Authenticator is enabled by writing ``totp_secret`` as
        superuser, and the email OTP policy is set to
        ``employee_required``.
        """
        super().setUp()
        self.params = self.env["ir.config_parameter"].sudo()
        self.params.set_param(PARAM, "employee_required")
        group_user = self.env.ref("base.group_user")
        Users = self.env["res.users"].with_context(no_reset_password=True)
        values = {
            "email": "mfa_coexist@example.com",
            "groups_id": [(6, 0, [group_user.id])],
        }
        self.user_totp = Users.create(
            dict(values, name="Mfa Totp User", login="mfa_totp_user")
        )
        self.user_totp.sudo().write({"totp_secret": TOTP_SECRET})
        self.user_plain = Users.create(
            dict(values, name="Mfa Plain User", login="mfa_plain_user")
        )

    def test_authenticator_user_keeps_totp(self):
        """Assert a user with Authenticator keeps the app code step.

        Pure Python - trigger P9 (L-21: ``totp_secret`` can only be
        written through ``sudo()``) and P1 (L-01: the return values of
        ``_mfa_type`` and ``_mfa_url`` cannot be asserted from YAML).
        """
        self.assertTrue(self.user_totp.totp_enabled)
        self.assertEqual(self.user_totp._mfa_type(), "totp")
        self.assertEqual(self.user_totp._mfa_url(), "/web/login/totp")

    def test_user_without_authenticator_gets_mail_otp(self):
        """Assert a user without Authenticator gets the email OTP step.

        Pure Python - trigger P1 (L-01: the return values of
        ``_mfa_type`` and ``_mfa_url`` cannot be asserted from YAML).
        """
        self.assertFalse(self.user_plain.totp_enabled)
        self.assertEqual(self.user_plain._mfa_type(), "mail_otp")
        self.assertEqual(self.user_plain._mfa_url(), "/web/login/mail_otp")

    def test_policy_none(self):
        """Assert policy ``none`` leaves only the Authenticator active.

        Pure Python - trigger P1 (L-01: the return values of
        ``_mfa_type`` and ``_mfa_url`` cannot be asserted from YAML).
        """
        self.params.set_param(PARAM, "none")
        self.assertEqual(self.user_totp._mfa_type(), "totp")
        self.assertEqual(self.user_totp._mfa_url(), "/web/login/totp")
        self.assertIsNone(self.user_plain._mfa_type())
        self.assertIsNone(self.user_plain._mfa_url())
