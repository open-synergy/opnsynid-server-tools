# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Base Amount To Text',
    'version': '8.0.1.0.0',
    'summary': 'Add the capability to have amount to text method',
    'author': 'Michael Viriyananda, Andhitia Rama, '
              'OpenSynergy Indonesia',
    'website': 'https://opensynergy-indonesia.com',
    'category': 'Base',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_lang_view.xml',
        'views/res_currency_view.xml'
    ],
    'installable': True,
    'license': 'AGPL-3',
}
