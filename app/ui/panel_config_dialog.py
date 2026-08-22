from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QGroupBox,
)
from PySide6.QtCore import Qt

from app.ui.panel_configuration_copy_dialog import (
    PanelConfigurationCopyDialog
)


class PanelConfigDialog(QDialog):

    def __init__(
        self,
        node,
        projects_dir=None,
        target_project_folder=None,
        parent=None
    ):

        super().__init__(parent)

        self.node = node

        self.projects_dir = (
            projects_dir
        )

        self.target_project_folder = (
            target_project_folder
        )

        self.copied_configuration = None

        # =====================================================
        # WINDOW
        # =====================================================

        self.setWindowTitle(
            "Panel Configuration"
        )

        self.setModal(True)

        self.resize(
            620,
            620
        )

        # =====================================================
        # MAIN LAYOUT
        # =====================================================

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            24,
            20,
            24,
            20
        )

        layout.setSpacing(
            14
        )

        # =====================================================
        # TITLE
        # =====================================================

        title = QLabel(
            "PANEL CONFIGURATION"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 26px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Configure the equipment connected to this panel "
            "and the number of test components to be created."
        )

        description.setWordWrap(
            True
        )

        description.setStyleSheet(
            """
            QLabel {
                color: #9ca3af;
                font-size: 13px;
            }
            """
        )

        layout.addWidget(
            description
        )

        # =====================================================
        # PANEL GROUP
        # =====================================================

        panel_group = QGroupBox(
            "Panel"
        )

        panel_form = QFormLayout(
            panel_group
        )

        panel_form.setContentsMargins(
            20,
            20,
            20,
            20
        )

        panel_form.setSpacing(
            12
        )

        self.panel_name = QLineEdit()

        self.panel_name.setText(
            str(
                getattr(
                    node,
                    "name",
                    ""
                ) or ""
            )
        )

        # Panel name is the identity of the current panel.
        # It should not be modified from this dialog.
        self.panel_name.setReadOnly(
            True
        )

        panel_form.addRow(
            "Panel:",
            self.panel_name
        )

        layout.addWidget(
            panel_group
        )

        # =====================================================
        # FEED EQUIPMENT
        # =====================================================

        equipment_group = QGroupBox(
            "Feed Equipment"
        )

        equipment_form = QFormLayout(
            equipment_group
        )

        equipment_form.setContentsMargins(
            20,
            20,
            20,
            20
        )

        equipment_form.setSpacing(
            12
        )

        # -----------------------------------------------------
        # EQUIPMENT NAME
        # -----------------------------------------------------

        self.equipment_name = QLineEdit()

        self.equipment_name.setPlaceholderText(
            "Example: 110kV Transformer / Motor / Feeder"
        )

        self.equipment_name.setText(
            str(
                getattr(
                    node,
                    "equipment_name",
                    ""
                ) or ""
            )
        )

        equipment_form.addRow(
            "Equipment Name:",
            self.equipment_name
        )

        # -----------------------------------------------------
        # EQUIPMENT TYPE
        # -----------------------------------------------------

        self.equipment_type = QLineEdit()

        self.equipment_type.setPlaceholderText(
            "Example: Transformer / Motor / Feeder"
        )

        self.equipment_type.setText(
            str(
                getattr(
                    node,
                    "equipment_type",
                    ""
                ) or ""
            )
        )

        equipment_form.addRow(
            "Equipment Type:",
            self.equipment_type
        )

        layout.addWidget(
            equipment_group
        )

        # =====================================================
        # TEST COMPONENTS
        # =====================================================

        component_group = QGroupBox(
            "Test Components"
        )

        component_form = QFormLayout(
            component_group
        )

        component_form.setContentsMargins(
            20,
            20,
            20,
            20
        )

        component_form.setSpacing(
            12
        )

        # -----------------------------------------------------
        # CT COUNT
        # -----------------------------------------------------

        self.ct_count = QSpinBox()

        self.ct_count.setRange(
            0,
            100
        )

        self.ct_count.setValue(
            self._get_int_value(
                node,
                "ct_count",
                0
            )
        )

        component_form.addRow(
            "Number of CTs:",
            self.ct_count
        )

        # -----------------------------------------------------
        # NUMERICAL RELAY COUNT
        # -----------------------------------------------------

        self.relay_count = QSpinBox()

        self.relay_count.setRange(
            0,
            100
        )

        self.relay_count.setValue(
            self._get_int_value(
                node,
                "relay_count",
                0
            )
        )

        component_form.addRow(
            "Numerical Relays:",
            self.relay_count
        )

        # -----------------------------------------------------
        # AUXILIARY RELAY COUNT
        # -----------------------------------------------------

        self.aux_count = QSpinBox()

        self.aux_count.setRange(
            0,
            100
        )

        self.aux_count.setValue(
            self._get_int_value(
                node,
                "aux_count",
                0
            )
        )

        component_form.addRow(
            "Auxiliary Relays:",
            self.aux_count
        )

        # -----------------------------------------------------
        # METER COUNT
        # -----------------------------------------------------

        self.meter_count = QSpinBox()

        self.meter_count.setRange(
            0,
            100
        )

        self.meter_count.setValue(
            self._get_int_value(
                node,
                "meter_count",
                0
            )
        )

        component_form.addRow(
            "Meters:",
            self.meter_count
        )

        layout.addWidget(
            component_group
        )

        # =====================================================
        # INFORMATION
        # =====================================================

        info = QLabel(
            "Changing the component counts creates or removes "
            "the corresponding test components. Existing "
            "component configurations are preserved where possible."
        )

        info.setWordWrap(
            True
        )

        info.setStyleSheet(
            """
            QLabel {
                color: #9ca3af;
                font-size: 12px;
            }
            """
        )

        layout.addWidget(
            info
        )

        # =====================================================
        # BUTTONS
        # =====================================================

        buttons = QHBoxLayout()

        buttons.setSpacing(
            10
        )

        # -----------------------------------------------------
        # IMPORT CONFIGURATION
        # -----------------------------------------------------

        self.copy_button = QPushButton(
            "Import from Existing Panel"
        )

        self.copy_button.setMinimumHeight(
            42
        )

        self.copy_button.setToolTip(
            "Copy configuration and selected component "
            "parameters from another panel."
        )

        self.copy_button.clicked.connect(
            self.copy_from_existing_panel
        )

        # -----------------------------------------------------
        # CANCEL
        # -----------------------------------------------------

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.cancel_button.setMinimumHeight(
            42
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        # -----------------------------------------------------
        # SAVE
        # -----------------------------------------------------

        self.save_button = QPushButton(
            "Save Configuration"
        )

        self.save_button.setMinimumHeight(
            42
        )

        self.save_button.clicked.connect(
            self.accept
        )

        # -----------------------------------------------------
        # LAYOUT
        # -----------------------------------------------------

        buttons.addWidget(
            self.copy_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.cancel_button
        )

        buttons.addWidget(
            self.save_button
        )

        layout.addLayout(
            buttons
        )

    # =========================================================
    # INTEGER VALUE
    # =========================================================

    @staticmethod
    def _get_int_value(
        node,
        attribute,
        default=0
    ):

        value = getattr(
            node,
            attribute,
            default
        )

        try:

            return int(
                value or default
            )

        except (
            TypeError,
            ValueError
        ):

            return default

    # =========================================================
    # IMPORT FROM EXISTING PANEL
    # =========================================================

    def copy_from_existing_panel(self):

        # -----------------------------------------------------
        # PROJECT DIRECTORY CHECK
        # -----------------------------------------------------

        if self.projects_dir is None:

            QMessageBox.warning(
                self,
                "Import Configuration",
                "Project directory is not available."
            )

            return

        # -----------------------------------------------------
        # OPEN PANEL SELECTION DIALOG
        # -----------------------------------------------------

        dialog = PanelConfigurationCopyDialog(

            projects_dir=self.projects_dir,

            target_project_folder=(
                self.target_project_folder
            ),

            target_panel_id=getattr(
                self.node,
                "node_id",
                None
            ),

            parent=self
        )

        # -----------------------------------------------------
        # USER CANCELLED
        # -----------------------------------------------------

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        # -----------------------------------------------------
        # GET CONFIGURATION
        # -----------------------------------------------------

        configuration = (
            dialog.get_configuration()
        )

        if not configuration:

            return

        self.copied_configuration = (
            configuration
        )

        # =====================================================
        # PANEL CONFIGURATION
        # =====================================================

        panel_config = (
            configuration.get(
                "panel_configuration",
                {}
            )
        )

        # -----------------------------------------------------
        # EQUIPMENT NAME
        # -----------------------------------------------------

        if (
            "equipment_name"
            in panel_config
        ):

            self.equipment_name.setText(
                str(
                    panel_config[
                        "equipment_name"
                    ] or ""
                )
            )

        # -----------------------------------------------------
        # EQUIPMENT TYPE
        # -----------------------------------------------------

        if (
            "equipment_type"
            in panel_config
        ):

            self.equipment_type.setText(
                str(
                    panel_config[
                        "equipment_type"
                    ] or ""
                )
            )

        # -----------------------------------------------------
        # CT COUNT
        # -----------------------------------------------------

        if (
            "ct_count"
            in panel_config
        ):

            self.ct_count.setValue(
                self._safe_int(
                    panel_config[
                        "ct_count"
                    ]
                )
            )

        # -----------------------------------------------------
        # RELAY COUNT
        # -----------------------------------------------------

        if (
            "relay_count"
            in panel_config
        ):

            self.relay_count.setValue(
                self._safe_int(
                    panel_config[
                        "relay_count"
                    ]
                )
            )

        # -----------------------------------------------------
        # AUXILIARY RELAY COUNT
        # -----------------------------------------------------

        if (
            "aux_count"
            in panel_config
        ):

            self.aux_count.setValue(
                self._safe_int(
                    panel_config[
                        "aux_count"
                    ]
                )
            )

        # -----------------------------------------------------
        # METER COUNT
        # -----------------------------------------------------

        if (
            "meter_count"
            in panel_config
        ):

            self.meter_count.setValue(
                self._safe_int(
                    panel_config[
                        "meter_count"
                    ]
                )
            )

        # =====================================================
        # UPDATE WINDOW TITLE / STATUS
        # =====================================================

        source_name = (
            configuration.get(
                "source_panel_name",
                ""
            )
        )

        if source_name:

            self.copy_button.setText(
                f"Imported from {source_name}"
            )

        else:

            self.copy_button.setText(
                "Configuration Imported"
            )

        # Keep the button usable for another import.
        self.copy_button.setToolTip(
            "Import configuration from another panel."
        )

    # =========================================================
    # SAFE INTEGER
    # =========================================================

    @staticmethod
    def _safe_int(
        value,
        default=0
    ):

        try:

            return int(
                value or default
            )

        except (
            TypeError,
            ValueError
        ):

            return default

    # =========================================================
    # GET CONFIGURATION
    # =========================================================

    def get_configuration(self):

        return {

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

    # =========================================================
    # GET COPIED CONFIGURATION
    # =========================================================

    def get_copied_configuration(self):

        return (
            self.copied_configuration
        )