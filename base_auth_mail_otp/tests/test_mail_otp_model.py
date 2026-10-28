# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from unittest.mock import patch

from odoo_yaml_test import YamlTransactionCase

from odoo import fields
from odoo.tests import tagged

CODE_PATH = (
    "odoo.addons.base_auth_mail_otp.models.res_users."
    "ResUsers._mail_otp_generate_code"
)
SEND_PATH = "odoo.addons.base.models.ir_mail_server.IrMailServer.send_email"


@tagged("post_install", "-at_install")
class TestMailOtpModel(YamlTransactionCase):
    """Return value and mail tests for the email OTP models."""

    def setUp(self):
        """Create an internal and a portal user and reset the settings."""
        super().setUp()
        self.params = self.env["ir.config_parameter"].sudo()
        self.Challenge = self.env["mail_otp_challenge"]
        group_user = self.env.ref("base.group_user")
        group_portal = self.env.ref("base.group_portal")
        Users = self.env["res.users"].with_context(no_reset_password=True)
        self.internal = Users.create(
            {
                "name": "Otp Internal",
                "login": "otp_internal",
                "email": "otp_internal@example.com",
                "groups_id": [(6, 0, [group_user.id])],
            }
        )
        self.portal = Users.create(
            {
                "name": "Otp Portal",
                "login": "otp_portal",
                "email": "otp_portal@example.com",
                "groups_id": [(6, 0, [group_portal.id])],
            }
        )

    def _set_policy(self, policy):
        """Store the policy setting."""
        self.params.set_param("base_auth_mail_otp.mail_otp_policy", policy)

    def _answers(self, user):
        """Return the three MFA answers of the user as a tuple."""
        return (
            user._mfa_type(),
            user._mfa_url(),
            user._rpc_api_keys_only(),
        )

    def test_mfa_disabled_policy(self):
        """Assert the MFA answers are empty when the policy is disabled.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        return value of ``_mfa_type`` and its siblings).
        """
        self._set_policy("none")
        for user in (self.internal, self.portal):
            self.assertEqual(self._answers(user), (None, None, False))

    def test_mfa_employee_policy(self):
        """Assert only the internal user is asked for a code.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        return value of ``_mfa_type`` and its siblings).
        """
        self._set_policy("employee_required")
        self.assertEqual(
            self._answers(self.internal),
            ("mail_otp", "/web/login/mail_otp", True),
        )
        self.assertEqual(self._answers(self.portal), (None, None, False))

    def test_mfa_all_policy(self):
        """Assert both internal and portal users are asked for a code.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        return value of ``_mfa_type`` and its siblings).
        """
        self._set_policy("all_required")
        for user in (self.internal, self.portal):
            self.assertEqual(
                self._answers(user),
                ("mail_otp", "/web/login/mail_otp", True),
            )

    def test_mfa_exemption(self):
        """Assert permanent, future and lapsed exemptions.

        Pure Python - trigger P1 (L-01: the ``call`` action discards the
        return value of ``_mfa_type`` and its siblings).
        """
        self._set_policy("all_required")
        now = fields.Datetime.now()
        self.internal.write({"mail_otp_exempt": True})
        self.assertEqual(self._answers(self.internal), (None, None, False))
        self.internal.write({"mail_otp_exempt_until": now + timedelta(days=1)})
        self.assertEqual(self._answers(self.internal), (None, None, False))
        self.internal.write({"mail_otp_exempt_until": now - timedelta(days=1)})
        self.assertEqual(
            self._answers(self.internal),
            ("mail_otp", "/web/login/mail_otp", True),
        )

    def test_code_hash_is_not_the_code(self):
        """Assert only a keyed hash of the code is stored and a log written.

        Pure Python - trigger P6 (L-15: the generated code must be patched
        to a known value, and YAML has no patch support).
        """
        with patch(CODE_PATH, return_value="123456"):
            challenge = self.Challenge.create({"user_id": self.internal.id})
            challenge._issue_code()
        self.assertNotEqual(challenge.code_hash, "123456")
        self.assertEqual(len(challenge.code_hash), 64)
        self.assertEqual(
            challenge.code_hash, self.Challenge._mail_otp_hash(challenge.id, "123456")
        )
        sent = self.env["mail_otp_log"].search_count(
            [("challenge_id", "=", challenge.id), ("event", "=", "sent")]
        )
        self.assertEqual(sent, 1)

    def test_check_code_lifecycle(self):
        """Assert used, wrong, locked and expired outcomes of a challenge.

        Pure Python - trigger P1 (L-01: ``_check_code`` returns its outcome
        and the ``call`` action discards it) and P6 (L-15: the code is
        patched).
        """
        self.params.set_param("base_auth_mail_otp.mail_otp_max_attempt", "2")
        with patch(CODE_PATH, return_value="123456"):
            ok = self.Challenge.create({"user_id": self.internal.id})
            ok._issue_code()
            locked = self.Challenge.create({"user_id": self.internal.id})
            locked._issue_code()
            expired = self.Challenge.create({"user_id": self.internal.id})
            expired._issue_code()
        self.assertEqual(ok._check_code("123456"), "ok")
        self.assertEqual(ok.state, "used")
        self.assertEqual(ok._check_code("123456"), "used")
        self.assertEqual(locked._check_code("000000"), "wrong")
        self.assertEqual(locked._check_code("000000"), "locked")
        self.assertEqual(locked.state, "locked")
        self.assertEqual(locked._check_code("123456"), "locked")
        expired.write({"expiration_date": fields.Datetime.now() - timedelta(minutes=1)})
        self.assertEqual(expired._check_code("123456"), "expired")
        self.assertEqual(expired.state, "expired")
        events = (
            self.env["mail_otp_log"]
            .search([("challenge_id", "=", locked.id)])
            .mapped("event")
        )
        self.assertIn("locked", events)
        self.assertEqual(events.count("failure"), 2)

    def test_resend_rules(self):
        """Assert the resend delay and the hourly mail limit.

        Pure Python - trigger P1 (L-01: ``_resend_error`` returns the
        refusal text and the ``call`` action discards it).
        """
        self.params.set_param("base_auth_mail_otp.mail_otp_resend_delay", "60")
        self.params.set_param("base_auth_mail_otp.mail_otp_max_mail_per_hour", "2")
        challenge = self.Challenge.create({"user_id": self.internal.id})
        challenge._issue_code()
        self.assertTrue(challenge._resend_error())
        challenge.write(
            {"last_sent_date": fields.Datetime.now() - timedelta(seconds=120)}
        )
        self.assertFalse(challenge._resend_error())
        challenge._issue_code()
        challenge.write(
            {"last_sent_date": fields.Datetime.now() - timedelta(seconds=120)}
        )
        self.assertTrue(challenge._resend_error())

    def test_failed_mail_does_not_keep_the_code(self):
        """Assert a mail that failed to send does not contain the code.

        Pure Python - trigger P6 (L-15: the mail server must be patched to
        fail, and YAML has no patch support).
        """
        with patch(CODE_PATH, return_value="654321"), patch(
            SEND_PATH, side_effect=Exception("smtp down")
        ):
            challenge = self.Challenge.create({"user_id": self.internal.id})
            challenge._issue_code()
        mails = self.env["mail.mail"].search(
            [("email_to", "ilike", "otp_internal@example.com")]
        )
        self.assertTrue(mails)
        for mail in mails:
            self.assertNotIn("654321", mail.body_html or "")
            self.assertNotIn("654321", mail.body or "")
        messages = self.env["mail.message"].search([("body", "ilike", "654321")])
        self.assertFalse(messages)

    def test_sent_mail_is_deleted(self):
        """Assert a successfully sent mail leaves nothing behind.

        Pure Python - trigger P6 (L-15: the generated code must be patched
        so the leftover search can look for it).
        """
        with patch(CODE_PATH, return_value="777777"):
            challenge = self.Challenge.create({"user_id": self.internal.id})
            challenge._issue_code()
        self.assertFalse(
            self.env["mail.mail"].search([("body_html", "ilike", "777777")])
        )
        self.assertFalse(self.env["mail.message"].search([("body", "ilike", "777777")]))
