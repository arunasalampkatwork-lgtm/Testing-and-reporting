from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QHBoxLayout,
    QComboBox
)


class ComponentConfigDialog(QDialog):

    def __init__(
        self,
        component,
        parent=None
    ):

        super().__init__(parent)

        self.component = component

        self.setWindowTitle(
            f"Configure {component.name}"
        )

        self.resize(
            500,
            400
        )

        layout = QVBoxLayout(self)

        form = QFormLayout()

        # =====================================================
        # COMMON FIELDS
        # =====================================================

        self.manufacturer = QLineEdit()

        self.model = QLineEdit()

        self.serial_number = QLineEdit()

        form.addRow(
            "Manufacturer:",
            self.manufacturer
        )

        form.addRow(
            "Model:",
            self.model
        )

        form.addRow(
            "Serial Number:",
            self.serial_number
        )

        # =====================================================
        # COMPONENT-SPECIFIC FIELDS
        # =====================================================

        self.extra_fields = {}

        if component.component_type == "CT":

            self.add_ct_fields(
                form
            )

        elif component.component_type == "NUMERICAL_RELAY":

            self.add_relay_fields(
                form
            )

        elif component.component_type == "AUXILIARY_RELAY":

            self.add_auxiliary_relay_fields(
                form
            )

        layout.addLayout(
            form
        )

        # =====================================================
        # BUTTONS
        # =====================================================

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

        self.load_existing_values()

    # =========================================================
    # CT
    # =========================================================

    def add_ct_fields(
        self,
        form
    ):

        self.extra_fields[
            "ct_ratio"
        ] = QLineEdit()

        self.extra_fields[
            "ct_class"
        ] = QLineEdit()

        self.extra_fields[
            "burden"
        ] = QLineEdit()

        self.extra_fields[
            "core"
        ] = QLineEdit()

        form.addRow(
            "CT Ratio:",
            self.extra_fields["ct_ratio"]
        )

        form.addRow(
            "Class:",
            self.extra_fields["ct_class"]
        )

        form.addRow(
            "Burden:",
            self.extra_fields["burden"]
        )

        form.addRow(
            "Core:",
            self.extra_fields["core"]
        )

    # =========================================================
    # NUMERICAL RELAY
    # =========================================================

    def add_relay_fields(
        self,
        form
    ):

        self.extra_fields[
            "ct_ratio"
        ] = QLineEdit()

        self.extra_fields[
            "vt_ratio"
        ] = QLineEdit()

        self.extra_fields[
            "firmware"
        ] = QLineEdit()

        form.addRow(
            "CT Ratio:",
            self.extra_fields["ct_ratio"]
        )

        form.addRow(
            "VT Ratio:",
            self.extra_fields["vt_ratio"]
        )

        form.addRow(
            "Firmware:",
            self.extra_fields["firmware"]
        )

    # =========================================================
    # AUXILIARY RELAY
    # =========================================================

    def add_auxiliary_relay_fields(
        self,
        form
    ):

        self.extra_fields[
            "coil_voltage"
        ] = QLineEdit()

        self.extra_fields[
            "contact_configuration"
        ] = QLineEdit()

        form.addRow(
            "Coil Voltage:",
            self.extra_fields["coil_voltage"]
        )

        form.addRow(
            "Contact Configuration:",
            self.extra_fields[
                "contact_configuration"
            ]
        )

    # =========================================================
    # LOAD EXISTING
    # =========================================================

    def load_existing_values(
        self
    ):

        self.manufacturer.setText(
            getattr(
                self.component,
                "manufacturer",
                ""
            )
        )

        self.model.setText(
            getattr(
                self.component,
                "model",
                ""
            )
        )

        self.serial_number.setText(
            getattr(
                self.component,
                "serial_number",
                ""
            )
        )

        for key, widget in self.extra_fields.items():

            value = getattr(
                self.component,
                key,
                ""
            )

            widget.setText(
                str(value)
            )

    # =========================================================
    # GET CONFIGURATION
    # =========================================================

    def get_configuration(
        self
    ):

        configuration = {

            "manufacturer":
                self.manufacturer.text().strip(),

            "model":
                self.model.text().strip(),

            "serial_number":
                self.serial_number.text().strip()
        }

        for key, widget in self.extra_fields.items():

            configuration[key] = (
                widget.text().strip()
            )

        return configuration