from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QScrollArea,
    QComboBox,
)


class CTTestingDialog(QDialog):

    def __init__(
        self,
        project_id,
        panel_id,
        component,
        test_service=None,
        parent=None,
    ):
        super().__init__(parent)

        self.project_id = project_id
        self.panel_id = panel_id
        self.component = component
        self.test_service = test_service

        self.fields = {}

        self.setWindowTitle(
            f"CT Testing - {component.name}"
        )

        self.resize(900, 750)

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = QLabel(
            f"Current Transformer Testing - "
            f"{self.component.name}"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )

        main_layout.addWidget(header)

        # -------------------------------------------------
        # SCROLL AREA
        # -------------------------------------------------

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        container = QDialog()

        container_layout = QVBoxLayout(container)

        # -------------------------------------------------
        # CT IDENTIFICATION
        # -------------------------------------------------

        identification = QGroupBox(
            "CT Identification"
        )

        identification_layout = QFormLayout()

        self.add_field(
            identification_layout,
            "ct_ratio",
            "CT Ratio",
            getattr(
                self.component,
                "ct_ratio",
                ""
            ),
        )

        self.add_field(
            identification_layout,
            "core",
            "Core",
            getattr(
                self.component,
                "core",
                ""
            ),
        )

        self.add_field(
            identification_layout,
            "ct_class",
            "CT Class",
            getattr(
                self.component,
                "ct_class",
                ""
            ),
        )

        self.add_field(
            identification_layout,
            "burden",
            "Rated Burden",
            getattr(
                self.component,
                "burden",
                ""
            ),
        )

        self.add_field(
            identification_layout,
            "manufacturer",
            "Manufacturer",
            getattr(
                self.component,
                "manufacturer",
                ""
            ),
        )

        self.add_field(
            identification_layout,
            "model",
            "Model",
            getattr(
                self.component,
                "model",
                ""
            ),
        )

        self.add_field(
            identification_layout,
            "serial_number",
            "Serial Number",
            getattr(
                self.component,
                "serial_number",
                ""
            ),
        )

        identification.setLayout(
            identification_layout
        )

        container_layout.addWidget(
            identification
        )

        # -------------------------------------------------
        # RATIO TEST
        # -------------------------------------------------

        ratio_group = QGroupBox(
            "CT Ratio Test"
        )

        ratio_layout = QFormLayout()

        self.add_field(
            ratio_layout,
            "primary_current",
            "Primary Current",
            "",
            "A",
        )

        self.add_field(
            ratio_layout,
            "secondary_current",
            "Secondary Current",
            "",
            "A",
        )

        self.add_readonly(
            ratio_layout,
            "measured_ratio",
            "Measured Ratio",
        )

        self.add_readonly(
            ratio_layout,
            "ratio_error",
            "Ratio Error",
            "%",
        )

        ratio_group.setLayout(
            ratio_layout
        )

        container_layout.addWidget(
            ratio_group
        )

        self.fields[
            "primary_current"
        ].textChanged.connect(
            self.calculate_ratio
        )

        self.fields[
            "secondary_current"
        ].textChanged.connect(
            self.calculate_ratio
        )

        # -------------------------------------------------
        # POLARITY
        # -------------------------------------------------

        polarity_group = QGroupBox(
            "Polarity Test"
        )

        polarity_layout = QFormLayout()

        self.add_combo(
            polarity_layout,
            "expected_polarity",
            "Expected Polarity",
            [
                "CORRECT",
                "REVERSE",
            ],
        )

        self.add_combo(
            polarity_layout,
            "observed_polarity",
            "Observed Polarity",
            [
                "CORRECT",
                "REVERSE",
            ],
        )

        self.add_readonly(
            polarity_layout,
            "polarity_result",
            "Polarity Result",
        )

        polarity_group.setLayout(
            polarity_layout
        )

        container_layout.addWidget(
            polarity_group
        )

        self.fields[
            "expected_polarity"
        ].currentTextChanged.connect(
            self.calculate_polarity
        )

        self.fields[
            "observed_polarity"
        ].currentTextChanged.connect(
            self.calculate_polarity
        )

        # -------------------------------------------------
        # INSULATION RESISTANCE
        # -------------------------------------------------

        ir_group = QGroupBox(
            "Insulation Resistance"
        )

        ir_layout = QFormLayout()

        self.add_field(
            ir_layout,
            "ir_primary_earth",
            "Primary - Earth",
            "",
            "MΩ",
        )

        self.add_field(
            ir_layout,
            "ir_secondary_earth",
            "Secondary - Earth",
            "",
            "MΩ",
        )

        self.add_field(
            ir_layout,
            "ir_primary_secondary",
            "Primary - Secondary",
            "",
            "MΩ",
        )

        self.add_field(
            ir_layout,
            "ir_test_voltage",
            "Test Voltage",
            "",
            "V",
        )

        self.add_field(
            ir_layout,
            "ir_test_duration",
            "Test Duration",
            "",
            "s",
        )

        ir_group.setLayout(
            ir_layout
        )

        container_layout.addWidget(
            ir_group
        )

        # -------------------------------------------------
        # WINDING RESISTANCE
        # -------------------------------------------------

        winding_group = QGroupBox(
            "Winding Resistance"
        )

        winding_layout = QFormLayout()

        self.add_field(
            winding_layout,
            "resistance_phase_a",
            "Phase A",
            "",
            "Ω",
        )

        self.add_field(
            winding_layout,
            "resistance_phase_b",
            "Phase B",
            "",
            "Ω",
        )

        self.add_field(
            winding_layout,
            "resistance_phase_c",
            "Phase C",
            "",
            "Ω",
        )

        self.add_field(
            winding_layout,
            "resistance_test_current",
            "Test Current",
            "",
            "A",
        )

        self.add_field(
            winding_layout,
            "winding_temperature",
            "Winding Temperature",
            "",
            "°C",
        )

        winding_group.setLayout(
            winding_layout
        )

        container_layout.addWidget(
            winding_group
        )

        # -------------------------------------------------
        # EXCITATION / KNEE POINT
        # -------------------------------------------------

        excitation_group = QGroupBox(
            "Excitation / Knee Point Test"
        )

        excitation_layout = QFormLayout()

        self.add_field(
            excitation_layout,
            "knee_point_voltage",
            "Knee Point Voltage",
            "",
            "V",
        )

        self.add_field(
            excitation_layout,
            "knee_point_current",
            "Knee Point Current",
            "",
            "mA",
        )

        self.add_field(
            excitation_layout,
            "excitation_test_voltage",
            "Test Voltage",
            "",
            "V",
        )

        self.add_field(
            excitation_layout,
            "excitation_test_current",
            "Excitation Current",
            "",
            "mA",
        )

        excitation_group.setLayout(
            excitation_layout
        )

        container_layout.addWidget(
            excitation_group
        )

        # -------------------------------------------------
        # BURDEN
        # -------------------------------------------------

        burden_group = QGroupBox(
            "Burden Test"
        )

        burden_layout = QFormLayout()

        self.add_field(
            burden_layout,
            "burden_test_current",
            "Test Current",
            "",
            "A",
        )

        self.add_field(
            burden_layout,
            "measured_burden",
            "Measured Burden",
            "",
            "VA",
        )

        self.add_readonly(
            burden_layout,
            "burden_error",
            "Burden Error",
            "%",
        )

        burden_group.setLayout(
            burden_layout
        )

        container_layout.addWidget(
            burden_group
        )

        self.fields[
            "measured_burden"
        ].textChanged.connect(
            self.calculate_burden
        )

        # -------------------------------------------------
        # ENGINEERING VALIDATION
        # -------------------------------------------------

        validation_group = QGroupBox(
            "Engineering Validation"
        )

        validation_layout = QFormLayout()

        self.add_field(
            validation_layout,
            "tolerance_percent",
            "Tolerance",
            "5",
            "%",
        )

        validation_group.setLayout(
            validation_layout
        )

        container_layout.addWidget(
            validation_group
        )

        # -------------------------------------------------
        # REMARKS
        # -------------------------------------------------

        remarks_group = QGroupBox(
            "Remarks and Result"
        )

        remarks_layout = QFormLayout()

        self.add_field(
            remarks_layout,
            "remarks",
            "Remarks",
        )

        self.add_combo(
            remarks_layout,
            "result",
            "Result",
            [
                "PASS",
                "FAIL",
                "NOT TESTED",
            ],
        )

        remarks_group.setLayout(
            remarks_layout
        )

        container_layout.addWidget(
            remarks_group
        )

        container_layout.addStretch()

        scroll.setWidget(
            container
        )

        main_layout.addWidget(
            scroll
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        clear_button = QPushButton(
            "Clear"
        )

        save_button = QPushButton(
            "Save Test"
        )

        close_button = QPushButton(
            "Close"
        )

        clear_button.clicked.connect(
            self.clear_fields
        )

        save_button.clicked.connect(
            self.save_test
        )

        close_button.clicked.connect(
            self.reject
        )

        button_layout.addWidget(
            clear_button
        )

        button_layout.addWidget(
            save_button
        )

        button_layout.addWidget(
            close_button
        )

        main_layout.addLayout(
            button_layout
        )

    # =====================================================
    # FIELD HELPERS
    # =====================================================

    def add_field(
        self,
        layout,
        field_id,
        label,
        default="",
        unit="",
    ):

        widget = QLineEdit()

        widget.setText(
            str(default or "")
        )

        if unit:
            label = f"{label} ({unit})"

        self.fields[field_id] = widget

        layout.addRow(
            QLabel(label),
            widget
        )

    def add_readonly(
        self,
        layout,
        field_id,
        label,
        unit="",
    ):

        widget = QLineEdit()

        widget.setReadOnly(True)

        if unit:
            label = f"{label} ({unit})"

        self.fields[field_id] = widget

        layout.addRow(
            QLabel(label),
            widget
        )

    def add_combo(
        self,
        layout,
        field_id,
        label,
        options,
    ):

        widget = QComboBox()

        widget.addItems(
            options
        )

        self.fields[field_id] = widget

        layout.addRow(
            QLabel(label),
            widget
        )

    # =====================================================
    # CALCULATIONS
    # =====================================================

    def calculate_ratio(self):

        try:

            primary = float(
                self.fields[
                    "primary_current"
                ].text()
            )

            secondary = float(
                self.fields[
                    "secondary_current"
                ].text()
            )

            if secondary == 0:
                raise ValueError

            ratio = (
                primary / secondary
            )

            self.fields[
                "measured_ratio"
            ].setText(
                f"{ratio:.4f}"
            )

            configured_ratio = str(
                getattr(
                    self.component,
                    "ct_ratio",
                    ""
                )
            )

            if "/" in configured_ratio:

                expected = float(
                    configured_ratio
                    .split("/")[0]
                ) / float(
                    configured_ratio
                    .split("/")[1]
                )

                error = (
                    (ratio - expected)
                    / expected
                ) * 100

                self.fields[
                    "ratio_error"
                ].setText(
                    f"{error:.2f}"
                )

        except (
            ValueError,
            ZeroDivisionError,
        ):

            self.fields[
                "measured_ratio"
            ].clear()

            self.fields[
                "ratio_error"
            ].clear()

    def calculate_polarity(self):

        expected = self.fields[
            "expected_polarity"
        ].currentText()

        observed = self.fields[
            "observed_polarity"
        ].currentText()

        if expected == observed:

            self.fields[
                "polarity_result"
            ].setText("PASS")

        else:

            self.fields[
                "polarity_result"
            ].setText("FAIL")

    def calculate_burden(self):

        try:

            measured = float(
                self.fields[
                    "measured_burden"
                ].text()
            )

            rated = str(
                getattr(
                    self.component,
                    "burden",
                    ""
                )
            )

            rated_value = float(
                rated.lower()
                .replace("va", "")
                .strip()
            )

            if rated_value == 0:
                raise ValueError

            error = (
                (measured - rated_value)
                / rated_value
            ) * 100

            self.fields[
                "burden_error"
            ].setText(
                f"{error:.2f}"
            )

        except (
            ValueError,
            ZeroDivisionError,
        ):

            self.fields[
                "burden_error"
            ].clear()

    # =====================================================
    # VALUES
    # =====================================================

    def get_field_values(self):

        values = {}

        for field_id, widget in self.fields.items():

            if isinstance(
                widget,
                QLineEdit,
            ):

                values[field_id] = (
                    widget.text().strip()
                )

            elif isinstance(
                widget,
                QComboBox,
            ):

                values[field_id] = (
                    widget.currentText()
                )

        return values

    # =====================================================
    # SAVE
    # =====================================================

    def save_test(self):

        values = self.get_field_values()

        if not self.test_service:

            QMessageBox.warning(
                self,
                "Save Failed",
                "Test service is not available."
            )

            return

        try:

            test_id = (
                self.test_service
                .save_component_test(
                    project_id=self.project_id,
                    panel_id=self.panel_id,
                    component_id=self.component.component_id,
                    test_type="CT",
                    measurements=values,
                    result=values.get(
                        "result",
                        "NOT TESTED",
                    ),
                    remarks=values.get(
                        "remarks",
                        "",
                    ),
                )
            )

            QMessageBox.information(
                self,
                "Test Saved",
                f"CT test saved successfully.\n\n"
                f"Test ID: {test_id}",
            )

        except AttributeError:

            QMessageBox.warning(
                self,
                "Save Method Missing",
                "The test service does not yet have "
                "save_component_test().",
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error),
            )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear_fields(self):

        for widget in self.fields.values():

            if isinstance(
                widget,
                QLineEdit,
            ):

                widget.clear()

        self.fields[
            "tolerance_percent"
        ].setText("5")

        self.fields[
            "result"
        ].setCurrentIndex(2)