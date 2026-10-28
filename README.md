[![Build Status](https://travis-ci.com/open-synergy/opnsynid-server-tools.svg?branch=14.0)](https://travis-ci.com/open-synergy/opnsynid-server-tools)
![pre-commit](https://github.com/open-synergy/opnsynid-server-tools/actions/workflows/pre-commit.yml/badge.svg)
[![codecov](https://codecov.io/gh/open-synergy/opnsynid-server-tools/branch/14.0/graph/badge.svg)](https://codecov.io/gh/open-synergy/opnsynid-server-tools)

<!-- /!\ do not modify above this line -->

# opnsynid-server-tools

opnsynid-server-tools

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[base_auth_mail_otp](base_auth_mail_otp/) | 14.0.1.0.2 |  | Email one-time password (OTP) as a second login step
[base_auth_mail_otp_admin_passkey](base_auth_mail_otp_admin_passkey/) | 14.0.1.0.1 |  | Skip the email OTP when the administrator passkey is used
[base_auth_mail_otp_password_security](base_auth_mail_otp_password_security/) | 14.0.1.0.1 |  | Check password expiration only after the email OTP step
[base_copy_user_access](base_copy_user_access/) | 14.0.1.1.1 |  | Copy access right from another user
[base_copy_user_operating_unit](base_copy_user_operating_unit/) | 14.0.1.0.0 |  | Copy Allowed Operating Unit and Default Operating Unit from another user
[base_custom_system_parameter](base_custom_system_parameter/) | 14.0.1.1.0 |  | Base Custom System Parameter
[base_duration](base_duration/) | 14.0.1.3.0 |  | Base Duration
[base_public_holiday](base_public_holiday/) | 14.0.1.3.0 |  | Base Public Holiday
[base_user_copy_user_role](base_user_copy_user_role/) | 14.0.1.2.0 |  | Base Copy User Role
[base_user_role_menu](base_user_role_menu/) | 14.0.1.1.0 |  | Manage Menu Access Based on Roles
[ssi_base_import_xml](ssi_base_import_xml/) | 14.0.1.2.0 |  | Import data records using XML files
[ssi_copy_move_user_from_group](ssi_copy_move_user_from_group/) | 14.0.1.0.0 |  | Copy or move all members of one group to another group
[ssi_frequency](ssi_frequency/) | 14.0.1.3.1 |  | Frequency
[ssi_super_calendar](ssi_super_calendar/) | 14.0.1.0.2 |  | Super Calendar
[ssi_user_group_m2m](ssi_user_group_m2m/) | 14.0.1.0.0 |  | User Group Many2many
[ssi_user_group_section](ssi_user_group_section/) | 14.0.1.0.0 |  | User Group Section
[test_base_auth_mail_otp](test_base_auth_mail_otp/) | 14.0.1.0.1 |  | Test coexistence of email OTP with the Authenticator app
[test_base_duration](test_base_duration/) | 14.0.1.1.0 |  | Test Module - Base Duration

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to OCA
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
