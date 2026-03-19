# Copyright 2024 OpenSynergy Indonesia
# Copyright 2024 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import ast
import base64

from lxml import etree

from odoo import _, fields, models


class BaseImportXML(models.TransientModel):
    _name = "base_import_xml"
    _description = "Import Data from XML"

    model_name = fields.Char(
        string="Model",
        readonly=True,
    )
    file_data = fields.Binary(
        string="XML File",
        required=True,
        attachment=False,
    )
    file_name = fields.Char(string="File Name")
    error_message = fields.Text(
        string="Messages",
        readonly=True,
    )

    def action_import(self):
        self.ensure_one()
        model_name = self.model_name or self.env.context.get("active_model")

        if not model_name:
            self.error_message = _(
                "Target model is unknown. Please reload and try again."
            )
            return self._reopen()

        if model_name not in self.env:
            self.error_message = _("Model '%s' not found.") % model_name
            return self._reopen()

        try:
            xml_bytes = base64.b64decode(self.file_data)
            # Strip UTF-8 BOM and leading whitespace — lxml requires the XML
            # declaration to start at byte 0.
            xml_bytes = xml_bytes.lstrip(b"\xef\xbb\xbf").lstrip()
            root = etree.fromstring(xml_bytes)
        except Exception as e:
            self.error_message = _("Error parsing XML file: %s") % str(e)
            return self._reopen()

        success_count, update_count, errors = self._process_records(model_name, root)

        msg_parts = [
            _("Created: %d record(s). Updated: %d record(s).")
            % (success_count, update_count)
        ]
        if errors:
            msg_parts.append(_("\nErrors encountered:"))
            msg_parts.extend(errors)

        self.error_message = "\n".join(msg_parts)
        return self._reopen()

    def _process_records(self, model_name, root):
        """Process all <record> elements from XML root."""
        success_count = 0
        update_count = 0
        errors = []

        # Support both <odoo><data><record ...> and bare <record ...> roots.
        if root.tag in ("odoo", "openerp"):
            data_nodes = root.findall("data") or [root]
            record_elems = []
            for data_node in data_nodes:
                record_elems.extend(data_node.findall("record"))
        elif root.tag == "data":
            record_elems = root.findall("record")
        else:
            # Fallback: root itself is treated as a container of <record> elements.
            record_elems = root.findall("record")

        for i, record_elem in enumerate(record_elems, start=1):
            record_model = record_elem.get("model") or model_name
            result = self._process_record(record_model, record_elem, i)
            success_count += result.get("success", 0)
            update_count += result.get("update", 0)
            errors.extend(result.get("errors", []))

        return success_count, update_count, errors

    def _process_record(self, model_name, record_elem, row_num):
        """Process a single <record> element."""
        if model_name not in self.env:
            return {
                "errors": [_("Row %d: model '%s' not found.") % (row_num, model_name)]
            }

        # Extract the id attribute to use as xml_id (__export__.<id>).
        id_attr = record_elem.get("id", "").strip()

        vals = {}
        errors = []

        target_model = self.env[model_name]

        for field_elem in record_elem.findall("field"):
            field_result = self._process_field(target_model, field_elem, row_num, vals)
            errors.extend(field_result)

        try:
            with self.env.cr.savepoint():
                success, update = self._import_or_update_record(
                    model_name, target_model, vals, id_attr
                )
            return {
                "success": 1 if success else 0,
                "update": 1 if update else 0,
                "errors": errors,
            }
        except Exception as e:
            errors.append(_("Row %d: %s") % (row_num, str(e)))
            return {"errors": errors}

    def _process_field(self, target_model, field_elem, row_num, vals):
        """Process a single <field> element and populate vals dict."""
        errors = []
        field_name = field_elem.get("name")
        if not field_name or field_name not in target_model._fields:
            return errors

        field = target_model._fields[field_name]
        ref_attr = field_elem.get("ref")
        eval_attr = field_elem.get("eval")

        if ref_attr:
            # Resolve an XML ID reference to a record id.
            try:
                vals[field_name] = self.env.ref(ref_attr).id
            except Exception:
                errors.append(
                    _("Row %d, field '%s': ref '%s' not found.")
                    % (row_num, field_name, ref_attr)
                )
        elif eval_attr is not None:
            # Parse eval expression safely using ast.literal_eval.
            try:
                vals[field_name] = ast.literal_eval(eval_attr)
            except (ValueError, SyntaxError) as e:
                errors.append(
                    _("Row %d, field '%s': eval error: %s") % (row_num, field_name, e)
                )
        else:
            raw_text = field_elem.text or ""
            text = raw_text.strip()
            if field.type in ("integer",):
                try:
                    vals[field_name] = int(text) if text else 0
                except ValueError:
                    vals[field_name] = 0
            elif field.type in ("float", "monetary"):
                try:
                    vals[field_name] = float(text) if text else 0.0
                except ValueError:
                    vals[field_name] = 0.0
            elif field.type == "boolean":
                vals[field_name] = text.lower() in ("1", "true", "yes")
            elif field.type in ("text", "html"):
                # Preserve internal whitespace/indentation (e.g. CDATA code blocks).
                vals[field_name] = raw_text.strip("\n")
            else:
                vals[field_name] = text

        return errors

    def _import_or_update_record(self, model_name, target_model, vals, id_attr):
        """Create or update a record based on id_attr (xml_id).

        Returns:
            tuple: (success_flag, update_flag)
        """
        IrModelData = self.env["ir.model.data"]

        if id_attr:
            # Look up existing record via __export__.<id> xml_id.
            existing = self.env.ref("__export__.%s" % id_attr, raise_if_not_found=False)
            if existing:
                existing.write(vals)
                return False, True
            else:
                new_record = target_model.create(vals)
                IrModelData.create(
                    {
                        "module": "__export__",
                        "name": id_attr,
                        "model": model_name,
                        "res_id": new_record.id,
                        "noupdate": False,
                    }
                )
                return True, False
        else:
            target_model.create(vals)
            return True, False

    def _reopen(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }
