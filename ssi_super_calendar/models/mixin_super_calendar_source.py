# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, time, timedelta

import pytz

from odoo import api, fields, models


class MixinSuperCalendarSource(models.AbstractModel):
    """Keep ``super_calendar`` rows in sync with a source model.

    A model that inherits this mixin describes its busy periods in
    ``_get_super_calendar_values``. The mixin deletes and re-creates the
    matching ``super_calendar`` rows whenever a source record is created,
    when one of ``_super_calendar_trigger_fields`` is written, and on
    demand with ``action_refresh_super_calendar``. Rows are removed when
    the source record is deleted. All writes to ``super_calendar`` use
    ``sudo()`` because internal users have read-only access to it.
    """

    _name = "mixin.super_calendar_source"
    _description = "Super Calendar Source Mixin"

    # Names of the fields whose change triggers a re-synchronization.
    _super_calendar_trigger_fields = []

    def _get_super_calendar_values(self):
        """Return the busy periods of this source record.

        Extension point: override it in the source model. It is
        called on one record at a time.

        :return: list of dicts with the keys ``name``, ``date_start``,
            ``date_end``, ``allday``, ``applies_to_all`` and
            ``partner_ids`` (list of ``res.partner`` IDs); an empty list
            means the record is never busy
        """
        self.ensure_one()
        return []

    @api.model
    def _super_calendar_date_range(self, date):
        """Return the UTC bounds of one whole day in the user timezone.

        The end bound is 00:00 of the following day. The timezone of the
        current user is used, falling back to UTC when it is empty or
        unknown.

        :param date: a ``date`` or a date string
        :return: tuple ``(start, end)`` of naive UTC ``datetime`` values
        """
        date = fields.Date.to_date(date)
        try:
            tz = pytz.timezone(self.env.user.tz or "UTC")
        except pytz.UnknownTimeZoneError:
            tz = pytz.utc
        start = tz.localize(datetime.combine(date, time.min))
        end = tz.localize(datetime.combine(date + timedelta(days=1), time.min))
        return (
            start.astimezone(pytz.utc).replace(tzinfo=None),
            end.astimezone(pytz.utc).replace(tzinfo=None),
        )

    def _super_calendar_delete_rows(self):
        """Delete every ``super_calendar`` row owned by these records."""
        if not self.ids:
            return
        calendar = self.env["super_calendar"].sudo().with_context(active_test=False)
        calendar.search(
            [("res_model", "=", self._name), ("res_id", "in", self.ids)]
        ).unlink()

    def _super_calendar_sync(self):
        """Rebuild the ``super_calendar`` rows of these records.

        Existing rows of the records are deleted and the rows described
        by ``_get_super_calendar_values`` are inserted again, in the
        same transaction. The values are computed with ``sudo()`` so the
        stored rows never depend on the user who triggered the sync. The
        participant array is written with a parameterized SQL statement.
        """
        self._super_calendar_delete_rows()
        calendar = self.env["super_calendar"].sudo()
        for record in self.sudo():
            for vals in record._get_super_calendar_values():
                partners = sorted({int(pid) for pid in vals.get("partner_ids") or []})
                row = calendar.create(
                    {
                        "name": vals["name"],
                        "res_model": record._name,
                        "res_id": record.id,
                        "date_start": vals["date_start"],
                        "date_end": vals["date_end"],
                        "allday": vals.get("allday", False),
                        "applies_to_all": vals.get("applies_to_all", False),
                        "partner_count": len(partners),
                    }
                )
                self.env.cr.execute(
                    "UPDATE super_calendar SET partner_ids_array = %s::int4[] "
                    "WHERE id = %s",
                    (partners, row.id),
                )

    def action_refresh_super_calendar(self):
        """Rebuild the ``super_calendar`` rows of these records.

        Use it after a change the mixin cannot see, for example when the
        membership of a group of partners changed.

        :return: ``True``
        """
        self._super_calendar_sync()
        return True

    @api.model_create_multi
    def create(self, vals_list):
        """Create the source records and their ``super_calendar`` rows.

        Overridden so that a new source record is immediately visible in
        the calendar.
        """
        records = super().create(vals_list)
        records._super_calendar_sync()
        return records

    def write(self, vals):
        """Write the source records and re-sync when a trigger changes.

        Overridden to rebuild the rows only when ``vals`` touches one of
        ``_super_calendar_trigger_fields``; other writes leave them as is.
        """
        result = super().write(vals)
        if set(vals) & set(self._super_calendar_trigger_fields):
            self._super_calendar_sync()
        return result

    def unlink(self):
        """Delete the source records together with their calendar rows.

        Overridden so that no row survives its source document.
        """
        self._super_calendar_delete_rows()
        return super().unlink()
