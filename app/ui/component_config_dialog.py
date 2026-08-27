from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QGroupBox,
)


class ComponentConfigDialog(QDialog):

    METER_TYPES = [
        "Ammeter",
        "Voltmeter",
        "Multifunction Meter",
    ]

    METER_FUNCTIONS = {

        "Ammeter": [
            "CURRENT"
        ],

        "Voltmeter": [
            "VOLTAGE"
        ],

        "Multifunction Meter": [
            "VOLTAGE",
            "CURRENT",
            "FREQUENCY",
            "ACTIVE_POWER",
            "REACTIVE_POWER",
            "APPARENT_POWER",
            "POWER_FACTOR",
        ],
    }

    FUNCTION_LABELS = {

        "VOLTAGE":
            "Voltage",

        "CURRENT":
            "Current",

        "FREQUENCY":
            "Frequency",

        "ACTIVE_POWER":
            "Active Power",

        "REACTIVE_POWER":
            "Reactive Power",

        "APPARENT_POWER":
            "Apparent Power",

        "POWER_FACTOR":
            "Power Factor",
    }

    def __init__(
        self,
        component,
        parent=None,
    ):

        super().__init__(
            parent
        )

        self.component = component

        self.component_type = str(
            getattr(
                component,
                "component_type",
                ""
            )
        ).strip().upper()

        self.setWindowTitle(
            f"Edit Component - "
            f"{getattr(component, 'name', 'Component')}"
        )

        self.setModal(
            True
        )

        self.resize(
            600,
            720
        )

        self.build_ui()

        self.populate_existing_values()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            18,
            18,
            18,
            18
        )

        layout.setSpacing(
            12
        )

        # =================================================
        # HEADER
        # =================================================

        header = QLabel(
            "COMPONENT CONFIGURATION"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: 700;
                padding: 4px 0px;
            }
            """
        )

        layout.addWidget(
            header
        )

        # =================================================
        # GENERAL
        # =================================================

        general_group = QGroupBox(
            "General Information"
        )

        general_form = QFormLayout(
            general_group
        )

        general_form.setSpacing(
            9
        )

        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        self.name_edit = QLineEdit()

        self.name_edit.setReadOnly(
            True
        )

        general_form.addRow(
            "Component:",
            self.name_edit
        )

        # -------------------------------------------------
        # MANUFACTURER
        # -------------------------------------------------

        self.manufacturer_edit = QLineEdit()

        general_form.addRow(
            "Manufacturer:",
            self.manufacturer_edit
        )

        # -------------------------------------------------
        # MODEL
        # -------------------------------------------------

        self.model_edit = QLineEdit()

        general_form.addRow(
            "Model:",
            self.model_edit
        )

        # -------------------------------------------------
        # SERIAL
        # -------------------------------------------------

        self.serial_number_edit = QLineEdit()

        general_form.addRow(
            "Serial Number:",
            self.serial_number_edit
        )

        # -------------------------------------------------
        # DESCRIPTION
        # -------------------------------------------------

        self.description_edit = QLineEdit()

        general_form.addRow(
            "Description:",
            self.description_edit
        )

        layout.addWidget(
            general_group
        )

        # =================================================
        # CT
        # =================================================

        self.ct_primary_edit = QLineEdit()

        self.ct_primary_edit.setPlaceholderText(
            "Example: 1000"
        )

        self.ct_secondary_edit = QLineEdit()

        self.ct_secondary_edit.setPlaceholderText(
            "Example: 5"
        )

        self.ct_ratio_edit = QLineEdit()

        self.ct_ratio_edit.setReadOnly(
            True
        )

        self.ct_ratio_edit.setPlaceholderText(
            "Automatically calculated"
        )

        self.ct_class_edit = QLineEdit()

        self.burden_edit = QLineEdit()

        self.core_edit = QLineEdit()

        if self.component_type in (
            "CT",
            "CURRENT TRANSFORMER",
        ):

            ct_group = QGroupBox(
                "Current Transformer"
            )

            ct_form = QFormLayout(
                ct_group
            )

            ct_form.setSpacing(
                9
            )

            ct_form.addRow(
                "CT Primary (A):",
                self.ct_primary_edit
            )

            ct_form.addRow(
                "CT Secondary (A):",
                self.ct_secondary_edit
            )

            ct_form.addRow(
                "CT Ratio:",
                self.ct_ratio_edit
            )

            ct_form.addRow(
                "CT Class:",
                self.ct_class_edit
            )

            ct_form.addRow(
                "Burden:",
                self.burden_edit
            )

            ct_form.addRow(
                "Core:",
                self.core_edit
            )

            layout.addWidget(
                ct_group
            )

            self.ct_primary_edit.textChanged.connect(
                self.update_ct_ratio
            )

            self.ct_secondary_edit.textChanged.connect(
                self.update_ct_ratio
            )

        # =================================================
        # NUMERICAL RELAY
        # =================================================

        self.vt_ratio_edit = QLineEdit()

        self.firmware_edit = QLineEdit()

        if self.component_type == "NUMERICAL_RELAY":

            relay_group = QGroupBox(
                "Numerical Relay"
            )

            relay_form = QFormLayout(
                relay_group
            )

            relay_form.setSpacing(
                9
            )

            relay_form.addRow(
                "VT Ratio:",
                self.vt_ratio_edit
            )

            relay_form.addRow(
                "Firmware:",
                self.firmware_edit
            )

            layout.addWidget(
                relay_group
            )

        # =================================================
        # AUXILIARY RELAY
        # =================================================

        self.coil_voltage_edit = QLineEdit()

        self.contact_configuration_edit = (
            QLineEdit()
        )

        if self.component_type in (
            "AUXILIARY_RELAY",
            "AUX RELAY",
        ):

            aux_group = QGroupBox(
                "Auxiliary Relay"
            )

            aux_form = QFormLayout(
                aux_group
            )

            aux_form.setSpacing(
                9
            )

            aux_form.addRow(
                "Coil Voltage:",
                self.coil_voltage_edit
            )

            aux_form.addRow(
                "Contact Configuration:",
                self.contact_configuration_edit
            )

            layout.addWidget(
                aux_group
            )

        # =================================================
        # METER
        # =================================================

        self.meter_type_combo = QComboBox()

        self.meter_type_combo.addItem(
            "Select meter type",
            ""
        )

        for meter_type in self.METER_TYPES:

            self.meter_type_combo.addItem(
                meter_type,
                meter_type
            )

        self.accuracy_class_edit = QLineEdit()

        self.meter_function_list = QListWidget()

        self.meter_function_list.setMinimumHeight(
            150
        )

        self.meter_type_combo.currentIndexChanged.connect(
            self.update_meter_functions
        )

        if self.component_type == "METER":

            meter_group = QGroupBox(
                "Meter"
            )

            meter_layout = QFormLayout(
                meter_group
            )

            meter_layout.setSpacing(
                9
            )

            meter_layout.addRow(
                "Meter Type:",
                self.meter_type_combo
            )

            meter_layout.addRow(
                "Accuracy Class:",
                self.accuracy_class_edit
            )

            meter_layout.addRow(
                "Test Functions:",
                self.meter_function_list
            )

            layout.addWidget(
                meter_group
            )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        buttons.addStretch()

        cancel_button = QPushButton(
            "Cancel"
        )

        save_button = QPushButton(
            "Save Configuration"
        )

        save_button.setDefault(
            True
        )

        cancel_button.clicked.connect(
            self.reject
        )

        save_button.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            cancel_button
        )

        buttons.addWidget(
            save_button
        )

        layout.addLayout(
            buttons
        )

        # =================================================
        # STYLE
        # =================================================

        self.setStyleSheet(
            """
            QDialog {
                background-color: #242424;
            }

            QGroupBox {
                font-weight: 600;
                border: 1px solid #414141;
                border-radius: 7px;
                margin-top: 10px;
                padding: 12px;
                background-color: #292929;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0px 5px;
                color: #dddddd;
            }

            QLineEdit,
            QComboBox {
                min-height: 32px;
                padding: 4px 8px;
                border: 1px solid #444444;
                border-radius: 5px;
                background-color: #202020;
                color: #eeeeee;
            }

            QLineEdit:read-only {
                background-color: #303030;
                color: #aaaaaa;
            }

            QListWidget {
                background-color: #202020;
                border: 1px solid #444444;
                border-radius: 5px;
                padding: 4px;
            }

            QListWidget::item {
                padding: 7px;
                border-radius: 4px;
            }

            QListWidget::item:hover {
                background-color: #353535;
            }

            QPushButton {
                min-height: 36px;
                padding: 6px 14px;
                border-radius: 6px;
                border: 1px solid #444444;
                background-color: #333333;
                color: #eeeeee;
            }

            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #666666;
            }

            QPushButton:pressed {
                background-color: #252525;
            }
            """
        )

    # =====================================================
    # CT RATIO
    # =====================================================

    @staticmethod
    def _safe_float(
        value
    ):

        try:

            return float(
                str(
                    value
                ).strip()
            )

        except (
            TypeError,
            ValueError
        ):

            return None

    def update_ct_ratio(
        self
    ):

        if self.component_type not in (
            "CT",
            "CURRENT TRANSFORMER",
        ):

            return

        primary = self._safe_float(
            self.ct_primary_edit.text()
        )

        secondary = self._safe_float(
            self.ct_secondary_edit.text()
        )

        if (
            primary is not None
            and
            secondary is not None
            and
            primary > 0
            and
            secondary > 0
        ):

            self.ct_ratio_edit.setText(
                f"{primary:g}/{secondary:g}"
            )

        else:

            self.ct_ratio_edit.clear()

    # =====================================================
    # POPULATE EXISTING VALUES
    # =====================================================

    def populate_existing_values(
        self
    ):

        component = self.component

        # -------------------------------------------------
        # GENERAL
        # -------------------------------------------------

        self.name_edit.setText(
            str(
                getattr(
                    component,
                    "name",
                    ""
                )
                or ""
            )
        )

        self.manufacturer_edit.setText(
            str(
                getattr(
                    component,
                    "manufacturer",
                    ""
                )
                or ""
            )
        )

        self.model_edit.setText(
            str(
                getattr(
                    component,
                    "model",
                    ""
                )
                or ""
            )
        )

        self.serial_number_edit.setText(
            str(
                getattr(
                    component,
                    "serial_number",
                    ""
                )
                or ""
            )
        )

        self.description_edit.setText(
            str(
                getattr(
                    component,
                    "description",
                    ""
                )
                or ""
            )
        )

        # -------------------------------------------------
        # CT
        # -------------------------------------------------

        if self.component_type in (
            "CT",
            "CURRENT TRANSFORMER",
        ):

            self.ct_primary_edit.setText(
                self._display_value(
                    getattr(
                        component,
                        "ct_primary",
                        ""
                    )
                )
            )

            self.ct_secondary_edit.setText(
                self._display_value(
                    getattr(
                        component,
                        "ct_secondary",
                        ""
                    )
                )
            )

            self.ct_class_edit.setText(
                self._display_value(
                    getattr(
                        component,
                        "ct_class",
                        ""
                    )
                )
            )

            self.burden_edit.setText(
                self._display_value(
                    getattr(
                        component,
                        "burden",
                        ""
                    )
                )
            )

            self.core_edit.setText(
                self._display_value(
                    getattr(
                        component,
                        "core",
                        ""
                    )
                )
            )

            self.update_ct_ratio()

            # Legacy data compatibility.
            if not self.ct_ratio_edit.text():

                legacy_ratio = (
                    getattr(
                        component,
                        "ct_ratio",
                        ""
                    )
                    or ""
                )

                self.ct_ratio_edit.setText(
                    str(
                        legacy_ratio
                    ).strip()
                )

        # -------------------------------------------------
        # NUMERICAL RELAY
        # -------------------------------------------------

        if self.component_type == "NUMERICAL_RELAY":

            self.vt_ratio_edit.setText(
                self._display_value(
                    getattr(
                        component,
                        "vt_ratio",
                        ""
                    )
                )
            )

            self.firmware_edit.setText(
                self._display_value(
                    getattr(
                        component,
                        "firmware",
                        ""
                    )
                )
            )

        # -------------------------------------------------
        # AUXILIARY RELAY
        # -------------------------------------------------

        if self.component_type in (
            "AUXILIARY_RELAY",
            "AUX RELAY",
        ):

            self.coil_voltage_edit.setText(
                self._display_value(
                    getattr(
                        component,
                        "coil_voltage",
                        ""
                    )
                )
            )

            self.contact_configuration_edit.setText(
                self._display_value(
                    getattr(
                        component,
                        "contact_configuration",
                        ""
                    )
                )
            )

        # -------------------------------------------------
        # METER
        # -------------------------------------------------

        if self.component_type == "METER":

            existing_type = str(
                getattr(
                    component,
                    "meter_type",
                    ""
                )
                or ""
            ).strip()

            index = (
                self.meter_type_combo
                .findData(
                    existing_type
                )
            )

            if index >= 0:

                self.meter_type_combo.setCurrentIndex(
                    index
                )

            self.accuracy_class_edit.setText(
                self._display_value(
                    getattr(
                        component,
                        "accuracy_class",
                        ""
                    )
                )
            )

            self.update_meter_functions()

            existing_functions = set(
                getattr(
                    component,
                    "meter_functions",
                    []
                )
                or []
            )

            for row in range(
                self.meter_function_list.count()
            ):

                item = (
                    self.meter_function_list
                    .item(row)
                )

                code = item.data(
                    Qt.ItemDataRole.UserRole
                )

                item.setCheckState(
                    Qt.CheckState.Checked
                    if code in existing_functions
                    else Qt.CheckState.Unchecked
                )

    # =====================================================
    # DISPLAY VALUE
    # =====================================================

    @staticmethod
    def _display_value(
        value
    ):

        if value is None:
            return ""

        return str(
            value
        ).strip()

    # =====================================================
    # METER FUNCTIONS
    # =====================================================

    def update_meter_functions(
        self
    ):

        if self.component_type != "METER":

            return

        meter_type = (
            self.meter_type_combo
            .currentData()
        )

        functions = (
            self.METER_FUNCTIONS.get(
                meter_type,
                []
            )
        )

        existing = set(
            getattr(
                self.component,
                "meter_functions",
                []
            )
            or []
        )

        self.meter_function_list.clear()

        for code in functions:

            item = QListWidgetItem(
                self.FUNCTION_LABELS.get(
                    code,
                    code
                )
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                code
            )

            item.setFlags(
                item.flags()
                |
                Qt.ItemFlag.ItemIsUserCheckable
            )

            # Preserve existing selection.
            if code in existing:

                item.setCheckState(
                    Qt.CheckState.Checked
                )

            else:

                item.setCheckState(
                    Qt.CheckState.Unchecked
                )

            self.meter_function_list.addItem(
                item
            )

    # =====================================================
    # GET CONFIGURATION
    # =====================================================

    def get_configuration(
        self
    ):

        configuration = {

            "manufacturer":
                self.manufacturer_edit
                .text()
                .strip(),

            "model":
                self.model_edit
                .text()
                .strip(),

            "serial_number":
                self.serial_number_edit
                .text()
                .strip(),

            "description":
                self.description_edit
                .text()
                .strip(),

            "ct_primary":
                self.ct_primary_edit
                .text()
                .strip(),

            "ct_secondary":
                self.ct_secondary_edit
                .text()
                .strip(),

            "ct_ratio":
                self.ct_ratio_edit
                .text()
                .strip(),

            "ct_class":
                self.ct_class_edit
                .text()
                .strip(),

            "burden":
                self.burden_edit
                .text()
                .strip(),

            "core":
                self.core_edit
                .text()
                .strip(),

            "vt_ratio":
                self.vt_ratio_edit
                .text()
                .strip(),

            "firmware":
                self.firmware_edit
                .text()
                .strip(),

            "coil_voltage":
                self.coil_voltage_edit
                .text()
                .strip(),

            "contact_configuration":
                self.contact_configuration_edit
                .text()
                .strip(),
        }

        # -------------------------------------------------
        # METER
        # -------------------------------------------------

        if self.component_type == "METER":

            meter_type = (
                self.meter_type_combo
                .currentData()
            )

            functions = []

            for row in range(
                self.meter_function_list.count()
            ):

                item = (
                    self.meter_function_list
                    .item(row)
                )

                if (
                    item.checkState()
                    == Qt.CheckState.Checked
                ):

                    functions.append(
                        item.data(
                            Qt.ItemDataRole.UserRole
                        )
                    )

            configuration.update({

                "meter_type":
                    meter_type or "",

                "meter_functions":
                    functions,

                "accuracy_class":
                    self.accuracy_class_edit
                    .text()
                    .strip(),
            })

        return configuration