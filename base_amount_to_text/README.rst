.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3
    
===================
Base Amount To Text
===================

This module allows defining method "amount to text" as python code.
The method can be registered for each languanges or currencies.

Installation
============

To install this module, you need to:

1.  Clone the branch 8.0 of the repository https://github.com/open-synergy/opnsynid-server-tools
2.  Add the path to this repository in your configuration (addons-path)
3.  Update the module list
4.  Go to menu *Setting -> Modules -> Local Modules*
5.  Search For *Base Amount To Text*
6.  Install the module

Usage
=====
To use this module, you need to:

1. Go to menu *Setting -> Translations -> Languanges* or
   Go to menu *Accounting -> Miscellaneous -> Currencies*
2. Edit or create one.
3. There will be a new field named *Amount To Text*
4. Click add an item
5. There will be a new field named *Python Definition for Method Amount To Text*
6. Fill this field with a python code
7. To call the method use <model:base.amount_to_text>.amount_to_text(value)
   Example: account_invoice
   
   obj_base_amount2text = self.env['base.amount_to_text']
   obj_res_currency = self.env['res.currency']
   obj_res_lang = self.env['res.lang']

   lang = self.obj_res_lang.search(
      [('code', '=', 'en_US')])
   curr = self.obj_res_currency.search(
      [('name', '=', 'IDR')])
   amount2text = self.obj_amount2text.search([
         ('currency_id', '=', curr.id),
         ('lang_id', '=', lang.id)
   ])

   result = amount2text.amount_to_text(self.amount_total)


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/open-synergy/opnsynid-server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.


Credits
=======

Contributors
------------

* Michael Viriyananda <viriyananda.michael@gmail.com>
* Andhitia Rama <andhitia.r@gmail.com>

Maintainer
----------

.. image:: https://opensynergy-indonesia.com/logo.png
   :alt: OpenSynergy Indonesia
   :target: https://opensynergy-indonesia.com

This module is maintained by the OpenSynergy Indonesia.
