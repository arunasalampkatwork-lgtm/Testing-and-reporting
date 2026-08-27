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
    QAbstractSpinBox,
)

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

        self.projects_dir = projects_dir

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

        self.setMinimumSize(
            560,
            500
        )

        self._apply_style()

        self._build_ui()

    # =========================================================
    # STYLE
    # =========================================================

    def _apply_style(self):

        self.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3a3f46;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 14px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }

            QLineEdit,
            QSpinBox {
                min-height: 38px;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding-left: 8px;
                padding-right: 8px;
            }

            QLineEdit:focus,
            QSpinBox:focus {
                border: 1px solid #60a5fa;
            }

            QSpinBox::up-button,
            QSpinBox::down-button {
                width: 30px;
                min-width: 30px;
                border: none;
            }

            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
            }

            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
            }

            QPushButton {
                min-height: 40px;
                padding-left: 14px;
                padding-right: 14px;
                border-radius: 6px;
            }

            QPushButton:hover {
                border: 1px solid #60a5fa;
            }
            """
        )

    # =========================================================
    # BUILD UI
    # =========================================================

    def _build_ui(self):

        layout = QVBoxLayout(
            self
        )

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
                font-size: 24px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Configure the equipment connected to this panel "
            "and the number of test components."
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
        # PANEL
        # =====================================================

        panel_group = QGroupBox(
            "Panel"
        )

        panel_form = QFormLayout(
            panel_group
        )

        panel_form.setContentsMargins(
            18,
            20,
            18,
            18
        )

        panel_form.setSpacing(
            10
        )

        self.panel_name = QLineEdit()

        self.panel_name.setText(
            str(
                getattr(
                    self.node,
                    "name",
                    ""
                ) or ""
            )
        )

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
        # EQUIPMENT
        # =====================================================

        equipment_group = QGroupBox(
            "Feed Equipment"
        )

        equipment_form = QFormLayout(
            equipment_group
        )

        equipment_form.setContentsMargins(
            18,
            20,
            18,
            18
        )

        equipment_form.setSpacing(
            10
        )

        self.equipment_name = QLineEdit()

        self.equipment_name.setText(
            str(
                getattr(
                    self.node,
                    "equipment_name",
                    ""
                ) or ""
            )
        )

        self.equipment_name.setPlaceholderText(
            "Example: Motor M-101"
        )

        equipment_form.addRow(
            "Equipment Name:",
            self.equipment_name
        )

        self.equipment_type = QLineEdit()

        self.equipment_type.setText(
            str(
                getattr(
                    self.node,
                    "equipment_type",
                    ""
                ) or ""
            )
        )

        self.equipment_type.setPlaceholderText(
            "Example: Motor / Transformer / Feeder"
        )

        equipment_form.addRow(
            "Equipment Type:",
            self.equipment_type
        )

        layout.addWidget(
            equipment_group
        )

        # =====================================================
        # COMPONENT COUNTS
        # =====================================================

        component_group = QGroupBox(
            "Test Components"
        )

        component_form = QFormLayout(
            component_group
        )

        component_form.setContentsMargins(
            18,
            20,
            18,
            18
        )

        component_form.setSpacing(
            10
        )

        # -----------------------------------------------------
        # CT
        # -----------------------------------------------------

        self.ct_count = self._create_spinbox(
            "ct_count"
        )

        component_form.addRow(
            "Number of CTs:",
            self.ct_count
        )

        # -----------------------------------------------------
        # RELAYS
        # -----------------------------------------------------

        self.relay_count = self._create_spinbox(
            "relay_count"
        )

        component_form.addRow(
            "Numerical Relays:",
            self.relay_count
        )

        # -----------------------------------------------------
        # AUX RELAYS
        # -----------------------------------------------------

        self.aux_count = self._create_spinbox(
            "aux_count"
        )

        component_form.addRow(
            "Auxiliary Relays:",
            self.aux_count
        )

        # -----------------------------------------------------
        # METERS
        # -----------------------------------------------------

        self.meter_count = self._create_spinbox(
            "meter_count"
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
            "Use 'Import from Existing Panel' to copy the "
            "configuration and selected component parameters "
            "from another panel."
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

        layout.addStretch()

        # =====================================================
        # BUTTONS
        # =====================================================

        buttons = QHBoxLayout()

        self.copy_button = QPushButton(
            "Import from Existing Panel"
        )

        self.copy_button.setMinimumHeight(
            42
        )

        self.copy_button.clicked.connect(
            self.copy_from_existing_panel
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.cancel_button.setMinimumHeight(
            42
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        self.save_button = QPushButton(
            "Save Configuration"
        )

        self.save_button.setMinimumHeight(
            42
        )

        self.save_button.clicked.connect(
            self.accept
        )

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
    # CREATE SPINBOX
    # =========================================================

    def _create_spinbox(
        self,
        attribute
    ):

        spinbox = QSpinBox()

        spinbox.setRange(
            0,
            100
        )

        spinbox.setButtonSymbols(
            QAbstractSpinBox.ButtonSymbols.UpDownArrows
        )

        spinbox.setMinimumHeight(
            40
        )

        spinbox.setEnabled(
            True
        )

        spinbox.setReadOnly(
            False
        )

        spinbox.setKeyboardTracking(
            True
        )

        spinbox.setValue(
            self._get_int_value(
                self.node,
                attribute,
                0
            )
        )

        return spinbox

    # =========================================================
    # INTEGER
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
    # IMPORT
    # =========================================================

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

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

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
        # IMPORT STATUS
        # =====================================================

        source_name = str(
            configuration.get(
                "source_panel_name",
                ""
            ) or ""
        )

        component_count = len(
            configuration.get(
                "components",
                []
            )
        )

        if source_name:

            self.copy_button.setText(
                f"Imported from {source_name}"
            )

            self.copy_button.setToolTip(
                f"{component_count} component "
                f"configurations imported."
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