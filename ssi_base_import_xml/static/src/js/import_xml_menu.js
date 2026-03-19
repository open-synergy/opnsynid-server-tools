odoo.define("ssi_base_import_xml.ImportXmlButton", function (require) {
    "use strict";

    const ControlPanel = require("web.ControlPanel");

    const {Component, hooks} = owl;
    const {useRef} = hooks;

    class ImportXmlButton extends Component {
        _onImportXmlClick() {
            alert("Import XML button clicked!");
        }
    }
    ImportXmlButton.template = "ssi_base_import_xml.Button";

    // Patch control panel to initialize import xml component
    ControlPanel.components = Object.assign({}, ControlPanel.components, {
        ImportXmlButton,
    });
    ControlPanel.patch("ssi_base_import_xml.ControlPanel", (T) => {
        class ControlPanelImportXml extends T {
            constructor() {
                super(...arguments);
                if ("cp_content" in this.props) {
                    const content = this.props.cp_content || {};
                    if ("$importXml" in content) {
                        this.additionalContent.importXml = content.$importXml;
                    }
                }

                this.contentRefs.importXml = useRef("importXml");
            }
        }
        return ControlPanelImportXml;
    });

    return ImportXmlButton;
});
