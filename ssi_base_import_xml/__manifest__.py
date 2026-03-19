# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# pylint: disable=locally-disabled, manifest-required-author

{
    "name": "SSI Base Import XML",
    "version": "14.0.1.0.0",
    "summary": "Import data records using XML files",
    "author": "PT. Simetri Sinergi Indonesia,OpenSynergy Indonesia",
    "category": "Generic Modules/Base",
    "website": "https://simetri-sinergi.id",
    "depends": ["base_import", "web"],
    # "data": [
    #     "security/ir.model.access.csv",
    #     "wizards/ssi_base_import_xml.xml",
    #     "templates/assets.xml",
    # ],
    # "qweb": ["static/src/xml/import_xml.xml"],
    "installable": True,
    "application": False,
    "license": "AGPL-3",
}
