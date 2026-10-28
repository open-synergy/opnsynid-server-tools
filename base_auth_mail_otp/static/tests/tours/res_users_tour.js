/* Copyright 2026 OpenSynergy Indonesia
   Copyright 2026 PT. Simetri Sinergi Indonesia
   License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define("base_auth_mail_otp.res_users_tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    // IK: docs/res_users/01-configure-policy.md
    tour.register(
        "base_auth_mail_otp_res_users_configure_policy",
        {
            test: true,
            url: "/web",
        },
        [
            // Flow 1 - Open the Settings > General Settings menu
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Settings app",
                trigger: '.o_app[data-menu-xmlid="base.menu_administration"]',
            },
            {
                content: "Open the General Settings menu",
                trigger: '.o_menu_sections [data-menu-xmlid="base_setup.menu_config"]',
            },

            // Flow 2 - Click the Email OTP tab
            {
                content: "Click the Email OTP tab",
                trigger: ".settings_tab .tab[data-key='base_auth_mail_otp']",
                extra_trigger: ".o_base_settings",
            },

            // Flow 3 - Select the policy
            {
                content: "Select the Internal users only policy",
                trigger: "select.o_field_widget[name='mail_otp_policy']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text Internal users only",
            },

            // Flow 4 - Fill in the limits
            {
                content: "Fill in the code validity",
                trigger: ".o_field_widget[name='mail_otp_code_validity']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text 15",
            },

            // Flow 5 - Fill in the trusted device validity
            {
                content: "Fill in the trusted device validity",
                trigger: ".o_field_widget[name='mail_otp_trusted_device_days']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text 7",
            },

            // Flow 6 - Click Save
            {
                content: "Click Save",
                trigger: "button[name='execute']",
                extra_trigger: ".o_form_view.o_form_editable",
                run: function (actions) {
                    // Mark the Settings renderer node that Save rebuilds, in
                    // the same run as the click (atomic). A rebuilt node has
                    // no marker, whether Save re-renders in place or reloads
                    // the whole page.
                    $(".o_base_settings .settings_tab").addClass("oe_tour_stale");
                    actions.click(this.$anchor);
                },
            },
            {
                content: "Wait for the Settings page to be rebuilt",
                trigger:
                    ".o_base_settings .settings_tab:not(.oe_tour_stale) " +
                    ".tab[data-key='base_auth_mail_otp']",
                run: function () {
                    // Waiting only; do not trigger the default click action.
                },
            },

            // Post-Condition - the Email OTP settings are shown again
            {
                content: "Click the Email OTP tab again",
                trigger: ".settings_tab .tab[data-key='base_auth_mail_otp']",
                extra_trigger: ".o_base_settings",
            },
            {
                content: "The Email OTP settings are displayed",
                trigger: "select.o_field_widget[name='mail_otp_policy']",
                extra_trigger: ".app_settings_block[data-key='base_auth_mail_otp']",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );

    // IK: docs/res_users/02-exempt-user.md
    tour.register(
        "base_auth_mail_otp_res_users_exempt_user",
        {
            test: true,
            url: "/web",
        },
        [
            // Flow 1 - Open the Settings > Users & Companies > Users menu
            tour.stepUtils.showAppsMenuItem(),
            {
                content: "Open the Settings app",
                trigger: '.o_app[data-menu-xmlid="base.menu_administration"]',
            },
            {
                content: "Open the Users & Companies menu",
                trigger: '.o_menu_sections [data-menu-xmlid="base.menu_users"]',
            },
            {
                content: "Open the Users menu",
                trigger:
                    '.o_menu_sections [data-menu-xmlid="base.menu_action_res_users"]',
            },
            {
                content: "The Users list is displayed",
                trigger: ".o_control_panel .breadcrumb-item.active:contains(Users)",
                extra_trigger: ".o_list_view",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 2 - Find and open the user to exempt
            {
                content: "Open the user to exempt",
                trigger: ".o_list_view .o_data_row:contains('Otp Exempt Tour User')",
                extra_trigger: ".o_list_view",
            },
            {
                content: "Click the Edit button",
                trigger: ".o_form_button_edit:enabled",
                extra_trigger: ".o_form_view",
            },

            // Flow 3 - Click the Email OTP tab
            {
                content: "Click the Email OTP tab",
                trigger: ".o_notebook .nav-link:contains('Email OTP')",
                extra_trigger: ".o_form_view.o_form_editable",
            },

            // Flow 4 - Tick Exempt from Email OTP
            {
                content: "Tick Exempt from Email OTP",
                trigger: ".o_field_widget[name='mail_otp_exempt'] input",
                extra_trigger: ".o_form_view.o_form_editable",
            },

            // Flow 5 - Fill in Exempt Until
            {
                content: "Fill in Exempt Until",
                trigger: ".o_field_widget[name='mail_otp_exempt_until'] input",
                extra_trigger: ".o_form_view.o_form_editable",
                run: "text 12/31/2099 10:00:00",
            },

            // Flow 6 - Click Save
            {
                content: "Click Save",
                trigger: ".o_form_button_save",
                extra_trigger: ".o_form_view.o_form_editable",
            },

            // Post-Condition - the exemption is saved
            {
                content: "The user form is saved",
                trigger: ".o_form_view.o_form_readonly",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );

    // IK: docs/res_users/03-login-email-code.md
    // The optional Flow 7 (Send a new code) is a recovery path and is
    // covered by the controller HTTP tests, not by this tour.
    tour.register(
        "base_auth_mail_otp_res_users_login_email_code",
        {
            test: true,
            url: "/web/login",
        },
        [
            // Flow 1 - Open the login page
            {
                content: "The login page is displayed",
                trigger: "input#login",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 2 - Fill in Email and Password, click Log in
            {
                content: "Fill in the login",
                trigger: "input#login",
                run: "text otp_tour_user",
            },
            {
                content: "Fill in the password",
                trigger: "input#password",
                run: "text Otp#Tour-4nHy!Pc8",
            },
            {
                content: "Click Log in",
                trigger: "button:contains('Log in')",
            },

            // Flow 3 - The Email Verification page is displayed
            {
                content: "The Email Verification page is displayed",
                trigger: "label:contains('Verification Code')",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },

            // Flow 4 - Type the code
            {
                content: "Type the code",
                trigger: "input#mail_otp_code",
                run: "text 123456",
            },

            // Flow 5 - Tick Trust this device
            {
                content: "Tick Trust this device",
                trigger: "label[for='mail_otp_remember']",
            },

            // Flow 6 - Click Verify
            {
                content: "Click Verify",
                trigger: "button.o_mail_otp_verify",
            },

            // Post-Condition - the Odoo home page opens
            {
                content: "The user is logged in",
                trigger: ".o_user_menu .oe_topbar_name",
                run: function () {
                    // Assertion only; do not trigger the default click action.
                },
            },
        ]
    );
});
