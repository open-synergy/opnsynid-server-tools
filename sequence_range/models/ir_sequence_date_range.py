# Copyright 2021 OpenSynergy Indonesia
# Copyright 2021 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import models, api, fields
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class IrSequenceDateRange(models.Model):
    _name = "ir.sequence.date_range"
    _description = "Sequence Date Range"
    _rec_name = "sequence_id"

    @api.multi
    def _get_number_next_actual(self):
        '''Return number from ir_sequence row when no_gap implementation,
        and number from postgres sequence when standard implementation.'''
        for seq in self:
            if seq.sequence_id.implementation != "standard":
                seq.number_next_actual = seq.number_next
            else:
                seq_id = "%03d_%03d" % (seq.sequence_id.id, seq.id)
                query = """SELECT last_value,
                           (SELECT increment_by
                            FROM pg_sequences
                            WHERE sequencename = 'ir_sequence_%(seq_id)s'),
                                  is_called
                           FROM ir_sequence_%(seq_id)s"""
                if self.env.cr._cnx.server_version < 100000:
                    query = """SELECT last_value,
                                      increment_by,
                                      is_called
                              FROM ir_sequence_%(seq_id)s"""
                self.env.cr.execute(query % {'seq_id': seq_id})
                (last_value, increment_by, is_called) = self.env.cr.fetchone()
                if is_called:
                    seq.number_next_actual = last_value + increment_by
                else:
                    seq.number_next_actual = last_value

    @api.multi
    def _set_number_next_actual(self):
        for seq in self:
            seq.write({'number_next': seq.number_next_actual or 1})

    @api.model
    def default_get(self, fields):
        result = super(IrSequenceDateRange, self).default_get(fields)
        result["number_next_actual"] = 1
        return result

    date_from = fields.Date(
        string="From",
        required=True,
    )
    date_to = fields.Date(
        string="To",
        required=True,
    )
    sequence_id = fields.Many2one(
        string="Main Sequence",
        comodel_name="ir.sequence",
        required=True,
        ondelete="cascade",
    )
    number_next = fields.Integer(
        string="Next Number",
        required=True,
        default=1,
        help="Next number of this sequence",
    )
    number_next_actual = fields.Integer(
        string="Actual Next Number",
        compute="_get_number_next_actual",
        inverse="_set_number_next_actual",
        help="Next number that will be used. This number can be incremented "
             "frequently so the displayed value might already be obsolete",
    )

    @api.model
    def create(self, values):
        seq = super(IrSequenceDateRange, self).create(values)
        main_seq = seq.sequence_id
        if main_seq.implementation == "standard":
            seq_name = "ir_sequence_%03d_%03d" % (main_seq.id, seq.id)
            self._create_sequence(
                seq_name,
                main_seq.number_increment,
                values.get("number_next_actual", 1))
        return seq

    @api.multi
    def _create_sequence(self, seq_name, number_increment, number_next):
        cr = self.env.cr
        if number_increment == 0:
            raise UserError(_("Step must not be zero."))
        sql = "CREATE SEQUENCE %s INCREMENT BY %%s START WITH %%s" % seq_name
        cr.execute(sql, (number_increment, number_next))

    @api.multi
    def _select_nextval(self):
        self.ensure_one()
        cr = self.env.cr
        seq_name = "ir_sequence_%03d_%03d" % (self.sequence_id.id, self.id)
        cr.execute("SELECT nextval('%s')" % seq_name)
        return cr.fetchone()

    @api.multi
    def _update_nogap(self):
        self.ensure_one()
        cr = self.env.cr
        number_next = self.number_next
        number_increment = self.sequence_id.number_increment
        query_select = """SELECT number_next
                          FROM %s WHERE id=%s
                          FOR UPDATE NOWAIT""" % (self._table, self.id)
        cr.execute(query_select)
        query_update = """UPDATE %s
                       SET number_next=number_next+%s
                       WHERE id=%s""" % (self._table, number_increment, self.id)
        cr.execute(query_update)
        self.invalidate_cache(["number_next"], [self.id])
        return number_next

    @api.multi
    def _next(self):
        self.ensure_one()
        if self.sequence_id.implementation == "standard":
            number_next = self._select_nextval()
        else:
            number_next = self._update_nogap()
        return self.sequence_id.get_next_char(number_next)

    @api.multi
    def _alter_sequence(self, number_increment=None, number_next=None):
        self.ensure_one()
        cr = self.env.cr
        seq_name = "ir_sequence_%03d_%03d" % (self.sequence_id.id, self.id)
        if number_increment == 0:
            raise UserError(_("Step must not be zero."))
        query_select = """SELECT relname
                          FROM pg_class
                          WHERE relkind='S' AND
                          relname='%s'""" % (str(seq_name))
        cr.execute(query_select)
        if not cr.fetchone():
            return
        statement = "ALTER SEQUENCE %s" % (seq_name, )
        if number_increment is not None:
            statement += " INCREMENT BY %d" % (number_increment, )
        if number_next is not None:
            statement += " RESTART WITH %d" % (number_next, )
        cr.execute(statement)

    @api.multi
    def alter_sequence(self, number_increment=None, number_next=None):
        for seq in self:
            self._alter_sequence(
                number_increment=number_increment,
                number_next=number_next)

    @api.multi
    def _drop_sequences(self):
        cr = self.env.cr
        seq_names = [
            "ir_sequence_%03d_%03d" % (x.sequence_id.id, x.id) for x in self]
        names = ','.join(seq_names)
        cr.execute("DROP SEQUENCE IF EXISTS %s RESTRICT " % names)

    @api.multi
    def unlink(self):
        self._drop_sequences()
        return super(IrSequenceDateRange, self).unlink()

    @api.multi
    def write(self, values):
        if values.get("number_next"):
            seq_to_alter = self.filtered(
                lambda seq: seq.sequence_id.implementation == "standard")
            seq_to_alter.alter_sequence(number_next=values.get("number_next"))
        return super(IrSequenceDateRange, self).write(values)
