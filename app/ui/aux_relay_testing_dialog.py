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


class AuxRelayTestingDialog(QDialog):

    def __init__(
        self,
        project_id,
        panel_id,
        component,
        test_service=None,
        existing_test=None,
        test_id=None,
        parent=None,
    ):
        super().__init__(parent)

        self.project_id = project_id
        self.panel_id = panel_id
        self.component = component
        self.test_service = test_service
        self.test_id = test_id
        self.existing_test = existing_test

        self.fields = {}

        self.setWindowTitle(
            f"Auxiliary Relay Testing - "
            f"{component.name}"
        )

        self.resize(850, 700)

        self.build_ui()
        if self.existing_test:

            self.populate_existing_test()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        main_layout = QVBoxLayout(self)

        header = QLabel(
            f"Auxiliary Relay Testing - "
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

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        container = QDialog()

        container_layout = QVBoxLayout(container)

        # =================================================
        # IDENTIFICATION
        # =================================================

        identification = QGroupBox(
            "Relay Identification"
        )

        identification_layout = QFormLayout()

        self.add_field(
            identification_layout,
            "manufacturer",
            "Manufacturer",
            getattr(
                self.component,
                "manufacturer",
                "",
            ),
        )

        self.add_field(
            identification_layout,
            "model",
            "Model",
            getattr(
                self.component,
                "model",
                "",
            ),
        )

        self.add_field(
            identification_layout,
            "serial_number",
            "Serial Number",
            getattr(
                self.component,
                "serial_number",
                "",
            ),
        )

        self.add_field(
            identification_layout,
            "coil_voltage",
            "Coil Voltage",
            getattr(
                self.component,
                "coil_voltage",
                "",
            ),
            "V DC",
        )

        self.add_field(
            identification_layout,
            "contact_configuration",
            "Contact Configuration",
            getattr(
                self.component,
                "contact_configuration",
                "",
            ),
        )

        identification.setLayout(
            identification_layout
        )

        container_layout.addWidget(
            identification
        )

        # =================================================
        # COIL TEST
        # =================================================

        coil_group = QGroupBox(
            "Coil Pickup / Dropout Test"
        )

        coil_layout = QFormLayout()

        self.add_field(
            coil_layout,
            "rated_voltage",
            "Rated Coil Voltage",
            getattr(
                self.component,
                "coil_voltage",
                "",
            ),
            "V",
        )

        self.add_field(
            coil_layout,
            "pickup_voltage",
            "Measured Pickup Voltage",
            "",
            "V",
        )

        self.add_readonly(
            coil_layout,
            "pickup_voltage_percent",
            "Pickup Voltage",
            "%",
        )

        self.add_field(
            coil_layout,
            "dropout_voltage",
            "Measured Dropout Voltage",
            "",
            "V",
        )

        self.add_readonly(
            coil_layout,
            "dropout_voltage_percent",
            "Dropout Voltage",
            "%",
        )

        coil_group.setLayout(
            coil_layout
        )

        container_layout.addWidget(
            coil_group
        )

        self.fields[
            "rated_voltage"
        ].textChanged.connect(
            self.calculate_coil
        )

        self.fields[
            "pickup_voltage"
        ].textChanged.connect(
            self.calculate_coil
        )

        self.fields[
            "dropout_voltage"
        ].textChanged.connect(
            self.calculate_coil
        )

        # =================================================
        # TIMING
        # =================================================

        timing_group = QGroupBox(
            "Operating Time"
        )

        timing_layout = QFormLayout()

        self.add_field(
            timing_layout,
            "expected_pickup_time",
            "Expected Pickup Time",
            "",
            "ms",
        )

        self.add_field(
            timing_layout,
            "pickup_time",
            "Measured Pickup Time",
            "",
            "ms",
        )

        self.add_readonly(
            timing_layout,
            "pickup_time_error",
            "Pickup Time Error",
            "%",
        )

        self.add_field(
            timing_layout,
            "expected_dropout_time",
            "Expected Dropout Time",
            "",
            "ms",
        )

        self.add_field(
            timing_layout,
            "dropout_time",
            "Measured Dropout Time",
            "",
            "ms",
        )

        self.add_readonly(
            timing_layout,
            "dropout_time_error",
            "Dropout Time Error",
            "%",
        )

        timing_group.setLayout(
            timing_layout
        )

        container_layout.addWidget(
            timing_group
        )

        for field in (
            "expected_pickup_time",
            "pickup_time",
            "expected_dropout_time",
            "dropout_time",
        ):

            self.fields[
                field
            ].textChanged.connect(
                self.calculate_timing
            )

        # =================================================
        # CONTACT TEST
        # =================================================

        contact_group = QGroupBox(
            "Contact Test"
        )

        contact_layout = QFormLayout()

        self.add_combo(
            contact_layout,
            "no_contact_result",
            "NO Contact",
            [
                "PASS",
                "FAIL",
                "NOT TESTED",
            ],
        )

        self.add_combo(
            contact_layout,
            "nc_contact_result",
            "NC Contact",
            [
                "PASS",
                "FAIL",
                "NOT TESTED",
            ],
        )

        self.add_field(
            contact_layout,
            "contact_resistance",
            "Contact Resistance",
            "",
            "mΩ",
        )

        contact_group.setLayout(
            contact_layout
        )

        container_layout.addWidget(
            contact_group
        )

        # =================================================
        # FUNCTIONAL TEST
        # =================================================

        functional_group = QGroupBox(
            "Functional Test"
        )

        functional_layout = QFormLayout()

        self.add_combo(
            functional_layout,
            "expected_operation",
            "Expected Operation",
            [
                "OPERATE",
                "NO OPERATE",
            ],
        )

        self.add_combo(
            functional_layout,
            "observed_operation",
            "Observed Operation",
            [
                "OPERATE",
                "NO OPERATE",
            ],
        )

        self.add_readonly(
            functional_layout,
            "functional_result",
            "Functional Result",
        )

        functional_group.setLayout(
            functional_layout
        )

        container_layout.addWidget(
            functional_group
        )

        self.fields[
            "expected_operation"
        ].currentTextChanged.connect(
            self.calculate_functional
        )

        self.fields[
            "observed_operation"
        ].currentTextChanged.connect(
            self.calculate_functional
        )

        # =================================================
        # ENGINEERING VALIDATION
        # =================================================

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

        # =================================================
        # REMARKS / RESULT
        # =================================================

        result_group = QGroupBox(
            "Remarks and Result"
        )

        result_layout = QFormLayout()

        self.add_field(
            result_layout,
            "remarks",
            "Remarks",
        )

        self.add_combo(
            result_layout,
            "result",
            "Result",
            [
                "PASS",
                "FAIL",
                "NOT TESTED",
            ],
        )

        result_group.setLayout(
            result_layout
        )

        container_layout.addWidget(
            result_group
        )

        container_layout.addStretch()

        scroll.setWidget(
            container
        )

        main_layout.addWidget(
            scroll
        )

        # =================================================
        # BUTTONS
        # =================================================

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

        widget.addItems(options)

        self.fields[field_id] = widget

        layout.addRow(
            QLabel(label),
            widget
        )

    # =====================================================
    # CALCULATIONS
    # =====================================================

    def calculate_coil(self):

        try:

            rated = float(
                self.fields[
                    "rated_voltage"
                ].text()
            )

            if rated == 0:
                raise ValueError

            pickup = float(
                self.fields[
                    "pickup_voltage"
                ].text()
            )

            dropout = float(
                self.fields[
                    "dropout_voltage"
                ].text()
            )

            self.fields[
                "pickup_voltage_percent"
            ].setText(
                f"{pickup / rated * 100:.2f}"
            )

            self.fields[
                "dropout_voltage_percent"
            ].setText(
                f"{dropout / rated * 100:.2f}"
            )

        except (
            ValueError,
            ZeroDivisionError,
        ):

            self.fields[
                "pickup_voltage_percent"
            ].clear()

            self.fields[
                "dropout_voltage_percent"
            ].clear()

    def calculate_timing(self):

        self.calculate_time_error(
            "expected_pickup_time",
            "pickup_time",
            "pickup_time_error",
        )

        self.calculate_time_error(
            "expected_dropout_time",
            "dropout_time",
            "dropout_time_error",
        )

    def calculate_time_error(
        self,
        expected_id,
        actual_id,
        result_id,
    ):

        try:

            expected = float(
                self.fields[
                    expected_id
                ].text()
            )

            actual = float(
                self.fields[
                    actual_id
                ].text()
            )

            if expected == 0:
                raise ValueError

            error = (
                (actual - expected)
                / expected
            ) * 100

            self.fields[
                result_id
            ].setText(
                f"{error:.2f}"
            )

        except (
            ValueError,
            ZeroDivisionError,
        ):

            self.fields[
                result_id
            ].clear()

    def calculate_functional(self):

        expected = self.fields[
            "expected_operation"
        ].currentText()

        observed = self.fields[
            "observed_operation"
        ].currentText()

        if expected == observed:

            self.fields[
                "functional_result"
            ].setText("PASS")

        else:

            self.fields[
                "functional_result"
            ].setText("FAIL")

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
# =====================================================
# SAVE / UPDATE
# =====================================================

    def save_test(
        self
    ):

        values = self.get_field_values()

        if not self.test_service:

            QMessageBox.warning(
                self,
                "Save Failed",
                "Test service is not available."
            )

            return

        try:

            result = (
                values.get(
                    "result",
                    "NOT TESTED"
                )
                or
                "NOT TESTED"
            )

            remarks = (
                values.get(
                    "remarks",
                    ""
                )
            )

            # -------------------------------------------------
            # UPDATE EXISTING TEST
            # -------------------------------------------------

            if self.test_id:

                self.test_service.update_component_test(

                    test_id=(
                        self.test_id
                    ),

                    measurements=(
                        values
                    ),

                    result=(
                        result
                    ),

                    remarks=(
                        remarks
                    )
                )

                QMessageBox.information(
                    self,
                    "Test Updated",
                    (
                        "Auxiliary relay test "
                        "updated successfully.\n\n"
                        f"Test ID: {self.test_id}"
                    )
                )

                self.accept()

                return

            # -------------------------------------------------
            # NEW TEST
            # -------------------------------------------------

            test_id = (
                self.test_service
                .save_component_test(

                    project_id=(
                        self.project_id
                    ),

                    panel_id=(
                        self.panel_id
                    ),

                    component_id=(
                        self.component.component_id
                    ),

                    test_type="AUX_RELAY",

                    measurements=(
                        values
                    ),

                    result=(
                        result
                    ),

                    remarks=(
                        remarks
                    )
                )
            )

            QMessageBox.information(
                self,
                "Test Saved",
                (
                    "Auxiliary relay test "
                    "saved successfully.\n\n"
                    f"Test ID: {test_id}"
                )
            )

            self.accept()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error)
            )
 
    # =====================================================
    # POPULATE EXISTING TEST
    # =====================================================

    def populate_existing_test(
        self
    ):

        if not self.existing_test:

            return

        measurements = (
            self.existing_test.get(
                "measurements",
                {}
            )
            or {}
        )

        # -------------------------------------------------
        # POPULATE SAVED VALUES
        # -------------------------------------------------

        for field_id, widget in (
            self.fields.items()
        ):

            if field_id not in measurements:

                continue

            value = measurements.get(
                field_id
            )

            if isinstance(
                widget,
                QLineEdit
            ):

                widget.setText(
                    ""
                    if value is None
                    else str(value)
                )

            elif isinstance(
                widget,
                QComboBox
            ):

                index = widget.findText(
                    str(value)
                )

                if index >= 0:

                    widget.setCurrentIndex(
                        index
                    )

        # -------------------------------------------------
        # REMARKS
        # -------------------------------------------------

        if hasattr(
            self,
            "remarks_widget"
        ):

            self.remarks_widget.setText(
                str(
                    self.existing_test.get(
                        "remarks",
                        measurements.get(
                            "remarks",
                            ""
                        )
                    )
                    or ""
                )
            )

        # -------------------------------------------------
        # TOLERANCE
        # -------------------------------------------------

        if (
            "tolerance_percent"
            in measurements
            and
            hasattr(
                self,
                "tolerance_widget"
            )
        ):

            self.tolerance_widget.setText(
                str(
                    measurements[
                        "tolerance_percent"
                    ]
                )
            )

        # -------------------------------------------------
        # RECALCULATE EVERYTHING
        # -------------------------------------------------

        try:

            self.calculate_coil()

        except Exception:

            pass

        try:

            self.calculate_timing()

        except Exception:

            pass

        try:

            self.calculate_functional()

        except Exception:

            pass

        try:

            self.calculate_overall_result()

        except Exception:

            pass

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