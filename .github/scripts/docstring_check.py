#!/usr/bin/env python3
"""Aturan gerbang docstring modul Odoo SSI — SUMBER TUNGGAL.

Pasalnya milik skill `odoo-development`,
references/odoo-module-guidelines/10-docstring.md; berkas ini menegakkannya secara
mekanis, dan ia dipakai DUA gerbang sekaligus:

* lokal — `assets/verify-module.sh` (gerbang "setiap class & method punya
  docstring") meng-impor modul ini dari direktorinya sendiri;
* CI — `.github/workflows/docstring-gate.yml` di tiap repo modul menjalankan
  `python3 .github/scripts/docstring_check.py ci <merge-base>`. Salinan di repo
  modul dipasang `sync-config.sh` (skill odoo-development-repo-ops) untuk repo lama
  dan `apply-ssi-overrides.sh` (skill odoo-development-repo) untuk repo baru,
  keduanya menyalin LANGSUNG dari sini dan membuktikan keidentikannya byte-per-byte.

KENAPA SATU BERKAS. Sampai v3.73.3 logika yang sama hidup di dua salinan tulisan
tangan — satu di `verify-module.sh`, satu inline di `docstring-gate.yml` — dengan
kewajiban prosa "bila salah satu diubah, ubah keduanya". v3.68.0 mengubah satu
salinan saja (pembebasan class ekstensi), dan PR `open-synergy/ssi-school#399`
buntu: gerbang lokal membebaskan class ekstensi, gerbang CI menagihnya, dan baris
`.validator-exceptions` yang memuaskan CI dijatuhkan gerbang lokal sebagai
penyimpangan tak terpakai. Kewajiban menyinkronkan dua salinan tidak ditegakkan
apa pun kecuali ingatan; satu berkas menghapus kewajibannya.

Yang TIDAK tinggal di sini, dan kenapa: cara MENCETAK hasil di `verify-module.sh`
(kerangka gate/`result()`-nya melayani puluhan gerbang lain) dan parser
`.validator-exceptions` lengkapnya (memvalidasi bentuk baris & penanda
`@warisan` untuk semua gerbang). Parser di bawah hanya subset yang CI butuhkan:
ia membaca baris `module <kunci> -- <alasan>` yang sah dan mengabaikan sisanya —
baris yang bentuknya salah ditagih gerbang lokal, bukan di sini.

Berkas ini ikut tersalin ke repo modul, dan gerbang CI memeriksa SETIAP berkas
`.py` yang disentuh PR — termasuk dirinya sendiri saat pertama dipasang. Karena
itu setiap class & fungsi di sini wajib berdocstring.
"""
import ast
import os
import re
import subprocess
import sys

# --- identitas aturan --------------------------------------------------------
# LABEL adalah judul butir di `verify-module.sh`; RULE adalah kunci aturan dalam
# `.validator-exceptions` (kontrak validator §13), diturunkan dari LABEL dengan
# rumus `_slug()` verify-module.sh. verify-module.sh MEMERIKSA kesamaan keduanya
# setiap kali jalan, jadi rumus yang menyimpang gagal keras, bukan diam-diam
# membuat baris pengecualian berlaku di satu gerbang saja.
LABEL = "setiap class & method punya docstring"
RULE = re.sub(r"[^a-z0-9]+", "-", LABEL.lower()).strip("-")[:60]

# --- pengecualian TERTUTUP fungsi (10-docstring.md §Pengecualian) ------------
# Jangan ditambah tanpa mengubah file panduan itu lebih dulu.
#
# DUA di antaranya BERSYARAT, dan nama method saja TIDAK cukup untuk memutuskan:
# panduan hanya membebaskan onchange Pattern A/B/C (10-onchange.md) dan
# `_selection_*` satu baris. Versi lama gerbang membebaskan SETIAP `onchange_*`
# dan `_selection_*` hanya dari prefix namanya, sehingga Pattern E — yang
# memanggil `_super` atau bercabang non-trivial — lolos hijau padahal panduan
# mewajibkannya berdocstring. Gerbang yang lebih longgar dari aturannya bukan
# gerbang.
EXEMPT_EXACT = {"_insert_form_element", "_get_policy_field"}
# `_onchange_*` ikut dipertimbangkan di sini walaupun menyimpang dari konvensi
# penamaan: penyimpangan namanya ditagih gerbang tersendiri di verify-module.sh,
# bukan dengan diam-diam menghapus pembebasan docstring-nya.
ONCHANGE_PREFIX = ("onchange_", "_onchange_")


def real_body(fn):
    """Statement body sebuah fungsi, tanpa baris docstring-nya."""
    return fn.body[1:] if ast.get_docstring(fn) is not None else fn.body


def is_simple_onchange(fn):
    """True bila onchange-nya Pattern A/B/C — reset/set field, titik.

    Batasnya: setiap statement hanya assignment (boleh dibungkus `if`), dan tak
    ada panggilan apa pun. `_super`, `search()`, loop, dan `return` mendorongnya
    ke Pattern E, yang oleh 10-docstring.md tetap wajib berdocstring.

    `decorator_list` sengaja TIDAK ditelusuri: `@api.onchange("x")` sendiri sebuah
    ``ast.Call``, jadi menelusurinya membuat SETIAP onchange terhitung tidak
    sederhana — 394 salah-vonis saat aturan ini dikalibrasi ke korpus 14.0.
    """
    for st in real_body(fn):
        if not isinstance(st, (ast.Assign, ast.If)):
            return False
        for node in ast.walk(st):
            if isinstance(
                node,
                (ast.Call, ast.For, ast.While, ast.Try, ast.With, ast.Return, ast.Lambda),
            ):
                return False
    return True


def doc_exempt(fn):
    """True bila fungsi ini termasuk pengecualian TERTUTUP 10-docstring.md."""
    if fn.name in EXEMPT_EXACT:
        return True
    if fn.name.startswith(ONCHANGE_PREFIX):
        return is_simple_onchange(fn)
    if fn.name.startswith("_selection_"):
        return len(real_body(fn)) <= 1
    return False


# --- class EKSTENSI dibebaskan (kontrak validator §14) ------------------------
# Sejak 10-docstring.md v3.67.0 class ekstensi DILARANG berdocstring: docstring
# pertama non-kosong dalam MRO merebut `ir.model.info` (core
# `ir_model.py:358`), sehingga keterangan model basis tak pernah sampai ke
# konsumen REST/MCP. Tanpa pembebasan ini gerbang menagih class yang ditulis
# BENAR menurut pasalnya sendiri (kasus ssi-school#399, run 36025607429).
#
# ARAH GAGAL (§14a) — pembebasan ini MEMBEBASKAN, dan pembebasan salah tak pernah
# diprotes siapa pun. Karena itu, bila class punya `_name` DAN `_inherit` tetapi
# salah satunya bukan literal string (dirakit dinamis, dari variabel,
# f-string), keanggotaan `_name` di `_inherit` tak bisa dipastikan: fungsi
# memulangkan False dan temuan TETAP LAHIR. Salah menuduh bisa diprotes; salah
# membebaskan tidak.
#
# Yang TIDAK dicek literalnya: `_inherit` apa pun TANPA `_name` dibebaskan —
# tanpa `_name`, Odoo memakai `_inherit` sebagai nama model, jadi class itu
# ekstensi apa pun isi `_inherit`-nya. Batas yang diketahui (prevalensi korpus
# 14.0: 0 dari 932 ekstensi, review 24 Sep 2026): assign ganda (diambil yang
# PERTAMA, Python memakai yang terakhir), `_name` di dalam `if`, class
# non-Odoo ber-`_inherit`, dan `_inherit = None`/`[]` ikut dibebaskan.


def lit_strs(value):
    """Daftar string literal dari node, atau None bila TAK BISA dipastikan."""
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return [value.value]
    if isinstance(value, (ast.List, ast.Tuple)):
        out = []
        for e in value.elts:
            if isinstance(e, ast.Constant) and isinstance(e.value, str):
                out.append(e.value)
            else:
                return None
        return out
    return None


def class_assign(cls, field):
    """Nilai assignment `field` langsung di body class, atau None.

    Nama dicocokkan PERSIS — `_inherits` (delegation) bukan `_inherit`.
    """
    for st in cls.body:
        if isinstance(st, ast.Assign):
            for t in st.targets:
                if isinstance(t, ast.Name) and t.id == field:
                    return st.value
        elif isinstance(st, ast.AnnAssign):
            if isinstance(st.target, ast.Name) and st.target.id == field:
                return st.value
    return None


def is_extension_class(cls):
    """True bila class MENGEKSTENSI model yang sudah ada, bukan mendefinisikannya.

    Ekstensi = `_inherit` tanpa `_name`, ATAU `_name` yang muncul di dalam
    `_inherit`-nya sendiri. Keduanya menaruh class di MRO model yang sudah ada.
    Class basis yang mewarisi mixin (`_name` TIDAK ada di `_inherit`-nya) BUKAN
    ekstensi — ia tetap wajib berdocstring.
    """
    inh_node = class_assign(cls, "_inherit")
    if inh_node is None:
        return False
    name_node = class_assign(cls, "_name")
    if name_node is None:
        return True
    names = lit_strs(name_node)
    inherits = lit_strs(inh_node)
    if names is None or inherits is None:
        return False
    return any(n in inherits for n in names)


# --- pemindaian ---------------------------------------------------------------


def is_checked_path(path):
    """True bila berkas `.py` ini ikut diperiksa gerbang docstring.

    `__init__.py` dilewati: isinya hanya import. Satu-satunya tempat keputusan ini
    ditulis — `verify-module.sh` dan mode CI sama-sama memanggilnya.
    """
    return os.path.basename(path) != "__init__.py"


def scan_tree(tree):
    """Simbol tanpa docstring yang DITAGIH, dan jumlah class ekstensi dibebaskan.

    :param tree: hasil ``ast.parse`` satu berkas
    :return: ``(missing, freed)`` — ``missing`` list ``(nama, lineno)`` dalam
        urutan ``ast.walk`` (duplikat nama TIDAK digabung — pemanggil yang
        memutuskan); ``freed`` jumlah class ekstensi TANPA docstring yang
        dibebaskan (§14d: pembatalan dihitung supaya bisa dicetak)
    """
    missing = []
    freed = 0
    for node in ast.walk(tree):
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if doc_exempt(node):
                continue
        elif is_extension_class(node):
            # Class ekstensi: DILARANG berdocstring (10-docstring.md v3.67.0).
            if ast.get_docstring(node) is None:
                freed += 1
            continue
        if ast.get_docstring(node) is None:
            missing.append((node.name, node.lineno))
    return missing, freed


def missing_symbols(source):
    """{nama simbol: lineno} untuk class/method tanpa docstring, dan ``freed``.

    Nama yang muncul lebih dari sekali disimpan kemunculan PERTAMA-nya — di CI
    pembandingnya himpunan nama, bukan posisi.

    :return: ``(found, freed)``; ``found`` None bila sumbernya gagal di-parse —
        berkas yang sintaksnya rusak ditagih flake8/pylint, dan menebak isinya di
        sini hanya menghasilkan temuan palsu
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None, 0
    missing, freed = scan_tree(tree)
    found = {}
    for name, lineno in missing:
        found.setdefault(name, lineno)
    return found, freed


# --- mode CI: hanya pelanggaran BARU terhadap merge-base ------------------------
# KENAPA HANYA PELANGGARAN BARU. Korpus 14.0 memuat ~12.400 class/method tanpa
# docstring di 77 repo (sapuan 2026-08). Memerahkan semuanya sekaligus tidak membuat
# satu docstring pun tertulis; ia hanya membuat gerbang ini dimatikan. Yang ditahan
# karena itu HANYA simbol yang tak berdocstring DAN belum ada di merge-base. Utang
# warisan diukur terpisah lewat `audit-sweep.sh` (skill odoo-development-repo-ops).


def _git(*args):
    """Keluaran sebuah perintah git, atau None bila perintahnya gagal."""
    proc = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    return proc.stdout if proc.returncode == 0 else None


def _module_root(path):
    """Direktori modul Odoo terdekat di atas `path`, atau None."""
    cur = os.path.dirname(path)
    while cur:
        if os.path.isfile(os.path.join(cur, "__manifest__.py")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    return None


def _read_exceptions(module):
    """Kunci milik validator `module` di <modul>/.validator-exceptions.

    Subset parser verify-module.sh: hanya baris sah `module <kunci> -- <alasan>`
    yang dibaca; baris lain dilewati (bentuk yang salah ditagih gerbang lokal).
    """
    keys = set()
    path = os.path.join(module, ".validator-exceptions")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                head, sep, reason = line.partition(" -- ")
                if not sep or not reason.strip():
                    continue
                parts = head.split(None, 1)
                if len(parts) == 2 and parts[0] == "module":
                    keys.add(parts[1].strip())
    return keys


def run_ci(merge_base):
    """Gerbang CI: tagih class/method BARU tanpa docstring; exit 0 lolos, 1 gagal."""
    baseline_cache = {}
    exc_cache = {}

    def module_baseline(module):
        """Nama simbol tanpa docstring di SELURUH modul, pada merge-base.

        Pembandingnya sengaja setingkat MODUL, bukan per berkas. Standar SSI
        mengizinkan struktur berkas ditata ulang selama XML ID & nama class utuh
        (02-core-principles.md), dan perbandingan per berkas membaca pemindahan
        class warisan sebagai "simbol baru" — lalu menuntut docstring untuk kode
        yang tidak disentuh PR itu. Deteksi rename bawaan git tidak menutup
        lubangnya: berkas yang dipindah SEKALIGUS diubah isinya jatuh di bawah
        ambang kemiripan dan terbaca sebagai hapus + tambah.
        """
        if module not in baseline_cache:
            names = set()
            listing = _git("ls-tree", "-r", "--name-only", merge_base, "--", module)
            for path in (listing or "").splitlines():
                if not path.endswith(".py"):
                    continue
                if not is_checked_path(path):
                    continue
                old_src = _git("show", "%s:%s" % (merge_base, path))
                if not old_src:
                    continue
                found, _freed = missing_symbols(old_src)
                if found:
                    names.update(found)
            baseline_cache[module] = names
        return baseline_cache[module]

    def excepted(module, key):
        """True bila kunci temuan ini tercakup <modul>/.validator-exceptions."""
        if module not in exc_cache:
            exc_cache[module] = _read_exceptions(module)
        return key in exc_cache[module]

    # --- berkas .py yang disentuh PR ini ---------------------------------------
    status = _git("diff", "--name-status", "-M", merge_base, "HEAD")
    if status is None:
        sys.exit("ERROR: `git diff` terhadap merge-base gagal.")

    pairs = []  # (path_baru, path_lama|None)
    for line in status.splitlines():
        cols = line.split("\t")
        code = cols[0]
        if code.startswith("D"):
            continue
        if code.startswith("R") and len(cols) == 3:
            pairs.append((cols[2], cols[1]))
        elif len(cols) >= 2:
            pairs.append((cols[1], cols[1]))

    findings = []
    checked = 0
    # Jumlah class ekstensi tanpa docstring yang dibebaskan di berkas HEAD (§14d).
    freed_ext = 0
    for new_path, old_path in pairs:
        if not new_path.endswith(".py"):
            continue
        if not is_checked_path(new_path):
            continue
        # setup/ hanya berisi symlink hasil setuptools-odoo.
        if new_path.startswith("setup/"):
            continue
        if not os.path.isfile(new_path):
            continue
        with open(new_path, encoding="utf-8") as fh:
            new_missing, freed = missing_symbols(fh.read())
        if new_missing is None:
            continue
        freed_ext += freed
        checked += 1
        module = _module_root(new_path)
        if module:
            baseline = module_baseline(module)
        else:
            # Di luar modul Odoo (skrip lepas): tak ada modul untuk dibandingkan,
            # jadi pembandingnya kembali ke berkas itu sendiri di merge-base.
            old_src = _git("show", "%s:%s" % (merge_base, old_path)) if old_path else None
            baseline = set(missing_symbols(old_src)[0] or {}) if old_src else set()
        for name, lineno in sorted(new_missing.items(), key=lambda kv: kv[1]):
            if name in baseline:
                continue  # utang warisan — diukur audit-sweep.sh, bukan di sini
            rel = os.path.relpath(new_path, module) if module else new_path
            if module and excepted(module, "%s|%s %s" % (RULE, rel, name)):
                print("  ⊘ %s:%d %s  [.validator-exceptions]" % (new_path, lineno, name))
                continue
            findings.append((new_path, lineno, name))

    print("Berkas .py diperiksa: %d" % checked)
    if freed_ext:
        # §14d: pembatalan tidak boleh senyap — baris info, bukan kegagalan.
        print(
            "  · %d class ekstensi dibebaskan dari kewajiban docstring —"
            " 10-docstring.md justru MELARANGnya berdocstring" % freed_ext
        )
    if not findings:
        print("")
        print("LOLOS: tidak ada class/method baru tanpa docstring.")
        return 0

    print("")
    print("GAGAL: %d class/method BARU tanpa docstring." % len(findings))
    print("")
    for path, lineno, name in findings:
        print("  ✗ %s:%d %s" % (path, lineno, name))
    print("")
    print("Aturannya: skill odoo-development,")
    print("  references/odoo-module-guidelines/10-docstring.md")
    print("Reproduksi & perbaiki di lokal:")
    print("  assets/vs-head.sh verify-module.sh <path-modul>")
    print("")
    print("Pengecualiannya TERTUTUP. Bila sebuah temuan memang tidak boleh")
    print("diperbaiki, daftarkan di <modul>/.validator-exceptions berikut")
    print("alasannya (kontrak validator §13) — jangan matikan gerbang ini.")
    print("")
    print("MODUL YANG DIPINDAH ANTAR REPO: gerbang ini membandingkan ke")
    print("merge-base, jadi SELURUH berkas modul pindahan terbaca BARU dan")
    print("utang docstring warisannya ikut memerah. Baris untuk temuan yang")
    print("memang sudah gagal di repo asal ditulis dengan penanda kelas 2:")
    print("  module <kunci> -- @warisan(<repo-asal>) <alasan>")
    print("Penanda itu ditaruh di AWAL alasan, dibuktikan dengan menjalankan")
    print("validator atas modul di repo asal. Temuan yang lahir dari pemindahan")
    print("itu sendiri BUKAN warisan — perbaiki, jangan tandai.")
    return 1


def main(argv):
    """CLI: ``docstring_check.py ci <merge-base>`` — dijalankan dari akar repo modul."""
    if len(argv) == 3 and argv[1] == "ci":
        return run_ci(argv[2])
    print(
        "pakai: docstring_check.py ci <merge-base>   (dari akar repo modul)",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
