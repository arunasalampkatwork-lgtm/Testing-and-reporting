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
)
from PySide6.QtCore import Qt


class ComponentConfigDialog(QDialog):

    # =====================================================
    # METER TYPES
    # =====================================================

    METER_TYPES = [
        "Ammeter",
        "Voltmeter",
        "Multifunction Meter",
    ]

    # =====================================================
    # METER FUNCTIONS
    # =====================================================

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

    # =====================================================
    # FUNCTION DISPLAY LABELS
    # =====================================================

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

    # =====================================================
    # INITIALIZATION
    # =====================================================

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
            or ""
        ).strip().upper()

        self.setWindowTitle(
            f"Edit Component - {component.name}"
        )

        self.resize(
            600,
            650
        )

        self.build_ui()

        self.populate_existing_values()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(
        self
    ):

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

        form = QFormLayout()

        form.setSpacing(
            10
        )

        # =================================================
        # COMMON
        # =================================================

        self.name_edit = QLineEdit()

        self.name_edit.setReadOnly(
            True
        )

        form.addRow(
            "Component:",
            self.name_edit
        )

        self.manufacturer_edit = (
            QLineEdit()
        )

        form.addRow(
            "Manufacturer:",
            self.manufacturer_edit
        )

        self.model_edit = (
            QLineEdit()
        )

        form.addRow(
            "Model:",
            self.model_edit
        )

        self.serial_number_edit = (
            QLineEdit()
        )

        form.addRow(
            "Serial Number:",
            self.serial_number_edit
        )

        self.description_edit = (
            QLineEdit()
        )

        form.addRow(
            "Description:",
            self.description_edit
        )

        # =================================================
        # CT
        # =================================================

        self.ct_primary_edit = (
            QLineEdit()
        )

        self.ct_primary_edit.setPlaceholderText(
            "e.g. 1000"
        )

        self.ct_secondary_edit = (
            QLineEdit()
        )

        self.ct_secondary_edit.setPlaceholderText(
            "e.g. 5"
        )

        self.ct_ratio_edit = (
            QLineEdit()
        )

        self.ct_ratio_edit.setPlaceholderText(
            "Automatically generated"
        )

        # Ratio should be derived from primary/secondary.
        self.ct_ratio_edit.setReadOnly(
            True
        )

        self.ct_class_edit = (
            QLineEdit()
        )

        self.ct_class_edit.setPlaceholderText(
            "e.g. 5P20"
        )

        self.burden_edit = (
            QLineEdit()
        )

        self.burden_edit.setPlaceholderText(
            "e.g. 15 VA"
        )

        self.core_edit = (
            QLineEdit()
        )

        self.core_edit.setPlaceholderText(
            "e.g. Protection"
        )

        if self.component_type in (
            "CT",
            "CURRENT TRANSFORMER",
        ):

            form.addRow(
                "CT Primary:",
                self.ct_primary_edit
            )

            form.addRow(
                "CT Secondary:",
                self.ct_secondary_edit
            )

            form.addRow(
                "CT Ratio:",
                self.ct_ratio_edit
            )

            form.addRow(
                "CT Class:",
                self.ct_class_edit
            )

            form.addRow(
                "Burden:",
                self.burden_edit
            )

            form.addRow(
                "Core:",
                self.core_edit
            )

            # -------------------------------------------------
            # Automatically update ratio
            # -------------------------------------------------

            self.ct_primary_edit.textChanged.connect(
                self.update_ct_ratio
            )

            self.ct_secondary_edit.textChanged.connect(
                self.update_ct_ratio
            )

        # =================================================
        # NUMERICAL RELAY
        # =================================================

        self.vt_ratio_edit = (
            QLineEdit()
        )

        self.firmware_edit = (
            QLineEdit()
        )

        if self.component_type == (
            "NUMERICAL_RELAY"
        ):

            form.addRow(
                "VT Ratio:",
                self.vt_ratio_edit
            )

            form.addRow(
                "Firmware:",
                self.firmware_edit
            )

        # =================================================
        # AUXILIARY RELAY
        # =================================================

        self.coil_voltage_edit = (
            QLineEdit()
        )

        self.contact_configuration_edit = (
            QLineEdit()
        )

        if self.component_type in (
            "AUXILIARY_RELAY",
            "AUX RELAY",
        ):

            form.addRow(
                "Coil Voltage:",
                self.coil_voltage_edit
            )

            form.addRow(
                "Contact Configuration:",
                self.contact_configuration_edit
            )

        # =================================================
        # METER
        # =================================================

        self.meter_type_combo = (
            QComboBox()
        )

        self.meter_type_combo.addItem(
            "Select meter type",
            ""
        )

        for meter_type in (
            self.METER_TYPES
        ):

            self.meter_type_combo.addItem(
                meter_type,
                meter_type
            )

        self.meter_type_combo.currentIndexChanged.connect(
            self.update_meter_functions
        )

        self.accuracy_class_edit = (
            QLineEdit()
        )

        self.meter_function_list = (
            QListWidget()
        )

        self.meter_function_list.setMinimumHeight(
            150
        )

        self.meter_function_list.setMaximumHeight(
            220
        )

        if self.component_type == "METER":

            form.addRow(
                "Meter Type:",
                self.meter_type_combo
            )

            form.addRow(
                "Accuracy Class:",
                self.accuracy_class_edit
            )

            form.addRow(
                "Test Functions:",
                self.meter_function_list
            )

        layout.addLayout(
            form
        )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        buttons.addStretch()

        save_button = QPushButton(
            "Save"
        )

        cancel_button = QPushButton(
            "Cancel"
        )

        save_button.setMinimumWidth(
            100
        )

        cancel_button.setMinimumWidth(
            100
        )

        save_button.clicked.connect(
            self.accept
        )

        cancel_button.clicked.connect(
            self.reject
        )

        buttons.addWidget(
            save_button
        )

        buttons.addWidget(
            cancel_button
        )

        layout.addLayout(
            buttons
        )

    # =====================================================
    # CT RATIO
    # =====================================================

    def update_ct_ratio(
        self
    ):

        if self.component_type not in (
            "CT",
            "CURRENT TRANSFORMER",
        ):

            return

        primary_text = (
            self.ct_primary_edit
            .text()
            .strip()
        )

        secondary_text = (
            self.ct_secondary_edit
            .text()
            .strip()
        )

        if not primary_text or not secondary_text:

            self.ct_ratio_edit.clear()

            return

        try:

            primary = float(
                primary_text
            )

            secondary = float(
                secondary_text
            )

            if (
                primary <= 0
                or secondary <= 0
            ):

                self.ct_ratio_edit.clear()

                return

            self.ct_ratio_edit.setText(
                f"{self._format_number(primary)}/"
                f"{self._format_number(secondary)}"
            )

        except (
            ValueError,
            TypeError,
        ):

            self.ct_ratio_edit.clear()

    # =====================================================
    # NUMBER FORMAT
    # =====================================================

    @staticmethod
    def _format_number(
        value
    ):

        if float(value).is_integer():

            return str(
                int(value)
            )

        return (
            f"{value:g}"
        )

    # =====================================================
    # POPULATE EXISTING VALUES
    # =====================================================

    def populate_existing_values(
        self
    ):

        # =================================================
        # COMMON
        # =================================================

        self.name_edit.setText(
            str(
                getattr(
                    self.component,
                    "name",
                    ""
                )
                or ""
            )
        )

        self.manufacturer_edit.setText(
            str(
                getattr(
                    self.component,
                    "manufacturer",
                    ""
                )
                or ""
            )
        )

        self.model_edit.setText(
            str(
                getattr(
                    self.component,
                    "model",
                    ""
                )
                or ""
            )
        )

        self.serial_number_edit.setText(
            str(
                getattr(
                    self.component,
                    "serial_number",
                    ""
                )
                or ""
            )
        )

        self.description_edit.setText(
            str(
                getattr(
                    self.component,
                    "description",
                    ""
                )
                or ""
            )
        )

        # =================================================
        # CT
        # =================================================

        ct_primary = getattr(
            self.component,
            "ct_primary",
            ""
        )

        ct_secondary = getattr(
            self.component,
            "ct_secondary",
            ""
        )

        self.ct_primary_edit.setText(
            self._value_to_text(
                ct_primary
            )
        )

        self.ct_secondary_edit.setText(
            self._value_to_text(
                ct_secondary
            )
        )

        self.ct_ratio_edit.setText(
            str(
                getattr(
                    self.component,
                    "ct_ratio",
                    ""
                )
                or ""
            )
        )

        self.ct_class_edit.setText(
            str(
                getattr(
                    self.component,
                    "ct_class",
                    ""
                )
                or ""
            )
        )

        self.burden_edit.setText(
            str(
                getattr(
                    self.component,
                    "burden",
                    ""
                )
                or ""
            )
        )

        self.core_edit.setText(
            str(
                getattr(
                    self.component,
                    "core",
                    ""
                )
                or ""
            )
        )

        # -------------------------------------------------
        # Generate ratio from primary/secondary if possible.
        # -------------------------------------------------

        if (
            str(
                ct_primary
                or ""
            ).strip()
            and
            str(
                ct_secondary
                or ""
            ).strip()
        ):

            self.update_ct_ratio()

        # =================================================
        # NUMERICAL RELAY
        # =================================================

        self.vt_ratio_edit.setText(
            str(
                getattr(
                    self.component,
                    "vt_ratio",
                    ""
                )
                or ""
            )
        )

        self.firmware_edit.setText(
            str(
                getattr(
                    self.component,
                    "firmware",
                    ""
                )
                or ""
            )
        )

        # =================================================
        # AUXILIARY RELAY
        # =================================================

        self.coil_voltage_edit.setText(
            str(
                getattr(
                    self.component,
                    "coil_voltage",
                    ""
                )
                or ""
            )
        )

        self.contact_configuration_edit.setText(
            str(
                getattr(
                    self.component,
                    "contact_configuration",
                    ""
                )
                or ""
            )
        )

        # =================================================
        # METER
        # =================================================

        if self.component_type == "METER":

            existing_type = str(
                getattr(
                    self.component,
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
                str(
                    getattr(
                        self.component,
                        "accuracy_class",
                        ""
                    )
                    or ""
                )
            )

            self.update_meter_functions()

            existing_functions = set(
                getattr(
                    self.component,
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
    # SAFE VALUE TO TEXT
    # =====================================================

    @staticmethod
    def _value_to_text(
        value
    ):

        if value in (
            None,
            "",
        ):

            return ""

        try:

            number = float(
                value
            )

            if number.is_integer():

                return str(
                    int(number)
                )

            return f"{number:g}"

        except (
            TypeError,
            ValueError,
        ):

            return str(
                value
            )

    # =====================================================
    # UPDATE METER FUNCTIONS
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

            item.setCheckState(
                Qt.CheckState.Checked
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

            # =================================================
            # COMMON
            # =================================================

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

            # =================================================
            # CT
            # =================================================

            "ct_primary":
                self._text_to_float(
                    self.ct_primary_edit.text()
                ),

            "ct_secondary":
                self._text_to_float(
                    self.ct_secondary_edit.text()
                ),

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

            # =================================================
            # NUMERICAL RELAY
            # =================================================

            "vt_ratio":
                self.vt_ratio_edit
                .text()
                .strip(),

            "firmware":
                self.firmware_edit
                .text()
                .strip(),

            # =================================================
            # AUXILIARY RELAY
            # =================================================

            "coil_voltage":
                self.coil_voltage_edit
                .text()
                .strip(),

            "contact_configuration":
                self.contact_configuration_edit
                .text()
                .strip(),
        }

        # =================================================
        # METER
        # =================================================

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
                    ==
                    Qt.CheckState.Checked
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

    # =====================================================
    # SAFE FLOAT CONVERSION
    # =====================================================

    @staticmethod
    def _text_to_float(
        text
    ):

        text = str(
            text
            or ""
        ).strip()

        if not text:

            return 0.0

        try:

            return float(
                text
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0.0