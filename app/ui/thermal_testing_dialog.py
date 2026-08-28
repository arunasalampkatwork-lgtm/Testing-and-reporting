from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QGroupBox,
    QLabel,
    QComboBox,
)

from app.services.thermal_template_service import (
    ThermalTemplateService,
)

from app.services.thermal_calculator import (
    ThermalCalculator,
)


DEFAULT_TOLERANCE = 5.0


class ThermalTestingDialog(QDialog):

    def __init__(
        self,
        database,
        manufacturer="",
        model="",
        nominal_current=1.0,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.database = database

        self.service = (
            ThermalTemplateService(
                database
            )
        )

        self.manufacturer = (
            manufacturer
        )

        self.model = (
            model
        )

        self.nominal_current = (
            float(
                nominal_current or 1.0
            )
        )

        self.templates = []

        self.template = None

        self.setWindowTitle(
            "49 - Thermal Overload Testing"
        )

        self.setMinimumWidth(
            750
        )

        self.build_ui()

        self.load_templates()

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )

        # =================================================
        # RELAY
        # =================================================

        relay_group = QGroupBox(
            "Relay"
        )

        relay_layout = QFormLayout()

        self.manufacturer_display = (
            QLineEdit(
                self.manufacturer
            )
        )

        self.manufacturer_display.setReadOnly(
            True
        )

        self.model_display = (
            QLineEdit(
                self.model
            )
        )

        self.model_display.setReadOnly(
            True
        )

        self.template_combo = (
            QComboBox()
        )

        relay_layout.addRow(
            "Manufacturer",
            self.manufacturer_display
        )

        relay_layout.addRow(
            "Model",
            self.model_display
        )

        relay_layout.addRow(
            "Thermal Template",
            self.template_combo
        )

        relay_group.setLayout(
            relay_layout
        )

        layout.addWidget(
            relay_group
        )

        # =================================================
        # TEMPLATE INFO
        # =================================================

        self.template_info = QLabel()

        self.template_info.setWordWrap(
            True
        )

        layout.addWidget(
            self.template_info
        )

        # =================================================
        # SETTINGS
        # =================================================

        settings_group = QGroupBox(
            "Thermal Test"
        )

        settings_layout = QFormLayout()

        self.rated_current = (
            QLineEdit()
        )

        self.pickup_current = (
            QLineEdit()
        )

        self.test_current = (
            QLineEdit()
        )

        self.actual_time = (
            QLineEdit()
        )

        self.tolerance = (
            QLineEdit(
                str(
                    DEFAULT_TOLERANCE
                )
            )
        )

        settings_layout.addRow(
            "Rated Current (A)",
            self.rated_current
        )

        settings_layout.addRow(
            "Pickup (xIn)",
            self.pickup_current
        )

        settings_layout.addRow(
            "Test Current (xIn)",
            self.test_current
        )

        settings_layout.addRow(
            "Actual Operating Time (s)",
            self.actual_time
        )

        settings_layout.addRow(
            "Tolerance (%)",
            self.tolerance
        )

        settings_group.setLayout(
            settings_layout
        )

        layout.addWidget(
            settings_group
        )

        # =================================================
        # RESULT
        # =================================================

        result_group = QGroupBox(
            "Result"
        )

        result_layout = QFormLayout()

        self.expected_time = (
            QLineEdit()
        )

        self.expected_time.setReadOnly(
            True
        )

        self.error_percent = (
            QLineEdit()
        )

        self.error_percent.setReadOnly(
            True
        )

        self.result = (
            QLineEdit()
        )

        self.result.setReadOnly(
            True
        )

        result_layout.addRow(
            "Expected Time (s)",
            self.expected_time
        )

        result_layout.addRow(
            "Error (%)",
            self.error_percent
        )

        result_layout.addRow(
            "Result",
            self.result
        )

        result_group.setLayout(
            result_layout
        )

        layout.addWidget(
            result_group
        )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        self.calculate_button = (
            QPushButton(
                "Calculate Expected Time"
            )
        )

        self.evaluate_button = (
            QPushButton(
                "Evaluate"
            )
        )

        self.close_button = (
            QPushButton(
                "Close"
            )
        )

        buttons.addWidget(
            self.calculate_button
        )

        buttons.addWidget(
            self.evaluate_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.close_button
        )

        layout.addLayout(
            buttons
        )

        # =================================================
        # SIGNALS
        # =================================================

        self.template_combo.currentIndexChanged.connect(
            self.template_changed
        )

        self.calculate_button.clicked.connect(
            self.calculate_expected_time
        )

        self.evaluate_button.clicked.connect(
            self.evaluate_test
        )

        self.close_button.clicked.connect(
            self.close
        )

    # =====================================================
    # LOAD TEMPLATES
    # =====================================================

    def load_templates(self):

        self.templates = (
            self.service.get_templates_for_relay(

                manufacturer=(
                    self.manufacturer
                ),

                model=(
                    self.model
                ),

                protection_function="49"
            )
        )

        self.template_combo.blockSignals(
            True
        )

        self.template_combo.clear()

        for template in self.templates:

            self.template_combo.addItem(
                template.name
            )

        self.template_combo.blockSignals(
            False
        )

        if not self.templates:

            self.template = None

            self.template_info.setText(
                "NO THERMAL TEMPLATE FOUND "
                "FOR THIS RELAY."
            )

            return

        self.template_combo.setCurrentIndex(
            0
        )

        self.template_changed(
            0
        )

    # =====================================================
    # TEMPLATE CHANGED
    # =====================================================

    def template_changed(
        self,
        index
    ):

        if (
            index < 0
            or
            index >= len(
                self.templates
            )
        ):

            return

        self.template = (
            self.templates[index]
        )

        self.rated_current.setText(
            f"{self.template.rated_current:g}"
        )

        self.pickup_current.setText(
            f"{self.template.pickup_current:g}"
        )

        info = (

            f"Template: {self.template.name}\n"

            f"Curve Type: {self.template.curve_type}\n"

            f"Thermal Constant: "
            f"{self.template.thermal_constant:g} s"

        )

        self.template_info.setText(
            info
        )

    # =====================================================
    # EXPECTED TIME
    # =====================================================

    def calculate_expected_time(self):

        if self.template is None:

            QMessageBox.warning(
                self,
                "Thermal Template",
                (
                    "No thermal template is "
                    "configured for this relay."
                )
            )

            return

        try:

            test_current = float(
                self.test_current
                .text()
            )

        except ValueError:

            QMessageBox.warning(
                self,
                "Invalid Input",
                "Enter a valid test current."
            )

            return

        try:

            if (
                self.template.curve_type
                ==
                "POINT_TABLE"
            ):

                expected = (
                    ThermalCalculator.interpolate_time(

                        test_current,

                        self.template.curves
                    )
                )

            elif (
                self.template.curve_type
                ==
                "EXPONENTIAL"
            ):

                expected = (
                    ThermalCalculator.exponential_time(

                        current_multiple=(
                            test_current
                        ),

                        pickup_multiple=(
                            self.template.pickup_current
                        ),

                        thermal_constant=(
                            self.template.thermal_constant
                        )
                    )
                )

            else:

                raise ValueError(
                    "Unsupported thermal curve type."
                )

            self.expected_time.setText(
                f"{expected:.3f}"
            )

        except (
            ValueError,
            OverflowError
        ) as exc:

            QMessageBox.warning(
                self,
                "Calculation Error",
                str(exc)
            )

    # =====================================================
    # EVALUATE
    # =====================================================

    def evaluate_test(self):

        try:

            expected = float(
                self.expected_time
                .text()
            )

            actual = float(
                self.actual_time
                .text()
            )

            tolerance = float(
                self.tolerance
                .text()
            )

        except ValueError:

            QMessageBox.warning(
                self,
                "Invalid Input",
                (
                    "Expected time, actual time "
                    "and tolerance must be valid numbers."
                )
            )

            return

        result = (
            ThermalCalculator.evaluate(

                actual_time=actual,

                expected_time=expected,

                tolerance=tolerance
            )
        )

        self.error_percent.setText(
            f"{result['error_percent']:.2f}"
        )

        self.result.setText(
            result["result"]
        )