.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Super Calendar
==============

A generic availability calendar keyed on ``res.partner``. It records when a
partner is busy (leave, assignment, public holiday, school agenda, ...) so
that one question can be asked in one place: *is partner X free in this
period?*

Rows of the calendar are never entered by hand. They are written by the
source documents, through the abstract model ``mixin.super_calendar_source``,
so the calendar cannot drift out of sync with them. Participants are stored in
a PostgreSQL ``int4[]`` column (``partner_ids_array``) with a GIN index; no
many2many relation table is used.

Work Instruction
================

* `View Availability on Super Calendar <docs/super_calendar/index.html>`_


Installation
============

To install this module, you need to:

1.  Clone the branch 14.0 of the repository https://github.com/open-synergy/opnsynid-server-tools
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list (Must be on developer mode)
4.  Go to menu *Apps -> Apps -> Main Apps*
5.  Search For *Super Calendar*
6.  Install the module


Usage
=====

Make a model a source
---------------------

Inherit ``mixin.super_calendar_source`` and implement the hook:

.. code-block:: python

    class LeaveRequest(models.Model):
        _name = "leave.request"
        _inherit = ["mixin.super_calendar_source"]
        _super_calendar_trigger_fields = ["date_from", "date_to", "partner_id"]

        def _get_super_calendar_values(self):
            self.ensure_one()
            start, end = self._super_calendar_date_range(self.date_from)
            return [
                {
                    "name": self.display_name,
                    "date_start": start,
                    "date_end": end,
                    "allday": True,
                    "applies_to_all": False,
                    "partner_ids": [self.partner_id.id],
                }
            ]

Rows are rebuilt when a source record is created, when one of
``_super_calendar_trigger_fields`` is written, and by
``action_refresh_super_calendar()``. They are deleted with the source record.
The mixin does not resynchronize when the membership of a group of partners
changes; call ``action_refresh_super_calendar()`` in that case.

Ask who is busy
---------------

.. code-block:: python

    conflicts = env["super_calendar"].check_availability(
        date_start, date_end, partner_ids, exclude_refs=[("leave.request", 7)]
    )

It returns one dict per requested partner and conflicting row, with the keys
``partner_id``, ``calendar_id``, ``label``, ``res_model``, ``res_id``,
``date_start`` and ``date_end``. Periods that only touch (end equal to start)
do not conflict.

The search always runs as superuser, so the number of conflicts never depends
on the caller. The right to read the source document only decides the label:
without it, ``label`` is ``Not available`` and ``res_model`` / ``res_id`` are
``False``.


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
