.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
  :target: https://www.gnu.org/licenses/agpl
  :alt: License: AGPL-3

======================================
Base Auth Mail OTP - Password Security
======================================

This module lets ``base_auth_mail_otp`` and ``password_security`` work
together. The password expiration check runs only after the login is
complete, which for users with an email OTP means after the code is
accepted. An expired password then leads to a valid password reset page,
instead of an "Invalid signup token" error.

The module is installed automatically when both modules are installed.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/open-synergy/opnsynid-server-tools/issues>`_. In case of
trouble, please check there if your issue has already been reported. If you
spotted it first, help us smash it by providing detailed and welcomed
feedback.

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
