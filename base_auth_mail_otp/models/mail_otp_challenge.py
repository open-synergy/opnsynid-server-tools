# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import hmac
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.http import request

PARAM_PREFIX = "base_auth_mail_otp."

MAIL_OTP_POLICIES = ("none", "employee_required", "all_required")

MAIL_OTP_DEFAULTS = {
    "mail_otp_policy": "none",
    "mail_otp_code_validity": 10,
    "mail_otp_max_attempt": 5,
    "mail_otp_resend_delay": 60,
    "mail_otp_max_mail_per_hour": 5,
    "mail_otp_trusted_device_active": True,
    "mail_otp_trusted_device_days": 30,
}


class MailOtpChallenge(models.Model):
    """
    Represents one email OTP challenge issued to a user during login.
    A challenge is bound to the login session, stores only a keyed hash of
    the 6-digit code and tracks its expiration, wrong attempts and state.
    It also holds the helpers that read the module configuration.
    """

    _name = "mail_otp_challenge"
    _description = "Email OTP Challenge"
    _order = "id desc"

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        ondelete="cascade",
        index=True,
        help="User who has to enter the code to finish the login.",
    )
    code_hash = fields.Char(
        string="Code Hash",
        readonly=True,
        help="HMAC-SHA256 of the code. The plain code is never stored.",
    )
    expiration_date = fields.Datetime(
        string="Expiration Date",
        readonly=True,
        help="The code is rejected after this date and time.",
    )
    last_sent_date = fields.Datetime(
        string="Last Sent Date",
        readonly=True,
        help="Date and time the code was last sent by email.",
    )
    attempt_count = fields.Integer(
        string="Wrong Attempts",
        readonly=True,
        default=0,
        help="Number of wrong codes entered for this challenge.",
    )
    ip_address = fields.Char(
        string="IP Address",
        readonly=True,
        help="IP address of the login request that opened this challenge.",
    )
    user_agent = fields.Char(
        string="User Agent",
        readonly=True,
        help="Browser user agent of the login request.",
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("pending", "Pending"),
            ("used", "Used"),
            ("expired", "Expired"),
            ("locked", "Locked"),
        ],
        default="pending",
        required=True,
        readonly=True,
        help=(
            "Pending = waiting for the code, "
            "Used = the correct code was entered, "
            "Expired = the code validity has passed, "
            "Locked = too many wrong codes were entered."
        ),
    )

    @api.model
    def _mail_otp_get_param(self, name):
        """Read one module setting, falling back to its default.

        :param name: setting name, a key of ``MAIL_OTP_DEFAULTS``
        :return: the stored value converted to the type of the default
        """
        default = MAIL_OTP_DEFAULTS[name]
        value = self.env["ir.config_parameter"].sudo().get_param(PARAM_PREFIX + name)
        if not value:
            return default
        if isinstance(default, bool):
            return value not in ("False", "false", "0")
        if isinstance(default, int):
            try:
                value = int(value)
            except (TypeError, ValueError):
                return default
            return value if value >= 1 else default
        if name == "mail_otp_policy" and value not in MAIL_OTP_POLICIES:
            return default
        return value

    @api.model
    def _mail_otp_hash(self, challenge_id, code):
        """Compute the keyed hash stored instead of the plain code.

        :param challenge_id: id of the challenge the code belongs to
        :param code: the plain 6-digit code
        :return: hexadecimal HMAC-SHA256 digest
        """
        secret = self.env["ir.config_parameter"].sudo().get_param("database.secret")
        message = "%s:%s" % (challenge_id, code)
        return hmac.new(
            (secret or "").encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    @api.model
    def _mail_otp_request_info(self):
        """Return the client IP and user agent of the current request.

        :return: dict with ``ip_address`` and ``user_agent``; the values
            are ``False`` outside of an HTTP request
        """
        if not request or not getattr(request, "httprequest", None):
            return {"ip_address": False, "user_agent": False}
        httprequest = request.httprequest
        user_agent = httprequest.user_agent.string if httprequest.user_agent else ""
        return {
            "ip_address": httprequest.remote_addr,
            "user_agent": (user_agent or "")[:250] or False,
        }

    @api.model
    def _mail_otp_hourly_limit_reached(self, user):
        """Tell whether the user already got the maximum mails this hour.

        :param user: ``res.users`` record
        :return: ``True`` when the ``sent`` log count in the last 60
            minutes reached ``mail_otp_max_mail_per_hour``
        """
        limit = self._mail_otp_get_param("mail_otp_max_mail_per_hour")
        since = fields.Datetime.now() - timedelta(minutes=60)
        count = (
            self.env["mail_otp_log"]
            .sudo()
            .search_count(
                [
                    ("user_id", "=", user.id),
                    ("event", "=", "sent"),
                    ("create_date", ">=", since),
                ]
            )
        )
        return count >= limit

    def _is_usable(self):
        """Tell whether the challenge can still accept a code.

        :return: ``True`` when pending and not yet expired
        """
        self.ensure_one()
        return bool(
            self.state == "pending"
            and self.expiration_date
            and self.expiration_date > fields.Datetime.now()
        )

    def _resend_error(self):
        """Return why a new code cannot be sent now, if it cannot.

        Checks the minimum delay since ``last_sent_date`` and the maximum
        mails per hour of the user.

        :return: an error message, or ``False`` when sending is allowed
        """
        self.ensure_one()
        now = fields.Datetime.now()
        delay = self._mail_otp_get_param("mail_otp_resend_delay")
        if self.last_sent_date:
            wait = self.last_sent_date + timedelta(seconds=delay) - now
            if wait.total_seconds() > 0:
                return _("Please wait %s seconds before requesting a new code.") % (
                    int(wait.total_seconds()) + 1
                )
        if self._mail_otp_hourly_limit_reached(self.user_id):
            return _("Too many codes were sent. Please try again later.")
        return False

    def _issue_code(self):
        """Generate a new code for this challenge and email it.

        Replaces the stored hash and the expiration date, sets the state
        back to ``pending`` and writes a ``sent`` log entry. The number of
        wrong attempts is NOT reset.

        :raises UserError: when the user has no email address
        """
        self.ensure_one()
        user = self.user_id.sudo()
        if not user.email:
            raise UserError(
                _(
                    "The user %s has no email address. "
                    "Please contact the administrator."
                )
                % user.name
            )
        code = user._mail_otp_generate_code()
        validity = self._mail_otp_get_param("mail_otp_code_validity")
        now = fields.Datetime.now()
        self.write(
            {
                "code_hash": self._mail_otp_hash(self.id, code),
                "expiration_date": now + timedelta(minutes=validity),
                "last_sent_date": now,
                "state": "pending",
            }
        )
        self._mail_otp_send_mail(user, code, validity)
        self.env["mail_otp_log"].sudo()._add_log(user, self, "sent")

    def _mail_otp_send_mail(self, user, code, validity):
        """Send the code by email and wipe it from any leftover mail.

        The mail is sent immediately and deleted on success. If the
        ``mail.mail`` still exists afterwards (failure or queued), its
        body is replaced by a text that does not contain the code.

        :param user: ``res.users`` recipient
        :param code: the plain 6-digit code
        :param validity: validity of the code in minutes
        """
        template = self.env.ref("base_auth_mail_otp.mail_template_mail_otp_code")
        mail_id = (
            template.sudo()
            .with_context(mail_otp_code=code, mail_otp_validity=validity)
            .send_mail(
                user.id,
                force_send=True,
                email_values={"model": False, "res_id": False},
            )
        )
        mail = self.env["mail.mail"].sudo().browse(mail_id).exists()
        if mail:
            masked = _("<p>The verification code is no longer available.</p>")
            mail.write({"body_html": masked, "body": masked})

    def _check_code(self, code):
        """Validate a code entered by the user against this challenge.

        State transitions: ``pending`` to ``used`` on the right code,
        ``pending`` to ``locked`` on the last allowed wrong code and
        ``pending`` to ``expired`` when the validity has passed. Every
        outcome is written to the audit log.

        :param code: the code typed by the user
        :return: one of ``ok``, ``wrong``, ``locked``, ``expired``,
            ``used``
        """
        self.ensure_one()
        log = self.env["mail_otp_log"].sudo()
        user = self.user_id
        if self.state == "used":
            return "used"
        if self.state == "locked":
            return "locked"
        if not self._is_usable():
            self.write({"state": "expired"})
            log._add_log(user, self, "failure", note="expired")
            return "expired"
        expected = self.code_hash or ""
        given = self._mail_otp_hash(self.id, code or "")
        if hmac.compare_digest(expected, given):
            self.write({"state": "used"})
            log._add_log(user, self, "success")
            return "ok"
        attempts = self.attempt_count + 1
        values = {"attempt_count": attempts}
        log._add_log(user, self, "failure", note="wrong code")
        result = "wrong"
        if attempts >= self._mail_otp_get_param("mail_otp_max_attempt"):
            values["state"] = "locked"
            result = "locked"
        self.write(values)
        if result == "locked":
            log._add_log(user, self, "locked")
        return result
