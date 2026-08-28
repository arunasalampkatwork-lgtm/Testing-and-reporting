
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox, QPushButton,
    QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QGroupBox,
    QAbstractSpinBox
)

from app.ui.panel_configuration_copy_dialog import (
    PanelConfigurationCopyDialog
)
from app.services.component_manager import ComponentManager


class PanelConfigDialog(QDialog):

    COMPONENT_FIELDS = (
        "manufacturer",
        "model",
        "description",
        "ct_primary",
        "ct_secondary",
        "ct_ratio",
        "ct_class",
        "burden",
        "core",
        "vt_ratio",
        "firmware",
        "coil_voltage",
        "contact_configuration",
        "meter_type",
        "meter_functions",
        "accuracy_class",
        "protection_functions",
    )

    def __init__(
        self,
        node,
        projects_dir=None,
        target_project_folder=None,
        parent=None
    ):
        super().__init__(parent)

        self.node = node
        self.projects_dir = projects_dir
        self.target_project_folder = target_project_folder
        self.copied_configuration = None

        self.setWindowTitle("Panel Configuration")
        self.resize(620, 620)
        self.setMinimumSize(560, 500)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("PANEL CONFIGURATION")
        title.setStyleSheet(
            "font-size:24px;font-weight:bold;"
        )
        layout.addWidget(title)

        info = QLabel(
            "Configure the panel and the number of test components."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        panel_group = QGroupBox("Panel")
        panel_form = QFormLayout(panel_group)

        self.panel_name = QLineEdit(
            str(getattr(self.node, "name", "") or "")
        )
        self.panel_name.setReadOnly(True)
        panel_form.addRow("Panel:", self.panel_name)

        layout.addWidget(panel_group)

        equipment_group = QGroupBox("Feed Equipment")
        equipment_form = QFormLayout(equipment_group)

        self.equipment_name = QLineEdit(
            str(getattr(self.node, "equipment_name", "") or "")
        )
        self.equipment_type = QLineEdit(
            str(getattr(self.node, "equipment_type", "") or "")
        )

        equipment_form.addRow(
            "Equipment Name:",
            self.equipment_name
        )
        equipment_form.addRow(
            "Equipment Type:",
            self.equipment_type
        )

        layout.addWidget(equipment_group)

        component_group = QGroupBox("Test Components")
        component_form = QFormLayout(component_group)

        self.ct_count = self._spin("ct_count", 100)
        self.relay_count = self._spin("relay_count", 100)
        self.aux_count = self._spin("aux_count", 100)
        self.meter_count = self._spin("meter_count", 100)

        component_form.addRow("Number of CTs:", self.ct_count)
        component_form.addRow(
            "Number of Numerical Relays:",
            self.relay_count
        )
        component_form.addRow(
            "Number of Auxiliary Relays:",
            self.aux_count
        )
        component_form.addRow(
            "Number of Meters:",
            self.meter_count
        )

        layout.addWidget(component_group)

        layout.addStretch()

        buttons = QHBoxLayout()

        self.copy_button = QPushButton(
            "Import from Existing Panel"
        )
        self.copy_button.clicked.connect(
            self.copy_from_existing_panel
        )

        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)

        save = QPushButton("Save Configuration")
        save.clicked.connect(self.accept)

        buttons.addWidget(self.copy_button)
        buttons.addStretch()
        buttons.addWidget(cancel)
        buttons.addWidget(save)

        layout.addLayout(buttons)

    def _spin(self, attr, maximum):
        box = QSpinBox()
        box.setRange(0, maximum)
        box.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.UpDownArrows
        )
        box.setValue(
            self._get_int(
                getattr(self.node, attr, 0)
            )
        )
        return box

    @staticmethod
    def _get_int(value):
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    def copy_from_existing_panel(self):
        if self.projects_dir is None:
            QMessageBox.warning(
                self,
                "Import Configuration",
                "Project directory is not available."
            )
            return

        dialog = PanelConfigurationCopyDialog(
            projects_dir=self.projects_dir,
            target_project_folder=self.target_project_folder,
            target_panel_id=getattr(
                self.node,
                "node_id",
                None
            ),
            parent=self
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        config = dialog.get_configuration()
        self.copied_configuration = config

        panel = config.get(
            "panel_configuration",
            {}
        )

        if "equipment_name" in panel:
            self.equipment_name.setText(
                str(panel["equipment_name"] or "")
            )

        if "equipment_type" in panel:
            self.equipment_type.setText(
                str(panel["equipment_type"] or "")
            )

        if "ct_count" in panel:
            self.ct_count.setValue(
                self._get_int(panel["ct_count"])
            )

        if "relay_count" in panel:
            self.relay_count.setValue(
                self._get_int(panel["relay_count"])
            )

        if "aux_count" in panel:
            self.aux_count.setValue(
                self._get_int(panel["aux_count"])
            )

        if "meter_count" in panel:
            self.meter_count.setValue(
                self._get_int(panel["meter_count"])
            )

        components = config.get(
            "component_configuration",
            config.get("components", [])
        )

        self.copy_button.setText(
            f"Imported: {len(components)} components"
        )

        self.copy_button.setToolTip(
            "Component configuration is stored and will be "
            "applied when the panel configuration is saved."
        )

    def get_configuration(self):
        result = {
            "panel_name":
                self.panel_name.text().strip(),
            "equipment_name":
                self.equipment_name.text().strip(),
            "equipment_type":
                self.equipment_type.text().strip(),
            "ct_count":
                self.ct_count.value(),
            "relay_count":
                self.relay_count.value(),
            "aux_count":
                self.aux_count.value(),
            "meter_count":
                self.meter_count.value(),
        }

        if self.copied_configuration:
            result["_imported_components"] = list(
                self.copied_configuration.get(
                    "component_configuration",
                    self.copied_configuration.get(
                        "components",
                        []
                    )
                )
                or []
            )

            result["_import_source_project_folder"] = (
                self.copied_configuration.get(
                    "source_project_folder"
                )
            )

        return result

    def get_copied_configuration(self):
        return self.copied_configuration
