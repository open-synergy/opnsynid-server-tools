# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author

{
    "name": "Base Auth Mail OTP",
    "version": "14.0.1.0.0",
    "summary": "Email one-time password (OTP) as a second login step",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "category": "Generic Modules/Base",
    "website": "https://simetri-sinergi.id",
    "depends": [
        "base",
        "web",
        "mail",
        "web_tour",
    ],
    "data": [
        "security/ir_model_access/mail_otp_challenge.xml",
        "security/ir_model_access/mail_otp_trusted_device.xml",
        "security/ir_model_access/mail_otp_log.xml",
        "data/mail_template_data.xml",
        "menu.xml",
        "views/assets.xml",
        "views/mail_otp_templates.xml",
        "views/mail_otp_challenge.xml",
        "views/mail_otp_trusted_device.xml",
        "views/mail_otp_log.xml",
        "views/res_users.xml",
        "views/res_config_settings.xml",
    ],
    "installable": True,
    "application": False,
    "license": "AGPL-3",
}
