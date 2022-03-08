.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
  :target: https://www.gnu.org/licenses/agpl
  :alt: License: AGPL-3

=====================
Base Copy User Access
=====================

This Module allows the administrator to copy user access from one user to many users.

This Module created a wizard that can be access on "Action" button in Settings > Users > Users & Companies.

Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/opnsynid-server-tools
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *Base Copy User Access*
6.  Install the module

Usage
=====

To use this module, you need to:
    - Go to menu Settings > Users > Users & Companies
    - Select Users on the list of tree view
    - Click "Action" button on the top
    - Click "Copy User Access"
    - Select the user on the selection
    - Click "Copy"

Use Case
========
"User-A" is a users who have access as manager sales and accounting.
Administrator asked to make another two users who has the right equal access with User-A.
The two new users was named "User-B" and "User-C"

So administrator have to do:

- Without module Base Copy User Access is installed:
    * Check user access of User-A
        + Go to menu Settings > Users > Users
        + Find the User-A and opened it
    * Create a new User and named it User-B
        + Go to menu Settings > Users > Users
        + Create the User-B
    * Set up the access of User-B that has the right equal access with User-A
        + Go to menu Settings > Users > Users
        + Find the User-B and opened it
        + Fill user access of User-B according with user access of User-A
    * Create a new User and named it User-C
        + Go to menu Settings > Users > Users
        + Create the User-C
    * Set up the access of User-C that has the right equal access with User-A
        + Go to menu Settings > Users > Users
        + Find the User-C and opened it
        + Fill user access of User-C according with user access of User-A

- With module Base Copy User Access is installed:
    * Create a new User and named it User-B
        + Go to menu Settings > Users > Users
        + Create the User-B
    * Create a new User and named it User-C
        + Go to menu Settings > Users > Users
        + Create the User-C
    * Copy user access of User-A to User-B and User-C
        + Go to menu Settings > Users > Users
        + Select User-A and User-B on the list of tree view
        + Click "More" button on the top
        + Click "Copy User Access"
        + The wizard will show up and then fill the user with User-A

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/open-synergy/opnsynid-server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed
and welcomed feedback.


Credits
=======

Contributors
------------

* Nur Azmi <azmimr67@gmail.com>
* Michael Viriyananda <viriyananda.michael@gmail.com>
* Andhitia Rama <andhitia.r@gmail.com>

Maintainer
----------

.. image:: https://simetri-sinergi.id/logo.png
   :alt: PT. Simetri Sinergi Indonesia
   :target: https://simetri-sinergi.id.com

This module is maintained by the PT. Simetri Sinergi Indonesia.
