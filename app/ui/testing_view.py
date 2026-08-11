from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QScrollArea,
    QComboBox,
    QGroupBox,
)

from app.services.protection_calculator import (
    ProtectionCalculator
)

from app.config.protection_functions import (
    get_protection_function,
    normalize_protection_code,
)

from app.config.protection_curves import (
    get_curves
)


DEFAULT_TOLERANCE = 5.0


class TestingView(QWidget):

    def __init__(
        self,
        project_id,
        panel_id,
        relay_id,
        protection_function,
        test_service,
        parent=None,
    ):

        super().__init__(parent)

        self.project_id = project_id
        self.panel_id = panel_id
        self.relay_id = relay_id
        self.test_service = test_service

        self.protection_function = (
            normalize_protection_code(
                protection_function
            )
        )

        self.fields = {}

        self.setObjectName(
            "TestingView"
        )

        self.setMinimumWidth(
            650
        )

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        function = get_protection_function(
            self.protection_function
        )

        if function is None:

            main_layout.addWidget(
                QLabel(
                    "Unknown protection function."
                )
            )

            return

        # =================================================
        # HEADER
        # =================================================

        header = QLabel(
            f"{self.protection_function} - "
            f"{function['name']}"
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

        main_layout.addWidget(
            header
        )

        # =================================================
        # DESCRIPTION
        # =================================================

        description = QLabel(
            function.get(
                "description",
                ""
            )
        )

        description.setWordWrap(
            True
        )

        description.setStyleSheet(
            """
            QLabel {
                color: #666666;
                padding-left: 8px;
                padding-bottom: 5px;
            }
            """
        )

        main_layout.addWidget(
            description
        )

        # =================================================
        # TEST TYPE
        # =================================================

        self.test_type = function.get(
            "test_type",
            "functional"
        )

        # =================================================
        # SCROLL AREA
        # =================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        container = QWidget()

        self.form_layout = QFormLayout(
            container
        )

        self.form_layout.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        self.form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )

        scroll.setWidget(
            container
        )

        main_layout.addWidget(
            scroll
        )

        # =================================================
        # CREATE TOLERANCE OBJECT FIRST
        #
        # Calculation functions connect to this widget.
        # Therefore it MUST EXIST before create_function_fields().
        # =================================================

        self.tolerance_group = QGroupBox(
            "Engineering Validation"
        )

        tolerance_layout = QFormLayout()

        self.tolerance_widget = QLineEdit()

        self.tolerance_widget.setText(
            str(DEFAULT_TOLERANCE)
        )

        self.tolerance_widget.setPlaceholderText(
            "Tolerance (%)"
        )

        tolerance_layout.addRow(
            "Tolerance (%)",
            self.tolerance_widget
        )

        self.tolerance_group.setLayout(
            tolerance_layout
        )

        # =================================================
        # CREATE PROTECTION-SPECIFIC FIELDS
        # =================================================

        self.create_function_fields()

        # =================================================
        # ENGINEERING VALIDATION
        #
        # Added AFTER protection-specific fields.
        # =================================================

        self.form_layout.addRow(
            self.tolerance_group
        )

        # =================================================
        # REMARKS
        # =================================================

        self.remarks_widget = QLineEdit()

        self.remarks_widget.setPlaceholderText(
            "Optional remarks"
        )

        self.form_layout.addRow(
            "Remarks",
            self.remarks_widget
        )

        # =================================================
        # RESULT
        # =================================================

        self.result_widget = QLineEdit()

        self.result_widget.setReadOnly(
            True
        )

        self.result_widget.setStyleSheet(
            """
            QLineEdit {
                font-weight: bold;
                padding: 5px;
            }
            """
        )

        self.form_layout.addRow(
            "Result",
            self.result_widget
        )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        self.clear_button = QPushButton(
            "Clear"
        )

        self.save_button = QPushButton(
            "Save Test"
        )

        buttons.addWidget(
            self.clear_button
        )

        buttons.addWidget(
            self.save_button
        )

        buttons.addStretch()

        main_layout.addLayout(
            buttons
        )

        # =================================================
        # SIGNALS
        # =================================================

        self.clear_button.clicked.connect(
            self.clear_fields
        )

        self.save_button.clicked.connect(
            self.save_test
        )

    # =====================================================
    # CREATE FUNCTION FIELDS
    # =====================================================

    def create_function_fields(self):

        test_type = self.test_type

        # =================================================
        # IDMT
        # =================================================

        if test_type == "idmt":

            self.add_number(
                "pickup_current",
                "Pickup Current",
                "A",
                True
            )

            self.add_number(
                "test_current",
                "Test Current",
                "A",
                True
            )

            self.add_curve()

            self.add_number(
                "tms",
                "TMS",
                "",
                True
            )

            self.add_readonly(
                "psm",
                "PSM"
            )

            self.add_readonly(
                "expected_time",
                "Expected Operating Time",
                "s"
            )

            self.add_number(
                "actual_time",
                "Actual Operating Time",
                "s",
                True
            )

            self.add_readonly(
                "error_percent",
                "Time Error",
                "%"
            )

            self.connect_idmt()

            return

        # =================================================
        # CURRENT PICKUP
        # =================================================

        if test_type == "current_pickup_time":

            self.add_number(
                "pickup_current",
                "Pickup Current Setting",
                "A",
                True
            )

            self.add_number(
                "test_current",
                "Measured Pickup Current",
                "A",
                True
            )

            self.add_readonly(
                "pickup_error_percent",
                "Pickup Error",
                "%"
            )

            self.connect_current_pickup()

            return

        # =================================================
        # VOLTAGE
        # =================================================

        if test_type == "voltage_threshold":

            self.add_number(
                "voltage_setting",
                "Voltage Setting",
                "V",
                True
            )

            self.add_number(
                "measured_voltage",
                "Measured Pickup Voltage",
                "V",
                True
            )

            self.add_readonly(
                "error_percent",
                "Voltage Error",
                "%"
            )

            self.connect_voltage_threshold()

            return

        # =================================================
        # FREQUENCY
        # =================================================

        if test_type == "frequency_threshold":

            self.add_number(
                "frequency_setting",
                "Frequency Setting",
                "Hz",
                True
            )

            self.add_number(
                "measured_frequency",
                "Measured Pickup Frequency",
                "Hz",
                True
            )

            self.add_readonly(
                "error_percent",
                "Frequency Error",
                "%"
            )

            self.connect_frequency()

            return

        # =================================================
        # ROCOF
        # =================================================

        if test_type == "rocof":

            self.add_number(
                "frequency_before",
                "Frequency Before",
                "Hz",
                True
            )

            self.add_number(
                "frequency_after",
                "Frequency After",
                "Hz",
                True
            )

            self.add_number(
                "time_interval",
                "Time Interval",
                "s",
                True
            )

            self.add_readonly(
                "calculated_rocof",
                "Calculated ROCOF",
                "Hz/s"
            )

            self.add_number(
                "rocof_setting",
                "ROCOF Setting",
                "Hz/s",
                True
            )

            self.add_readonly(
                "error_percent",
                "ROCOF Error",
                "%"
            )

            self.connect_rocof()

            return

        # =================================================
        # DIRECTIONAL
        # =================================================

        if test_type == "directional_current":

            self.add_number(
                "pickup_current",
                "Pickup Current",
                "A",
                True
            )

            self.add_number(
                "test_current",
                "Test Current",
                "A",
                True
            )

            self.add_number(
                "expected_angle",
                "Expected Direction Angle",
                "°",
                True
            )

            self.add_number(
                "actual_angle",
                "Measured Direction Angle",
                "°",
                True
            )

            self.add_readonly(
                "angle_error",
                "Angle Error",
                "°"
            )

            self.connect_directional()

            return

        # =================================================
        # FUNCTIONAL
        # =================================================

        if test_type == "functional":

            self.add_select(
                "expected_operation",
                "Expected Operation",
                [
                    "OPERATE",
                    "NO OPERATE"
                ],
                True
            )

            self.add_select(
                "observed_operation",
                "Observed Operation",
                [
                    "OPERATE",
                    "NO OPERATE"
                ],
                True
            )

            self.connect_functional()

            return

        # =================================================
        # DIFFERENTIAL
        # =================================================

        if test_type == "differential":

            self.add_number(
                "current_1",
                "Current Input 1",
                "A",
                True
            )

            self.add_number(
                "current_2",
                "Current Input 2",
                "A",
                True
            )

            self.add_readonly(
                "differential_current",
                "Differential Current",
                "A"
            )

            self.add_number(
                "expected_differential",
                "Expected Differential",
                "A",
                True
            )

            self.add_readonly(
                "error_percent",
                "Differential Error",
                "%"
            )

            self.connect_differential()

            return

        # =================================================
        # UNKNOWN
        # =================================================

        self.form_layout.addRow(
            QLabel(
                f"No testing template is defined "
                f"for test type: {test_type}"
            )
        )

    # =====================================================
    # FIELD HELPERS
    # =====================================================

    def add_number(
        self,
        field_id,
        label,
        unit="",
        required=False
    ):

        widget = QLineEdit()

        widget.setPlaceholderText(
            "Enter value"
        )

        self.fields[
            field_id
        ] = widget

        self.form_layout.addRow(
            self.make_label(
                label,
                unit,
                required
            ),
            widget
        )

    # =====================================================

    def add_readonly(
        self,
        field_id,
        label,
        unit=""
    ):

        widget = QLineEdit()

        widget.setReadOnly(
            True
        )

        self.fields[
            field_id
        ] = widget

        self.form_layout.addRow(
            self.make_label(
                label,
                unit,
                False
            ),
            widget
        )

    # =====================================================

    def add_select(
        self,
        field_id,
        label,
        options,
        required=False
    ):

        widget = QComboBox()

        widget.addItems(
            options
        )

        self.fields[
            field_id
        ] = widget

        self.form_layout.addRow(
            self.make_label(
                label,
                "",
                required
            ),
            widget
        )

    # =====================================================

    def add_curve(self):

        widget = QComboBox()

        try:

            curves = get_curves(
                "51"
            )

        except Exception:

            curves = {}

        if curves:

            for curve_code in curves.keys():

                widget.addItem(
                    str(curve_code)
                )

        else:

            widget.addItems(
                [
                    "IEC Normal Inverse",
                    "IEC Very Inverse",
                    "IEC Extremely Inverse",
                    "IEC Long Time Inverse",
                ]
            )

        self.fields[
            "curve"
        ] = widget

        self.form_layout.addRow(
            self.make_label(
                "Curve",
                "",
                True
            ),
            widget
        )

    # =====================================================

    def make_label(
        self,
        label,
        unit,
        required
    ):

        text = str(label)

        if unit:
            text += f" ({unit})"

        if required:
            text += " *"

        return QLabel(
            text
        )

    # =====================================================
    # IDMT
    # =====================================================

    def connect_idmt(self):

        for field_id in [
            "pickup_current",
            "test_current",
            "tms"
        ]:

            self.fields[
                field_id
            ].textChanged.connect(
                self.calculate_idmt
            )

        self.fields[
            "curve"
        ].currentTextChanged.connect(
            self.calculate_idmt
        )

        self.fields[
            "actual_time"
        ].textChanged.connect(
            self.calculate_idmt_result
        )

        self.tolerance_widget.textChanged.connect(
            self.calculate_idmt_result
        )

    # =====================================================

    def calculate_idmt(self):

        try:

            calculation = (
                ProtectionCalculator
                .calculate_51_time(
                    curve_code=self.fields[
                        "curve"
                    ].currentText(),

                    pickup_current=float(
                        self.fields[
                            "pickup_current"
                        ].text()
                    ),

                    test_current=float(
                        self.fields[
                            "test_current"
                        ].text()
                    ),

                    tms=float(
                        self.fields[
                            "tms"
                        ].text()
                    )
                )
            )

            self.fields[
                "psm"
            ].setText(
                f"{calculation['psm']:.3f}"
            )

            self.fields[
                "expected_time"
            ].setText(
                f"{calculation['expected_time']:.4f}"
            )

            self.calculate_idmt_result()

        except (
            ValueError,
            TypeError,
            ZeroDivisionError
        ):

            self.fields[
                "psm"
            ].clear()

            self.fields[
                "expected_time"
            ].clear()

            self.fields[
                "error_percent"
            ].clear()

            self.result_widget.clear()

    # =====================================================

    def calculate_idmt_result(self):

        try:

            expected_time = float(
                self.fields[
                    "expected_time"
                ].text()
            )

            actual_time = float(
                self.fields[
                    "actual_time"
                ].text()
            )

            tolerance = float(
                self.tolerance_widget.text()
            )

            result = (
                ProtectionCalculator
                .evaluate_time_test(
                    expected_time=expected_time,
                    actual_time=actual_time,
                    tolerance_percent=tolerance
                )
            )

            self.fields[
                "error_percent"
            ].setText(
                f"{result['error_percent']:.2f}"
            )

            self.result_widget.setText(
                result["result"]
            )

        except (
            ValueError,
            TypeError,
            ZeroDivisionError
        ):

            self.fields[
                "error_percent"
            ].clear()

            self.result_widget.clear()

    # =====================================================
    # CURRENT PICKUP
    # =====================================================

    def connect_current_pickup(self):

        self.fields[
            "test_current"
        ].textChanged.connect(
            self.calculate_current_pickup
        )

        self.fields[
            "pickup_current"
        ].textChanged.connect(
            self.calculate_current_pickup
        )

        self.tolerance_widget.textChanged.connect(
            self.calculate_current_pickup
        )

    # =====================================================

    def calculate_current_pickup(self):

        try:

            result = (
                ProtectionCalculator
                .evaluate_current_pickup(
                    expected_current=float(
                        self.fields[
                            "pickup_current"
                        ].text()
                    ),

                    actual_current=float(
                        self.fields[
                            "test_current"
                        ].text()
                    ),

                    tolerance_percent=float(
                        self.tolerance_widget.text()
                    )
                )
            )

            self.fields[
                "pickup_error_percent"
            ].setText(
                f"{result['error_percent']:.2f}"
            )

            self.result_widget.setText(
                result["result"]
            )

        except (
            ValueError,
            TypeError,
            ZeroDivisionError
        ):

            self.fields[
                "pickup_error_percent"
            ].clear()

            self.result_widget.clear()

    # =====================================================
    # VOLTAGE
    # =====================================================

    def connect_voltage_threshold(self):

        for field_id in [
            "voltage_setting",
            "measured_voltage"
        ]:

            self.fields[
                field_id
            ].textChanged.connect(
                self.calculate_voltage
            )

        self.tolerance_widget.textChanged.connect(
            self.calculate_voltage
        )

    # =====================================================

    def calculate_voltage(self):

        try:

            direction = (
                "lower"
                if self.protection_function == "27"
                else "upper"
            )

            result = (
                ProtectionCalculator
                .evaluate_threshold(
                    expected_value=float(
                        self.fields[
                            "voltage_setting"
                        ].text()
                    ),

                    actual_value=float(
                        self.fields[
                            "measured_voltage"
                        ].text()
                    ),

                    tolerance_percent=float(
                        self.tolerance_widget.text()
                    ),

                    direction=direction
                )
            )

            self.fields[
                "error_percent"
            ].setText(
                f"{result['error_percent']:.2f}"
            )

            self.result_widget.setText(
                result["result"]
            )

        except (
            ValueError,
            TypeError,
            ZeroDivisionError
        ):

            self.fields[
                "error_percent"
            ].clear()

            self.result_widget.clear()

    # =====================================================
    # FREQUENCY
    # =====================================================

    def connect_frequency(self):

        for field_id in [
            "frequency_setting",
            "measured_frequency"
        ]:

            self.fields[
                field_id
            ].textChanged.connect(
                self.calculate_frequency
            )

        self.tolerance_widget.textChanged.connect(
            self.calculate_frequency
        )

    # =====================================================

    def calculate_frequency(self):

        try:

            result = (
                ProtectionCalculator
                .evaluate_frequency_pickup(
                    expected_frequency=float(
                        self.fields[
                            "frequency_setting"
                        ].text()
                    ),

                    actual_frequency=float(
                        self.fields[
                            "measured_frequency"
                        ].text()
                    ),

                    tolerance_percent=float(
                        self.tolerance_widget.text()
                    )
                )
            )

            self.fields[
                "error_percent"
            ].setText(
                f"{result['error_percent']:.2f}"
            )

            self.result_widget.setText(
                result["result"]
            )

        except (
            ValueError,
            TypeError,
            ZeroDivisionError
        ):

            self.fields[
                "error_percent"
            ].clear()

            self.result_widget.clear()

    # =====================================================
    # ROCOF
    # =====================================================

    def connect_rocof(self):

        for field_id in [
            "frequency_before",
            "frequency_after",
            "time_interval",
            "rocof_setting"
        ]:

            self.fields[
                field_id
            ].textChanged.connect(
                self.calculate_rocof
            )

        self.tolerance_widget.textChanged.connect(
            self.calculate_rocof
        )

    # =====================================================

    def calculate_rocof(self):

        try:

            rocof = (
                ProtectionCalculator
                .calculate_rocof(
                    frequency_1=float(
                        self.fields[
                            "frequency_before"
                        ].text()
                    ),

                    frequency_2=float(
                        self.fields[
                            "frequency_after"
                        ].text()
                    ),

                    time_interval=float(
                        self.fields[
                            "time_interval"
                        ].text()
                    )
                )
            )

            self.fields[
                "calculated_rocof"
            ].setText(
                f"{rocof:.4f}"
            )

            result = (
                ProtectionCalculator
                .evaluate_rocof(
                    expected_rocof=float(
                        self.fields[
                            "rocof_setting"
                        ].text()
                    ),

                    actual_rocof=rocof,

                    tolerance_percent=float(
                        self.tolerance_widget.text()
                    )
                )
            )

            self.fields[
                "error_percent"
            ].setText(
                f"{result['error_percent']:.2f}"
            )

            self.result_widget.setText(
                result["result"]
            )

        except (
            ValueError,
            TypeError,
            ZeroDivisionError
        ):

            self.fields[
                "calculated_rocof"
            ].clear()

            self.fields[
                "error_percent"
            ].clear()

            self.result_widget.clear()

    # =====================================================
    # DIRECTIONAL
    # =====================================================

    def connect_directional(self):

        for field_id in [
            "expected_angle",
            "actual_angle"
        ]:

            self.fields[
                field_id
            ].textChanged.connect(
                self.calculate_directional
            )

        self.tolerance_widget.textChanged.connect(
            self.calculate_directional
        )

    # =====================================================

    def calculate_directional(self):

        try:

            result = (
                ProtectionCalculator
                .evaluate_directional_test(
                    expected_angle=float(
                        self.fields[
                            "expected_angle"
                        ].text()
                    ),

                    actual_angle=float(
                        self.fields[
                            "actual_angle"
                        ].text()
                    ),

                    angle_tolerance=float(
                        self.tolerance_widget.text()
                    )
                )
            )

            self.fields[
                "angle_error"
            ].setText(
                f"{result['angle_error']:.2f}"
            )

            self.result_widget.setText(
                result["result"]
            )

        except (
            ValueError,
            TypeError
        ):

            self.fields[
                "angle_error"
            ].clear()

            self.result_widget.clear()

    # =====================================================
    # FUNCTIONAL
    # =====================================================

    def connect_functional(self):

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

    # =====================================================

    def calculate_functional(self):

        expected = (
            self.fields[
                "expected_operation"
            ].currentText()
        )

        observed = (
            self.fields[
                "observed_operation"
            ].currentText()
        )

        result = (
            ProtectionCalculator
            .evaluate_boolean_test(
                expected,
                observed
            )
        )

        self.result_widget.setText(
            result["result"]
        )

    # =====================================================
    # DIFFERENTIAL
    # =====================================================

    def connect_differential(self):

        for field_id in [
            "current_1",
            "current_2",
            "expected_differential"
        ]:

            self.fields[
                field_id
            ].textChanged.connect(
                self.calculate_differential
            )

        self.tolerance_widget.textChanged.connect(
            self.calculate_differential
        )

    # =====================================================

    def calculate_differential(self):

        try:

            differential = (
                ProtectionCalculator
                .calculate_differential_current(
                    current_1=float(
                        self.fields[
                            "current_1"
                        ].text()
                    ),

                    current_2=float(
                        self.fields[
                            "current_2"
                        ].text()
                    )
                )
            )

            self.fields[
                "differential_current"
            ].setText(
                f"{differential:.4f}"
            )

            result = (
                ProtectionCalculator
                .evaluate_differential_test(
                    expected_current=float(
                        self.fields[
                            "expected_differential"
                        ].text()
                    ),

                    actual_differential_current=differential,

                    tolerance_percent=float(
                        self.tolerance_widget.text()
                    )
                )
            )

            self.fields[
                "error_percent"
            ].setText(
                f"{result['error_percent']:.2f}"
            )

            self.result_widget.setText(
                result["result"]
            )

        except (
            ValueError,
            TypeError,
            ZeroDivisionError
        ):

            self.fields[
                "differential_current"
            ].clear()

            self.fields[
                "error_percent"
            ].clear()

            self.result_widget.clear()

    # =====================================================
    # GET FIELD VALUES
    # =====================================================

    def get_field_values(self):

        values = {}

        for field_id, widget in self.fields.items():

            if isinstance(
                widget,
                QLineEdit
            ):

                values[
                    field_id
                ] = widget.text().strip()

            elif isinstance(
                widget,
                QComboBox
            ):

                values[
                    field_id
                ] = widget.currentText()

        values[
            "tolerance_percent"
        ] = self.tolerance_widget.text().strip()

        values[
            "remarks"
        ] = self.remarks_widget.text().strip()

        values[
            "result"
        ] = self.result_widget.text().strip()

        return values

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate_fields(self, values):

        required_fields = []

        if self.test_type == "idmt":

            required_fields = [
                "pickup_current",
                "test_current",
                "tms",
                "actual_time"
            ]

        elif self.test_type == "current_pickup_time":

            required_fields = [
                "pickup_current",
                "test_current"
            ]

        elif self.test_type == "voltage_threshold":

            required_fields = [
                "voltage_setting",
                "measured_voltage"
            ]

        elif self.test_type == "frequency_threshold":

            required_fields = [
                "frequency_setting",
                "measured_frequency"
            ]

        elif self.test_type == "rocof":

            required_fields = [
                "frequency_before",
                "frequency_after",
                "time_interval",
                "rocof_setting"
            ]

        elif self.test_type == "directional_current":

            required_fields = [
                "pickup_current",
                "test_current",
                "expected_angle",
                "actual_angle"
            ]

        elif self.test_type == "functional":

            required_fields = [
                "expected_operation",
                "observed_operation"
            ]

        elif self.test_type == "differential":

            required_fields = [
                "current_1",
                "current_2",
                "expected_differential"
            ]

        # =================================================
        # REQUIRED FIELDS
        # =================================================

        for field_id in required_fields:

            value = str(
                values.get(
                    field_id,
                    ""
                )
            ).strip()

            if not value:

                QMessageBox.warning(
                    self,
                    "Required Field",
                    (
                        "Please enter: "
                        +
                        field_id.replace(
                            "_",
                            " "
                        ).title()
                    )
                )

                return False

        # =================================================
        # TOLERANCE
        # =================================================

        try:

            tolerance = float(
                values[
                    "tolerance_percent"
                ]
            )

            if tolerance < 0:
                raise ValueError

        except (
            ValueError,
            TypeError,
            KeyError
        ):

            QMessageBox.warning(
                self,
                "Invalid Tolerance",
                (
                    "Tolerance must be a valid "
                    "non-negative number."
                )
            )

            return False

        return True

    # =====================================================
    # SAVE
    # =====================================================

    def save_test(self):

        values = self.get_field_values()

        if not self.validate_fields(
            values
        ):
            return

        result = (
            values.get(
                "result",
                ""
            )
            or
            "NOT TESTED"
        )

        if self.test_service is None:

            QMessageBox.warning(
                self,
                "Save Failed",
                "Test service is not available."
            )

            return

        try:

            test_id = (
                self.test_service
                .save_protection_test(
                    project_id=self.project_id,
                    panel_id=self.panel_id,
                    relay_id=self.relay_id,
                    protection_code=self.protection_function,
                    settings={},
                    measurements=values,
                    result=result,
                    remarks=values.get(
                        "remarks",
                        ""
                    )
                )
            )

            QMessageBox.information(
                self,
                "Test Saved",
                (
                    "Test result saved successfully.\n\n"
                    f"Test ID: {test_id}"
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error)
            )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear_fields(self):

        for widget in self.fields.values():

            if isinstance(
                widget,
                QLineEdit
            ):

                widget.clear()

            elif isinstance(
                widget,
                QComboBox
            ):

                widget.setCurrentIndex(
                    0
                )

        self.tolerance_widget.setText(
            str(DEFAULT_TOLERANCE)
        )

        self.remarks_widget.clear()

        self.result_widget.clear()