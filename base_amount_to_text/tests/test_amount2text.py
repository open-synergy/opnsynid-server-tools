# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase

PYTHON_INDONESIA = """result=''
result_sen = ''
result_rupiah = ''

if value > 0:
    ones = [
        "", "Satu ","Dua ","Tiga ","Empat ", "Lima ","Enam ",
        "Tujuh ","Delapan ","Sembilan "
    ]
    tens = [
        "Sepuluh ","Sebelas ","Dua Belas ","Tiga Belas ",
        "Empat Belas ","Lima Belas ","Enam Belas ",
        "Tujuh Belas ","Delapan Belas ","Sembilan Belas "
    ]
    twenties = [
        "","","Dua Puluh ","Tiga Puluh ","Empat Puluh ",
        "Lima Puluh ","Enam Puluh ","Tujuh Puluh ",
        "Delapan Puluh ","Sembilan Puluh "
    ]
    thousands = ["","Ribu ","Juta ", "Milyar "]

    n3 = []
    r1 = ""

    ns = str(value)
    rupiah, sen = str(ns).split(".")

    if int(rupiah) > 0:
        for k in range(3, 33, 3):
            r = rupiah[-k:]
            q = len(rupiah) - k
            if q < -2:
                break
            else:
                if q >= 0:
                    n3.append(int(r[:3]))
                elif q >= -1:
                    n3.append(int(r[:2]))
                elif q >= -2:
                    n3.append(int(r[:1]))
            r1 = r

        for i, x in enumerate(n3):
            b1 = x % 10
            b2 = (x % 100)//10
            b3 = (x % 1000)//100
            if x == 0:
                continue
            else:
                t = thousands[i]
            if b2 == 0:
                if b1 == 1:
                    result_rupiah = 'se' + t + result_rupiah
                else:
                    result_rupiah = ones[b1] + t + result_rupiah
            elif b2 == 1:
                result_rupiah = tens[b1] + t + result_rupiah
            elif b2 > 1:
                result_rupiah = twenties[b2] + ones[b1] + t + result_rupiah
            if b3 > 0:
                result_rupiah = ones[b3] + "Ratus " + result_rupiah

        result_rupiah = result_rupiah.replace("seJuta", "Satu Juta")
        result_rupiah = result_rupiah.replace("seMilyar", "Satu Milyar")
        result_rupiah = result_rupiah.replace("Satu ratus", "Seratus")
        result_rupiah = result_rupiah.replace("ratus", "Ratus")
        result_rupiah = result_rupiah + "Rupiah"

        if int(sen) > 0:
            y = len(sen)
            for k in range(0,y):
                r = sen[k]
                if y == 1:
                    result_sen = ones[int(r)]
                elif y > 1:
                    n = int(sen)
                    if n > 0 and n < 9:
                        result_sen = ones[n]
                    else:
                        result_sen = result_sen + ones[int(r)]
            result_sen = " Koma " + result_sen + "Sen"

    result = result_rupiah + result_sen
"""

PYTHON_INDONESIA_ENG = """result=''
result_sen = ''
result_rupiah = ''

if value > 0:
    ones = [
        "", "One ","Two ","Three ","Four ",
        "Five ","Six ","Seven ","Eight ","Nine "
    ]
    tens = [
        "Ten ","Eleven ","Twelve ","Thirteen ",
        "Fourteen ","Fifteen ","Sixteen ",
        "Seventeen ","Eighteen ","Nineteen "
    ]
    twenties = [
        "","","Twenty ","Thirty ","Forty ",
        "Fifty ","Sixty ","Seventy ","Eighty ","Ninety "
    ]
    thousands = [
        "","Thousand ","Million ", "Billion ", "Trillion ",
    ]

    n3 = []
    r1 = ""

    ns = str(value)
    rupiah, sen = str(ns).split(".")

    if int(rupiah) > 0:
        for k in range(3, 33, 3):
            r = rupiah[-k:]
            q = len(rupiah) - k
            if q < -2:
                break
            else:
                if q >= 0:
                    n3.append(int(r[:3]))
                elif q >= -1:
                    n3.append(int(r[:2]))
                elif q >= -2:
                    n3.append(int(r[:1]))
            r1 = r

        for i, x in enumerate(n3):
            b1 = x % 10
            b2 = (x % 100)//10
            b3 = (x % 1000)//100
            if x == 0:
                continue
            else:
                t = thousands[i]
            if b2 == 0:
                result_rupiah = ones[b1] + t + result_rupiah
            elif b2 == 1:
                result_rupiah = tens[b1] + t + result_rupiah
            elif b2 > 1:
                result_rupiah = twenties[b2] + ones[b1] + t + result_rupiah
            if b3 > 0:
                result_rupiah = ones[b3] + "Hundred " + result_rupiah

        result_rupiah = result_rupiah + "Rupiah"

        if int(sen) > 0:
            n = int(sen)
            if n >= 0 and n <= 9:
                result_sen = ones[n]
            elif n >= 10 and n <= 19:
                p1 = n % 10
                result_sen = tens[p1]
            elif n >= 20 and n <= 99:
                p1 = n / 10
                p2 = n % 10
                result_sen = twenties[p1] + ones[p2]
            result_sen = " And " + result_sen + "Cent"

    result = result_rupiah + result_sen
"""


class TestAmount2Text(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(TestAmount2Text, self).setUp(*args, **kwargs)
        self.obj_res_lang = self.env['res.lang']
        self.obj_res_currency = self.env['res.currency']
        self.obj_amount2text = self.env['base.amount_to_text']

        self.IDR = self.env.ref('base.IDR')
        self.USD = self.env.ref("base.USD")
        self.lang_en = self.env.ref('base.lang_en')

        return result

    def _prepare_languange_IDR(self):
        data = {
            'code': 'id_IDR',
            'name': 'Indonesia',
            'translatable': 'translatable',
            'amount_to_text_ids': [
                (0, 0, {'currency_id': self.IDR.id,
                        'python_amount2text': PYTHON_INDONESIA})
            ],

        }
        return data

    def _prepare_currency_IDR(self):
        data = {
            'amount_to_text_ids': [
                (0, 0, {'lang_id': self.lang_en.id,
                        'python_amount2text': PYTHON_INDONESIA_ENG})
            ],
        }
        return data

    def test_amount_to_text_indo(self):
        # Create Languanges
        data_languange = self._prepare_languange_IDR()
        lang = self.obj_res_lang.\
            create(data_languange)

        # Check Create Languanges
        self.assertIsNotNone(lang)

        # Variables
        value_1 = 1000000.00
        value_2 = 2500350.05

        # Check Method Amount To Text Using Variable 1
        result_1 = self.obj_amount2text.get(
            value_1, self.IDR, lang)
        self.assertEqual(result_1, 'Satu Juta Rupiah')

        # Check Method Amount To Text Using Variable 2
        result_2 = self.obj_amount2text.get(
            value_2, self.IDR, lang)
        self.assertEqual(
            result_2,
            'Dua Juta Lima Ratus Ribu Tiga Ratus '
            'Lima Puluh Rupiah Koma Lima Sen')

    def test_amount_to_text_eng(self):
        # Update Currency
        data_currency = self._prepare_currency_IDR()
        self.IDR.write(data_currency)

        # Variables
        value_1 = 3550750.00
        value_2 = 19000.17

        # Check Method Amount To Text Using Variable 1
        result_1 = self.obj_amount2text.get(
            value_1, self.IDR, self.lang_en)
        self.assertEqual(
            result_1,
            'Three Million Five Hundred Fifty Thousand '
            'Seven Hundred Fifty Rupiah')

        # Check Method Amount To Text Using Variable 2
        result_2 = self.obj_amount2text.get(
            value_2, self.IDR, self.lang_en)
        self.assertEqual(
            result_2,
            'Nineteen Thousand Rupiah And Seventeen Cent')

    def test_no_amount_to_text_data(self):
        value_1 = 3550750.00
        result_1 = self.obj_amount2text.get(
            value_1, self.IDR, self.lang_en)
        self.assertEqual(
            result_1,
            "-")

    def test_use_user_profile_lang(self):
        data_languange = self._prepare_languange_IDR()
        lang = self.obj_res_lang.\
            create(data_languange)
        self.env.user.partner_id.lang = lang.code
        self.obj_amount2text.create({
            "currency_id": self.IDR.id,
            "lang_id": self.lang_en.id,
            "python_amount2text": PYTHON_INDONESIA_ENG,
        })

        # Variables
        value_1 = 1000000.00
        value_2 = 2500350.05

        # Check Method Amount To Text Using Variable 1
        result_1 = self.obj_amount2text.get(
            value_1, self.IDR)
        self.assertEqual(result_1, 'Satu Juta Rupiah')

        # Check Method Amount To Text Using Variable 2
        result_2 = self.obj_amount2text.get(
            value_2, self.IDR)
        self.assertEqual(
            result_2,
            'Dua Juta Lima Ratus Ribu Tiga Ratus '
            'Lima Puluh Rupiah Koma Lima Sen')

        self.env.user.partner_id.lang = self.lang_en.code

        result_3 = self.obj_amount2text.get(
            value_1, self.IDR)
        self.assertEqual(
            result_3,
            'One Million Rupiah')
