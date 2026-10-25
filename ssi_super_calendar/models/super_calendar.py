# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import AccessError


class SuperCalendar(models.Model):
    """Generic availability calendar keyed on ``res.partner``.

    Every row is one busy period of one source document (leave,
    assignment, holiday, school agenda, ...). Rows are written only by
    models that inherit ``mixin.super_calendar_source`` so the calendar
    cannot drift out of sync with its sources. The participants live in
    a raw PostgreSQL ``int4[]`` column, not in a many2many table.
    """

    _name = "super_calendar"
    _description = "Super Calendar"
    _order = "date_start, id"

    name = fields.Char(
        string="Name",
        required=True,
        groups="base.group_system",
        help="Raw label of the busy period. Only administrators can read "
        "it directly; other users see the label through the display name, "
        "which hides it when they cannot read the source document.",
    )
    res_model = fields.Char(
        string="Source Model",
        required=True,
        index=True,
        help="Technical name of the model that owns the source document.",
    )
    res_id = fields.Many2oneReference(
        string="Source ID",
        model_field="res_model",
        required=True,
        index=True,
        help="Database ID of the source document in the source model.",
    )
    date_start = fields.Datetime(
        string="Start Date",
        required=True,
        help="Start of the busy period, stored in UTC.",
    )
    date_end = fields.Datetime(
        string="End Date",
        required=True,
        help="End of the busy period, stored in UTC. The period does not "
        "include this instant.",
    )
    allday = fields.Boolean(
        string="All Day",
        help="Check this box when the busy period covers whole days.",
    )
    applies_to_all = fields.Boolean(
        string="Applies to Everyone",
        default=False,
        help="Check this box when the busy period concerns every partner, "
        "for example a public holiday.",
    )
    partner_count = fields.Integer(
        string="Number of Partners",
        help="Number of distinct partners attached to this period. It is "
        "written when the row is synchronized from its source.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck this box to ignore the period without deleting it.",
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Partners",
        compute="_compute_partner_ids",
        search="_search_partner_ids",
        store=False,
        help="Partners who are busy during the period. They are read from "
        "the ``partner_ids_array`` database column; no relation table "
        "exists.",
    )

    def init(self):
        """Create the raw participant column and the supporting indexes.

        The ``partner_ids_array`` column is not an ORM field. It is added
        here so that it exists after both installation and update, and it
        is indexed with GIN for the ``&&`` overlap operator. A btree index
        on ``(date_start, date_end)`` serves the period overlap test.
        """
        cr = self.env.cr
        cr.execute(
            "ALTER TABLE super_calendar "
            "ADD COLUMN IF NOT EXISTS partner_ids_array int4[] "
            "NOT NULL DEFAULT '{}'"
        )
        cr.execute(
            "CREATE INDEX IF NOT EXISTS "
            "super_calendar_partner_ids_array_gin_idx "
            "ON super_calendar USING gin (partner_ids_array)"
        )
        cr.execute(
            "CREATE INDEX IF NOT EXISTS super_calendar_date_range_idx "
            "ON super_calendar (date_start, date_end)"
        )

    @api.depends("partner_count")
    def _compute_partner_ids(self):
        """Fill ``partner_ids`` from the raw ``partner_ids_array`` column.

        The column is read with one parameterized SQL query for the
        whole recordset.
        """
        ids = [rec.id for rec in self if isinstance(rec.id, int)]
        mapping = {}
        if ids:
            self.env.cr.execute(
                "SELECT id, COALESCE(partner_ids_array, '{}') FROM super_calendar "
                "WHERE id = ANY(%s)",
                (ids,),
            )
            mapping = dict(self.env.cr.fetchall())
        partner_obj = self.env["res.partner"]
        for rec in self:
            rec.partner_ids = partner_obj.browse(mapping.get(rec.id) or [])

    @api.model
    def _search_partner_ids(self, operator, value):
        """Translate a search on ``partner_ids`` into an array overlap.

        Rows that apply to everyone match any positive search. A text
        value is resolved to partners by name first.

        :param operator: domain operator, positive or negative
        :param value: partner ID, list of IDs, text, or falsy
        :return: a domain restricting ``id`` with an ``inselect`` clause
        """
        negative = operator in ("!=", "not in", "not ilike", "not like")
        if isinstance(value, str):
            positive_op = operator[4:] if operator.startswith("not ") else operator
            partners = self.env["res.partner"].search(
                [("display_name", positive_op, value)]
            )
            ids = partners.ids
        elif isinstance(value, int) and not isinstance(value, bool):
            ids = [value]
        else:
            ids = [int(v) for v in (value or []) if v]
        if not ids and not isinstance(value, str):
            clause = (
                "SELECT id FROM super_calendar "
                "WHERE COALESCE(partner_ids_array, '{}') = '{}'"
            )
            return [
                ("id", "not inselect" if not negative else "inselect", (clause, []))
            ]
        clause = (
            "SELECT id FROM super_calendar "
            "WHERE applies_to_all OR partner_ids_array && %s::int4[]"
        )
        return [("id", "not inselect" if negative else "inselect", (clause, [ids]))]

    def _can_read_source(self):
        """Tell whether the current user may read the source document.

        Both the model access rights and the record rules of the source
        document are checked as the calling user, never as superuser.

        :return: ``True`` when the source document is readable
        """
        self.ensure_one()
        return self._can_read_ref(self.sudo().res_model, self.sudo().res_id)

    @api.model
    def _can_read_ref(self, res_model, res_id):
        """Check read access of the current user on one source record.

        :param res_model: technical name of the source model
        :param res_id: database ID of the source document
        :return: ``True`` when the user can read that record
        """
        if res_model not in self.env:
            return False
        source_model = self.env[res_model]
        if not source_model.check_access_rights("read", raise_exception=False):
            return False
        record = source_model.browse(res_id).exists()
        if not record:
            return False
        try:
            record.check_access_rule("read")
        except AccessError:
            return False
        return True

    @api.depends("name")
    @api.depends_context("uid")
    def _compute_display_name(self):
        """Compute ``display_name`` per user through ``name_get``."""
        names = dict(self.name_get())
        for rec in self:
            rec.display_name = names.get(rec.id, False)

    def name_get(self):
        """Return the label, hiding it from users without source access.

        The raw ``name`` is restricted to administrators, so it is read
        with ``sudo()`` and shown only when the calling user can read the
        source document; otherwise ``Not available`` is returned.
        """
        result = []
        for rec in self:
            if rec._can_read_source():
                label = rec.sudo().name
            else:
                label = _("Not available")
            result.append((rec.id, label))
        return result

    @api.model
    def check_availability(self, date_start, date_end, partner_ids, exclude_refs=None):
        """Return the busy periods that overlap a period for partners.

        The search always runs as superuser: the number of entries never
        depends on the access rights of the caller. Those rights only
        decide the label; when the caller cannot read the source
        document the label is ``Not available`` and ``res_model`` and
        ``res_id`` are ``False``. Two periods that only touch (end equal
        to start) do not conflict.

        :param date_start: start of the period to check (UTC)
        :param date_end: end of the period to check (UTC)
        :param partner_ids: list of ``res.partner`` IDs to check
        :param exclude_refs: optional list of ``(res_model, res_id)``
            tuples whose rows are ignored, typically the source document
            that is being planned
        :return: list of dicts with ``partner_id``, ``calendar_id``,
            ``label``, ``res_model``, ``res_id``, ``date_start`` and
            ``date_end``; one entry per requested partner and conflicting
            row
        """
        partners = sorted({int(pid) for pid in (partner_ids or []) if pid})
        if not partners:
            return []
        date_start = fields.Datetime.to_datetime(date_start)
        date_end = fields.Datetime.to_datetime(date_end)
        # Raw SQL below: push pending ORM writes (e.g. ``active``) first.
        self.env["super_calendar"].flush()
        query = (
            "SELECT id, res_model, res_id, date_start, date_end, "
            "applies_to_all, COALESCE(partner_ids_array, '{}') "
            "AS partner_ids_array "
            "FROM super_calendar "
            "WHERE active AND date_start < %s AND date_end > %s "
            "AND (applies_to_all OR partner_ids_array && %s::int4[])"
        )
        params = [date_end, date_start, partners]
        refs = [(model, int(rid)) for model, rid in (exclude_refs or [])]
        if refs:
            query += " AND (res_model, res_id) NOT IN %s"
            params.append(tuple(refs))
        query += " ORDER BY date_start, id"
        self.env.cr.execute(query, params)
        rows = self.env.cr.dictfetchall()
        names = self._get_check_labels(rows)
        result = []
        for row in rows:
            if row["applies_to_all"]:
                hit = partners
            else:
                hit = [pid for pid in partners if pid in row["partner_ids_array"]]
            label, res_model, res_id = names[row["id"]]
            for pid in hit:
                result.append(
                    {
                        "partner_id": pid,
                        "calendar_id": row["id"],
                        "label": label,
                        "res_model": res_model,
                        "res_id": res_id,
                        "date_start": row["date_start"],
                        "date_end": row["date_end"],
                    }
                )
        return result

    @api.model
    def _get_check_labels(self, rows):
        """Resolve label and source reference of conflicting rows.

        :param rows: list of dicts from the availability query
        :return: dict mapping the row ID to ``(label, res_model, res_id)``
        """
        labels = {}
        calendars = self.sudo().browse([row["id"] for row in rows])
        by_id = {rec.id: rec for rec in calendars}
        for row in rows:
            if self._can_read_ref(row["res_model"], row["res_id"]):
                labels[row["id"]] = (
                    by_id[row["id"]].name,
                    row["res_model"],
                    row["res_id"],
                )
            else:
                labels[row["id"]] = (_("Not available"), False, False)
        return labels
