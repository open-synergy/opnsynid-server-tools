# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from .mail_otp_challenge import MAIL_OTP_DEFAULTS, PARAM_PREFIX

TRUSTED_ACTIVE = "mail_otp_trusted_device_active"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    mail_otp_policy = fields.Selection(
        string="Email OTP Policy",
        selection=[
            ("none", "Disabled"),
            ("employee_required", "Internal users only"),
            ("all_required", "All users"),
        ],
        default=MAIL_OTP_DEFAULTS["mail_otp_policy"],
        config_parameter="base_auth_mail_otp.mail_otp_policy",
        help=(
            "Who must enter a code sent by email after the password. "
            "Disabled = nobody, Internal users only = users that are not "
            "portal, All users = everybody."
        ),
    )
    mail_otp_code_validity = fields.Integer(
        string="Code Validity (minutes)",
        default=MAIL_OTP_DEFAULTS["mail_otp_code_validity"],
        config_parameter="base_auth_mail_otp.mail_otp_code_validity",
        help="Minutes a code stays valid after it was sent.",
    )
    mail_otp_max_attempt = fields.Integer(
        string="Maximum Wrong Attempts",
        default=MAIL_OTP_DEFAULTS["mail_otp_max_attempt"],
        config_parameter="base_auth_mail_otp.mail_otp_max_attempt",
        help="Wrong codes allowed before the challenge is locked.",
    )
    mail_otp_resend_delay = fields.Integer(
        string="Resend Delay (seconds)",
        default=MAIL_OTP_DEFAULTS["mail_otp_resend_delay"],
        config_parameter="base_auth_mail_otp.mail_otp_resend_delay",
        help="Minimum seconds between two emails of the same challenge.",
    )
    mail_otp_max_mail_per_hour = fields.Integer(
        string="Maximum Emails per Hour",
        default=MAIL_OTP_DEFAULTS["mail_otp_max_mail_per_hour"],
        config_parameter="base_auth_mail_otp.mail_otp_max_mail_per_hour",
        help="Maximum codes emailed to one user within 60 minutes.",
    )
    mail_otp_trusted_device_active = fields.Boolean(
        string="Trusted Devices",
        default=MAIL_OTP_DEFAULTS[TRUSTED_ACTIVE],
        config_parameter="base_auth_mail_otp.mail_otp_trusted_device_active",
        help=(
            "Let users tick 'Trust this device' to skip the code on "
            "that browser. When unchecked every login asks for a code."
        ),
    )
    mail_otp_trusted_device_days = fields.Integer(
        string="Trusted Device Validity (days)",
        default=MAIL_OTP_DEFAULTS["mail_otp_trusted_device_days"],
        config_parameter="base_auth_mail_otp.mail_otp_trusted_device_days",
        help="Days a trusted device skips the code.",
    )

    @api.constrains(
        "mail_otp_code_validity",
        "mail_otp_max_attempt",
        "mail_otp_resend_delay",
        "mail_otp_max_mail_per_hour",
        "mail_otp_trusted_device_days",
    )
    def _check_mail_otp_positive_integer(self):
        """Reject Email OTP integer settings lower than 1.

        :raises ValidationError: when a setting is lower than 1
        """
        names = (
            "mail_otp_code_validity",
            "mail_otp_max_attempt",
            "mail_otp_resend_delay",
            "mail_otp_max_mail_per_hour",
            "mail_otp_trusted_device_days",
        )
        for record in self:
            for name in names:
                if record[name] < 1:
                    raise ValidationError(
                        _("%s must be at least 1.") % record._fields[name].string
                    )

    def get_values(self):
        """Return the settings values, with the real trusted device flag.

        Core stores a ``False`` boolean by deleting the parameter, which
        would read back as the default ``True``. The flag is therefore
        read from the explicit text written by ``set_values``.

        :return: dict of values for the non-classified fields
        """
        res = super().get_values()
        res[TRUSTED_ACTIVE] = self.env["mail_otp_challenge"]._mail_otp_get_param(
            TRUSTED_ACTIVE
        )
        return res

    def set_values(self):
        """Store the settings, keeping an explicit trusted device flag.

        The flag is written as the text ``True`` or ``False`` so that an
        unchecked box survives the default ``True``.
        """
        super().set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            PARAM_PREFIX + TRUSTED_ACTIVE,
            "True" if self.mail_otp_trusted_device_active else "False",
        )
