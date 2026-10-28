# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author

{
    "name": "Base Auth Mail OTP Admin Passkey",
    "version": "14.0.1.0.1",
    "summary": "Skip the email OTP when the administrator passkey is used",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "category": "Generic Modules/Base",
    "website": "https://simetri-sinergi.id",
    "depends": [
        "base_auth_mail_otp",
        "auth_admin_passkey",
    ],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": True,
    "license": "AGPL-3",
}
