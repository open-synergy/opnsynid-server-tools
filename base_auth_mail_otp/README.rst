.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
Base Auth Mail OTP
==================

Adds a second login step: after the password, users covered by the configured
policy must type a 6-digit code sent to their email address.

* The code lifetime, the number of wrong attempts, the resend delay and the
  emails per hour are configurable in the Settings.
* Only a keyed hash of the code is stored, never the code itself.
* Trusted devices let a browser skip the code for a configurable number of days.
* Admins can exempt a user, permanently or until a given date.
* Every sent code, success, failure and lock is written to an audit log.
* The module does not depend on ``auth_totp``. When a user has the Authenticator
  enabled, the Authenticator is asked instead of the email code.
* Password access over XML-RPC is refused for users covered by the policy; API keys
  keep working.


Work Instruction
================

* `Configure Email OTP Policy <docs/res_users/index.html>`_
* `Exempt a User from Email OTP <docs/res_users/index.html>`_
* `Log In with an Email Code <docs/res_users/index.html>`_


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/opnsynid-server-tools
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list (Must be on developer mode)
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *Base Auth Mail OTP*
6.  Install the module

Installing the module does not enable anything: the policy is *Disabled* until an
administrator changes it in *Settings -> General Settings -> Email OTP*.


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
