.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=================================
Manage Menu Access Based on Roles
=================================

This module change the way administrator manage menu access.

Key Features:

1. Wizards to reset groups field on ir.ui.menu
2. Change widget groups_id on ir.ui.menu into many2many_checkboxes
3. Field groups_id on ir.ui.menu only show groups with application == User Roles
4. Override write on ir.ui.menu so that only accept groups with application == User Roles. \
   This will prevent additional module to add groups into ir.ui.menu

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/open-synergy/opnsynid-server-tools
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *Manage Menu Access Based on Roles*
6.  Install the module

Usage
=====

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

* Michael Viriyananda <viriyananda.michael@gmail.com>

Maintainer
----------

.. image:: https://opensynergy-indonesia.com/logo.png
   :alt: OpenSynergy Indonesia
   :target: https://opensynergy-indonesia.com

This module is maintained by the OpenSynergy Indonesia.
