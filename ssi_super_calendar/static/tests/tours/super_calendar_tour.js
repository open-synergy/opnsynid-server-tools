odoo.define("ssi_super_calendar.super_calendar_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/super_calendar/01-view-availability.md
    tour.register(
        "ssi_super_calendar_super_calendar_view_availability",
        {
            test: true,
        },
        [
            // ── Flow 1 — Open the Settings > Technical > Super Calendar menu.
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Settings app",
                trigger: '.o_app[data-menu-xmlid="base.menu_administration"]',
            },
            {
                content: "Open the Technical menu",
                trigger: '.o_menu_sections [data-menu-xmlid="base.menu_custom"]',
            },
            {
                content: "Open the Super Calendar menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="ssi_super_calendar.super_calendar_menu"]',
            },
            // ── Flow 2 — The list shows the busy periods of every partner.
            {
                content: "Super Calendar list is displayed",
                trigger:
                    ".o_control_panel .breadcrumb-item.active:contains(Super Calendar)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only.
                },
            },
            {
                content: "The personal period is listed",
                trigger: ".o_data_row:contains(Tour Personal Leave)",
                extra_trigger: ".o_data_row:contains(Tour Public Holiday)",
                run: function () {
                    // Assertion only.
                },
            },
            // ── Flow 3 — Open the Filters menu and select Applies to Everyone.
            {
                content: "Open the Filters menu",
                trigger: ".o_search_options .o_filter_menu button",
            },
            {
                content: "Select the Applies to Everyone filter",
                trigger: ".o_filter_menu .dropdown-item:contains(Applies to Everyone)",
                run: function () {
                    this.$anchor[0].click();
                },
            },
            // ── Flow 4 — Only the periods that apply to everyone remain.
            {
                content: "Only the periods applying to everyone remain",
                trigger:
                    ".o_list_view:not(:has(.o_data_row:contains(Tour Personal Leave)))",
                extra_trigger: ".o_searchview_facet",
                run: function () {
                    // Assertion only.
                },
            },
            // ── Flow 5 — Click a period to open its read-only form.
            {
                content: "Open the public holiday period",
                trigger: ".o_data_row:contains(Tour Public Holiday) .o_data_cell:first",
                extra_trigger: ".o_list_view",
            },
            // ── Post-Condition — The form is displayed and cannot be edited.
            {
                content: "The period form is read-only",
                trigger: ".o_form_view.o_form_readonly",
                extra_trigger:
                    ".o_field_widget[name='display_name']:contains(Tour Public Holiday)",
                run: function () {
                    // Assertion only.
                },
            },
        ]
    );
});
