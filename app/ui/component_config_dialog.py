from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)


class ComponentConfigDialog(QDialog):

    def __init__(
        self,
        component,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.component = (
            component
        )

        self.component_type = (
            str(
                getattr(
                    component,
                    "component_type",
                    ""
                )
            )
            .strip()
            .upper()
        )

        self.fields = {}

        self.setWindowTitle(
            f"Component Configuration - "
            f"{component.name}"
        )

        self.resize(
            550,
            550
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

        form = QFormLayout()

        # =================================================
        # NAME
        # =================================================

        self.name_edit = QLineEdit()

        self.name_edit.setReadOnly(
            True
        )

        form.addRow(
            "Component:",
            self.name_edit
        )

        # =================================================
        # COMMON
        # =================================================

        self.manufacturer_edit = (
            QLineEdit()
        )

        self.model_edit = (
            QLineEdit()
        )

        self.serial_number_edit = (
            QLineEdit()
        )

        self.description_edit = (
            QLineEdit()
        )

        form.addRow(
            "Manufacturer:",
            self.manufacturer_edit
        )

        form.addRow(
            "Model:",
            self.model_edit
        )

        form.addRow(
            "Serial Number:",
            self.serial_number_edit
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

        self.ct_secondary_edit = (
            QLineEdit()
        )

        self.ct_ratio_edit = (
            QLineEdit()
        )

        self.ct_ratio_edit.setReadOnly(
            True
        )

        self.ct_class_edit = (
            QLineEdit()
        )

        self.burden_edit = (
            QLineEdit()
        )

        self.core_edit = (
            QLineEdit()
        )

        if self.component_type in (
            "CT",
            "CURRENT TRANSFORMER",
        ):

            form.addRow(
                "CT Primary (A):",
                self.ct_primary_edit
            )

            form.addRow(
                "CT Secondary (A):",
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

        layout.addLayout(
            form
        )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        save_button = QPushButton(
            "Save"
        )

        cancel_button = QPushButton(
            "Cancel"
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

        save_button.clicked.connect(
            self.accept
        )

        cancel_button.clicked.connect(
            self.reject
        )

    # =====================================================
    # POPULATE
    # =====================================================

    def populate_existing_values(self):

        component = (
            self.component
        )

        self.name_edit.setText(
            str(
                getattr(
                    component,
                    "name",
                    ""
                )
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

        # =================================================
        # CT
        # =================================================

        self.ct_primary_edit.setText(
            self._display_number(
                getattr(
                    component,
                    "ct_primary",
                    0
                )
            )
        )

        self.ct_secondary_edit.setText(
            self._display_number(
                getattr(
                    component,
                    "ct_secondary",
                    0
                )
            )
        )

        self.ct_ratio_edit.setText(
            str(
                getattr(
                    component,
                    "ct_ratio",
                    ""
                )
                or ""
            )
        )

        self.ct_class_edit.setText(
            str(
                getattr(
                    component,
                    "ct_class",
                    ""
                )
                or ""
            )
        )

        self.burden_edit.setText(
            str(
                getattr(
                    component,
                    "burden",
                    ""
                )
                or ""
            )
        )

        self.core_edit.setText(
            str(
                getattr(
                    component,
                    "core",
                    ""
                )
                or ""
            )
        )

        # =================================================
        # RELAY
        # =================================================

        self.vt_ratio_edit.setText(
            str(
                getattr(
                    component,
                    "vt_ratio",
                    ""
                )
                or ""
            )
        )

        self.firmware_edit.setText(
            str(
                getattr(
                    component,
                    "firmware",
                    ""
                )
                or ""
            )
        )

        # =================================================
        # AUX
        # =================================================

        self.coil_voltage_edit.setText(
            str(
                getattr(
                    component,
                    "coil_voltage",
                    ""
                )
                or ""
            )
        )

        self.contact_configuration_edit.setText(
            str(
                getattr(
                    component,
                    "contact_configuration",
                    ""
                )
                or ""
            )
        )

        self.update_ct_ratio()

    # =====================================================
    # CT RATIO
    # =====================================================

    def update_ct_ratio(self):

        try:

            primary = float(
                self.ct_primary_edit
                .text()
                .strip()
            )

            secondary = float(
                self.ct_secondary_edit
                .text()
                .strip()
            )

            if (
                primary <= 0
                or secondary <= 0
            ):

                raise ValueError

            self.ct_ratio_edit.setText(
                f"{primary:g}/{secondary:g}"
            )

        except (
            ValueError,
            TypeError
        ):

            self.ct_ratio_edit.clear()

    # =====================================================
    # GET CONFIGURATION
    # =====================================================

    def get_configuration(self):

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

        return configuration

    # =====================================================
    # DISPLAY NUMBER
    # =====================================================

    @staticmethod
    def _display_number(
        value
    ):

        try:

            number = float(
                value or 0
            )

            if number == 0:

                return ""

            return f"{number:g}"

        except (
            TypeError,
            ValueError
        ):

            return str(
                value
                or ""
            )