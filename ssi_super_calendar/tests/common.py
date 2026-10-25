# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime


def create_calendar_row(
    env, res_model, res_id, start, end, partner_ids=(), name="Busy", **extra
):
    """Insert one ``super_calendar`` row without going through a mixin.

    The row is created as superuser and the raw ``partner_ids_array``
    column is filled with parameterized SQL.

    :param env: environment used to create the row
    :param res_model: technical name of the source model
    :param res_id: database ID of the source record
    :param start: ``datetime`` where the busy period starts (UTC)
    :param end: ``datetime`` where the busy period ends (UTC)
    :param partner_ids: iterable of ``res.partner`` IDs
    :param name: raw label of the period
    :param extra: other field values, e.g. ``applies_to_all``
    :return: the new ``super_calendar`` record
    """
    partners = sorted(set(partner_ids))
    vals = {
        "name": name,
        "res_model": res_model,
        "res_id": res_id,
        "date_start": start,
        "date_end": end,
        "partner_count": len(partners),
    }
    vals.update(extra)
    row = env["super_calendar"].sudo().create(vals)
    env.cr.execute(
        "UPDATE super_calendar SET partner_ids_array = %s::int4[] WHERE id = %s",
        (partners, row.id),
    )
    return row


def hour(value):
    """Return a naive ``datetime`` on a fixed day at the given hour.

    :param value: hour of the day, from 0 to 23
    :return: the ``datetime`` on 2026-03-02 at ``value`` o'clock
    """
    return datetime(2026, 3, 2, value, 0, 0)
