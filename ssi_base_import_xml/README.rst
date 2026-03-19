.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
  :target: https://www.gnu.org/licenses/agpl
  :alt: License: AGPL-3

===============
Base Import XML
===============

Tujuan Modul
============

Modul ini menyediakan fitur **Import data melalui file XML** pada Odoo 14.
Sebuah tombol **Import XML** ditambahkan pada control panel di setiap list view.
Saat diklik, sebuah dialog wizard akan muncul di mana pengguna dapat mengunggah
file ``.xml`` untuk mengimpor data secara massal ke model yang sedang dibuka.

Mekanisme XML ID (Upsert)
=========================

Mekanisme import ini secara otomatis mengelola **XML ID** untuk setiap record
yang diimpor:

* Setiap ``<record>`` dalam file XML **wajib** memiliki atribut ``id``.
* XML ID yang disimpan ke database menggunakan prefix ``__export__``,
  sehingga menjadi ``__export__.<id_dari_file>``.
  Contoh: ``id="contact_alice"`` → XML ID = ``__export__.contact_alice``.
* Jika record dengan XML ID yang sama **belum ada** di database, record baru
  akan dibuat (**insert**).
* Jika record dengan XML ID yang sama **sudah ada** di database, record tersebut
  akan diperbarui (**update**). Tidak ada duplikasi data.

Perilaku ini memungkinkan file XML yang sama dapat dijalankan ulang kapan pun
untuk memperbarui data tanpa membuat record duplikat.

Format File XML
===============

File XML harus mengikuti format data standar Odoo::

    <?xml version="1.0" encoding="utf-8"?>
    <odoo>
        <data>
            <record id="contact_alice" model="res.partner">
                <field name="name">Alice</field>
                <field name="email">alice@example.com</field>
                <field name="is_company" eval="False"/>
            </record>
            <record id="contact_bob" model="res.partner">
                <field name="name">Bob</field>
                <field name="email">bob@example.com</field>
                <field name="country_id" ref="base.id_ID"/>
            </record>
        </data>
    </odoo>

Atribut ``<record>`` yang didukung:

* **id** *(wajib)* — identifier unik record; digunakan sebagai basis XML ID
  dengan prefix ``__export__``.
* **model** *(wajib)* — technical name model Odoo target.
  Record dengan model yang tidak cocok dengan model yang sedang dibuka akan
  dilewati.

Atribut ``<field>`` yang didukung:

* **name** *(wajib)* — nama field pada model target. Field yang tidak dikenal
  akan diabaikan.
* *(isi teks)* — nilai biasa; otomatis di-cast ke int/float/boolean untuk
  field numerik dan boolean.
* **eval** — ekspresi Python yang dievaluasi sebagai nilai field
  (contoh: ``eval="True"``, ``eval="42"``).
* **ref** — XML ID dari record terkait; database id-nya digunakan sebagai nilai
  (berguna untuk field Many2one).

Instalasi
=========

1. Clone branch 14.0 dari repository
   https://github.com/open-synergy/opnsynid-server-tools
2. Tambahkan path repository ke konfigurasi (addons-path)
3. Update daftar modul
4. Buka menu *Apps → Apps → Main Apps*
5. Cari *Base Import XML*
6. Install modul

Cara Penggunaan
===============

1. Buka tampilan list view manapun (contoh: Contacts → Contacts).
2. Klik tombol **Import XML** yang muncul di control panel (baris atas).
3. Pada dialog yang muncul, klik **Upload a file** dan pilih file ``.xml``.
4. Klik **Import**.
5. Area *Messages* akan menampilkan jumlah record yang berhasil diimpor
   beserta detail error jika ada.

Bug Tracker
===========

Bugs dilacak di `GitHub Issues <https://github.com/open-synergy/opnsynid-server-tools/issues>`_.
Jika menemukan masalah, periksa terlebih dahulu apakah issue tersebut sudah
dilaporkan di sana.

Credits
=======

Authors
-------

* PT. Simetri Sinergi Indonesia
* OpenSynergy Indonesia
