# Copyright 2026 OpenSynergy Indonesia
# Copyright 2026 PT. Simetri Sinergi Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree
from lxml.builder import E

from odoo import api, models

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo.addons.base.models.res_users import name_boolean_group, name_selection_groups


class ResGroups(models.Model):
    """
    Reworks the generated arch of ``base.user_groups_view`` (see
    ``res.groups._update_user_groups_view`` in Odoo core) so that
    application groups are bucketed under a ``user_group_section``
    (via ``ir.module.category.section_id``) instead of a flat list,
    ordered by the section's sequence.

    Applications whose category has no ``section_id`` are intentionally
    left out of the generated block: their groups remain manageable
    through the plain ``groups_id`` many2many field exposed on the
    "Other Groups" tab (see ``views/res_users_views.xml``).

    Unlike core, selection-kind applications are not additionally
    boxed by their parent category (``category_name``) — each
    application's field is placed directly under its section separator.
    This is safe because ``res.users.fields_get()`` (core, untouched)
    already sets each reified field's ``string`` to the application's
    own name, so the field is self-labelled without needing a wrapping
    ``<group string="...">``.

    The overall arch skeleton (three top-level groups: user type,
    selection groups, boolean groups) and every field/attrs computation
    is kept identical to Odoo core so upstream behavior (readonly
    dependency on User Type, hidden/extra category handling, the
    ``o_label_nowrap`` class) is preserved.
    """

    _name = "res.groups"
    _inherit = ["res.groups"]

    @api.model
    def _update_user_groups_view(self):
        # remove the language to avoid translations, it will be handled
        # at the view level
        self = self.with_context(lang=None)

        view = self.env.ref("base.user_groups_view", raise_if_not_found=False)
        if not (view and view.exists() and view._name == "ir.ui.view"):
            return

        if self._context.get("install_filename") or self._context.get(
            MODULE_UNINSTALL_FLAG
        ):
            # use a dummy view during install/upgrade/uninstall
            xml = E.field(name="groups_id", position="after")
        else:
            xml = self._get_sectioned_user_groups_view_arch()

        # serialize and update the view
        xml_content = etree.tostring(xml, pretty_print=True, encoding="unicode")
        if xml_content != view.arch:  # avoid useless xml validation if no change
            new_context = dict(view._context)
            new_context.pop("install_filename", None)
            new_context["lang"] = None
            view.with_context(new_context).write({"arch": xml_content})

    def _get_sectioned_user_groups_view_arch(self):
        group_no_one = self.env.ref("base.group_no_one")
        group_employee = self.env.ref("base.group_user")

        xml1 = [
            E.separator(string="User Type", colspan="2", groups="base.group_no_one")
        ]
        xml_by_section = {}

        user_type_field_name = ""
        user_type_readonly = str({})

        sorted_tuples = sorted(
            self.get_groups_by_application(),
            key=lambda t: t[0].xml_id != "base.module_category_user_type",
        )
        for app, kind, gs, _category_name in sorted_tuples:
            attrs = {}
            # hide groups in categories 'Hidden' and 'Extra' (except group_no_one)
            if app.xml_id in self._get_hidden_extra_categories():
                attrs["groups"] = "base.group_no_one"

            if app.xml_id == "base.module_category_user_type":
                # User type (employee, portal, public) stays a single
                # selection field at the top, exactly as in core.
                field_name = name_selection_groups(gs.ids)
                user_type_field_name = field_name
                user_type_readonly = str(
                    {"readonly": [(user_type_field_name, "!=", group_employee.id)]}
                )
                attrs["widget"] = "radio"
                attrs["groups"] = "base.group_no_one"
                xml1.append(E.field(name=field_name, **attrs))
                xml1.append(E.newline())
                continue

            section = app.section_id
            if not section:
                # Left out on purpose: managed via the "Other Groups" tab.
                continue

            bucket = xml_by_section.setdefault(
                section, {"selection": [], "boolean": []}
            )

            if kind == "selection":
                # Placed directly (no per-application-parent wrapping
                # group): the field's own fields_get() string already
                # shows the application's name next to its combobox.
                field_name = name_selection_groups(gs.ids)
                attrs["attrs"] = user_type_readonly
                bucket["selection"].append(E.newline())
                bucket["selection"].append(E.field(name=field_name, **attrs))
                bucket["selection"].append(E.newline())
            else:
                # application separator with boolean fields
                app_name = app.name or "Other"
                bucket["boolean"].append(
                    E.separator(string=app_name, colspan="4", **attrs)
                )
                attrs["attrs"] = user_type_readonly
                for g in gs:
                    field_name = name_boolean_group(g.id)
                    if g == group_no_one:
                        # make the group_no_one invisible in the form view
                        bucket["boolean"].append(
                            E.field(name=field_name, invisible="1", **attrs)
                        )
                    else:
                        bucket["boolean"].append(E.field(name=field_name, **attrs))

        if user_type_field_name:
            user_type_attrs = {
                "invisible": [(user_type_field_name, "!=", group_employee.id)]
            }
        else:
            user_type_attrs = {}

        # Flatten the per-section buckets into the two core containers
        # (selection groups / boolean groups), ordered by section
        # sequence, with a separator marking each section's start.
        xml2, xml3 = [], []
        for section in sorted(xml_by_section, key=lambda s: (s.sequence, s.name)):
            bucket = xml_by_section[section]
            if bucket["selection"]:
                xml2.append(E.separator(string=section.name, colspan="2"))
                xml2.extend(bucket["selection"])
            if bucket["boolean"]:
                xml3.append(E.separator(string=section.name, colspan="4"))
                xml3.extend(bucket["boolean"])

        xml3.append({"class": "o_label_nowrap"})

        xml = E.field(
            E.group(*xml1, col="2"),
            E.group(*xml2, col="2", attrs=str(user_type_attrs)),
            E.group(*xml3, col="4", attrs=str(user_type_attrs)),
            name="groups_id",
            position="replace",
        )
        xml.addprevious(etree.Comment("GENERATED AUTOMATICALLY BY GROUPS (sectioned)"))
        return xml
