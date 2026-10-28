.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================
Base Auth Mail OTP Admin Passkey
================================

Glue between ``base_auth_mail_otp`` and ``auth_admin_passkey``.

When the system administrator logs in to another account with the passkey
from the server configuration file, the email code step is skipped, because
the code would go to the mailbox of the user, not to the administrator.

* The login with the passkey marks the web session, and the marked session
  needs no email code.
* A login with the real password of the same user still asks for the code.
* A wrong password is still refused.
* The mark lives in the session only; logging out clears it.
* XML-RPC is not changed: for users covered by the email OTP the password is
  refused, and ``auth_admin_passkey`` still accepts the passkey there, as it
  did before the email OTP existed.


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/opnsynid-server-tools
2.  Clone the branch 14.0 of the repository https://github.com/OCA/server-auth
3.  Add the path to these repositories in your configuration (addons-path)
4.  Update the module list (Must be on developer mode)
5.  Go to menu *Apps -> Apps -> Main Apps*
6.  Search For *Base Auth Mail OTP Admin Passkey*
7.  Install the module

The module is installed automatically when ``base_auth_mail_otp`` and
``auth_admin_passkey`` are both installed.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/open-synergy/opnsynid-server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Andhitia Rama <andhitia.r@gmail.com>

Maintainer
----------

.. image:: https://simetri-sinergi.id/logo.png
   :alt: PT. Simetri Sinergi Indonesia
   :target: https://simetri-sinergi.id

This module is maintained by the PT. Simetri Sinergi Indonesia.
