# -*- coding: utf-8 -*-
# Copyright 2018 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models

FORMATROMAN = (
    ('M',  1000),
    ('CM', 900),
    ('D',  500),
    ('CD', 400),
    ('C',  100),
    ('XC', 90),
    ('L',  50),
    ('XL', 40),
    ('X',  10),
    ('IX', 9),
    ('V',  5),
    ('IV', 4),
    ('I',  1)
)


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    def _convert_to_roman(self, n):
        result = ""
        for numeral, integer in FORMATROMAN:
            while n >= integer:
                result += numeral
                n -= integer
        return result

    def _interpolation_dict_context(self, context=None):
        res = super(IrSequence, self)._interpolation_dict_context(context)
        dict_roman = res.copy()
        for key, value in res.iteritems():
            dict_roman['rom_' + key] =\
                self._convert_to_roman(int(value))
        return dict_roman
