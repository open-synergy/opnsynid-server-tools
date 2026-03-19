odoo.define("ssi_base_import_xml.ImportXmlButton", function (require) {
    "use strict";

    const core = require("web.core");
    const session = require("web.session");

    // Require ControlPanel to ensure it is loaded first so the qweb
    // template extension (which injects the button into ControlPanel) is applied.
    require("web.ControlPanel");

    // Use native addEventListener with capture=true on document.
    // Capture phase fires BEFORE bubble phase, so OWL's stopPropagation
    // in developer mode cannot block this handler.
    document.addEventListener(
        "click",
        function (ev) {
            if (!ev.target || !ev.target.closest(".o_button_import_xml")) {
                return;
            }
            if (!session.is_admin) {
                return;
            }
            ev.stopPropagation();

            // Get the active model name from the URL hash
            // e.g. #action=203&model=res.partner&view_type=list
            var hash = window.location.hash.slice(1);
            var params = new URLSearchParams(hash);
            var modelName = params.get("model") || "";

            // Trigger the wizard via core.bus which is handled by AbstractWebClient
            core.bus.trigger("do-action", {
                action: {
                    type: "ir.actions.act_window",
                    name: "Import from XML",
                    res_model: "base_import_xml",
                    view_mode: "form",
                    views: [[false, "form"]],
                    target: "new",
                    context: {default_model_name: modelName},
                },
            });
        },
        true
    );
});
