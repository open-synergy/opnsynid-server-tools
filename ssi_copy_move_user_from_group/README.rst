.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Copy/Move User From Group
==========================

This module provides a wizard to copy or move all members of one group
(``res.groups``) to another group, without changing any other group already
assigned to the affected users.


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/opnsynid-server-tools
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list (Must be on developer mode)
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *Copy/Move User From Group*
6.  Install the module


Usage
=====

To use this module, you need to:

- Enable developer mode.
- Go to menu Settings > Technical > Users & Companies > Groups.
- Open the group whose members you want to copy or move (source group).
- Click the "Action" button on the top, then click "Copy/Move User From Group".
- The wizard opens with the source group already filled in from the group you
  opened. Select the destination group.
- Click **Copy Users** to add every member of the source group to the
  destination group, keeping them in the source group as well.
- Click **Move Users** to add every member of the source group to the
  destination group and remove them from the source group.
- In both cases, any other group already assigned to the affected users is
  left untouched.

Notes
-----

- If the destination group has ``Inherited/Implied groups`` configured
  (``implied_ids``), Odoo automatically grants those implied groups to the
  affected users as well. This is native Odoo behaviour, not a side effect
  introduced by this module.
- Copying or moving users between groups that belong to conflicting user-type
  categories (Internal / Portal / Public) is blocked by Odoo's own
  consistency check and raises a validation error.


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

* Andhitia Rama <andhitia.r@gmail.com>

Maintainer
----------

.. image:: https://simetri-sinergi.id/logo.png
   :alt: PT. Simetri Sinergi Indonesia
   :target: https://simetri-sinergi.id

This module is maintained by the PT. Simetri Sinergi Indonesia.
