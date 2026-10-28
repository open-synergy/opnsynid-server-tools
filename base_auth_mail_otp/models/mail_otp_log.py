# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MailOtpLog(models.Model):
    """
    Represents an audit entry of the email OTP login step.
    One entry is written whenever a code is sent, accepted, rejected or
    when a challenge gets locked.
    """

    _name = "mail_otp_log"
    _description = "Email OTP Log"
    _order = "id desc"

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        ondelete="cascade",
        index=True,
        help="User the event belongs to.",
    )
    challenge_id = fields.Many2one(
        comodel_name="mail_otp_challenge",
        string="Challenge",
        ondelete="set null",
        help="Challenge the event belongs to.",
    )
    event = fields.Selection(
        string="Event",
        selection=[
            ("sent", "Code Sent"),
            ("success", "Success"),
            ("failure", "Failure"),
            ("locked", "Locked"),
        ],
        required=True,
        help=(
            "Code Sent = a code was emailed, "
            "Success = the correct code was entered, "
            "Failure = a wrong or expired code was entered, "
            "Locked = the challenge was locked."
        ),
    )
    ip_address = fields.Char(
        string="IP Address",
        help="IP address of the request that caused the event.",
    )
    user_agent = fields.Char(
        string="User Agent",
        help="Browser user agent of the request that caused the event.",
    )
    note = fields.Char(
        string="Note",
        help="Short free text with extra information about the event.",
    )

    @api.model
    def _add_log(self, user, challenge, event, note=False):
        """Write one audit entry.

        :param user: ``res.users`` the event belongs to
        :param challenge: ``mail_otp_challenge`` record, may be empty
        :param event: one of ``sent``, ``success``, ``failure``, ``locked``
        :param note: optional short text
        :return: the created ``mail_otp_log`` record
        """
        values = self.env["mail_otp_challenge"]._mail_otp_request_info()
        values.update(
            {
                "user_id": user.id,
                "challenge_id": challenge.id if challenge else False,
                "event": event,
                "note": note,
            }
        )
        return self.sudo().create(values)
