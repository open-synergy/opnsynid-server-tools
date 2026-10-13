.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========
Frequency
=========


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/opnsynid-server-tools
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *Frequency*
6.  Install the module

Usage
=====

``frequency._get_rrule(dtstart, until=None, tz=None)`` returns a one-shot
generator of naive UTC ``datetime`` values.

* ``dtstart`` is required. An empty value raises ``UserError`` when the
  method is called, not when the generator is iterated.
* ``dtstart`` and ``until`` accept a naive UTC ``datetime`` or a ``date``.
  A ``date`` for ``dtstart`` means 00:00:00; a ``date`` for ``until`` means
  23:59:59.999999, so the last day is included.
* Without ``until`` the series never ends. Stop iterating yourself.
* ``tz`` (then the context ``tz``, the user ``tz``, then UTC) is the
  timezone used to compute the series. Local time is kept across daylight
  saving changes and results are converted back to UTC.
* Months use the flags ``jan`` ... ``des`` (``des`` is December).
* ``interval`` must be at least 1, ``month_day`` between 1 and 31 and
  ``set_pos`` between -366 and 366; invalid data raises ``ValidationError``.


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

* Usamah <usa8bit@gmail.com>

Other credits
~~~~~~~~~~~~~

The functionality of this module is part of module:

* fieldservice_recurring (https://github.com/OCA/field-service)

Maintainer
----------

.. image:: https://simetri-sinergi.id/logo.png
   :alt: PT. Simetri Sinergi Indonesia
   :target: https://simetri-sinergi.id

This module is maintained by the PT. Simetri Sinergi Indonesia.
