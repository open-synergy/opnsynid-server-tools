# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import patch

# HttpSavepointCase - NOT HttpCase on 14.0 (no ``cls.env`` in setUpClass).
from odoo.tests import HttpSavepointCase, tagged

CODE_PATH = (
    "odoo.addons.base_auth_mail_otp.models.res_users."
    "ResUsers._mail_otp_generate_code"
)


@tagged("post_install", "-at_install")
class TestUiResUsers(HttpSavepointCase):
    """Tour tests for the email OTP work instructions of ``res.users``."""

    @classmethod
    def setUpClass(cls):
        """Create the users the tours work with."""
        super().setUpClass()
        group_user = cls.env.ref("base.group_user")
        Users = cls.env["res.users"].with_context(no_reset_password=True)
        cls.exempt_user = Users.create(
            {
                "name": "Otp Exempt Tour User",
                "login": "otp_exempt_tour_user",
                "email": "otp_exempt_tour_user@example.com",
                "groups_id": [(6, 0, [group_user.id])],
            }
        )
        cls.login_user = Users.create(
            {
                "name": "Otp Login Tour User",
                "login": "otp_tour_user",
                "password": "Otp#Tour-4nHy!Pc8",
                "email": "otp_tour_user@example.com",
                "groups_id": [(6, 0, [group_user.id])],
            }
        )

    def test_configure_policy(self):
        """Run the configure policy tour for ``res.users``.

        IK: docs/res_users/01-configure-policy.md
        """
        self.start_tour(
            "/web", "base_auth_mail_otp_res_users_configure_policy", login="admin"
        )

    def test_exempt_user(self):
        """Run the exempt user tour for ``res.users``.

        IK: docs/res_users/02-exempt-user.md
        """
        self.start_tour(
            "/web", "base_auth_mail_otp_res_users_exempt_user", login="admin"
        )

    def test_login_email_code(self):
        """Run the login with an email code tour for ``res.users``.

        IK: docs/res_users/03-login-email-code.md
        """
        self.env["ir.config_parameter"].sudo().set_param(
            "base_auth_mail_otp.mail_otp_policy", "all_required"
        )
        with patch(CODE_PATH, return_value="123456"):
            self.start_tour(
                "/web/login",
                "base_auth_mail_otp_res_users_login_email_code",
                login=None,
            )
