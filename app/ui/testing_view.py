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
from app.ui.thermal_testing_dialog import (
    ThermalTestingDialog
)

DEFAULT_TOLERANCE = 5.0


class TestingView(QWidget):
    """
    Protection testing view.

    Current-based protection quantities are entered as
    multiples of relay nominal current:

        xIn

    where:

        In = selected CT secondary current.

    Example:

        CT = 1000/5

        In = 5 A

        1.20 xIn
        =
        1.20 × 5
        =
        6 A

    The ProtectionCalculator performs protection calculations
    in xIn for current-based protection functions.

    Therefore:

        Tester input
                ↓
             xIn
                ↓
       ProtectionCalculator
                ↓
      engineering result

    CT secondary current is used only to display the
    corresponding physical secondary injection current.
    """

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        project_id,
        panel_id,
        relay_id,
        protection_function,
        test_service,
        component=None,
        ct_component=None,
        parent=None
    ):

        super().__init__(
            parent
        )

        # =================================================
        # IDENTIFICATION
        # =================================================

        self.project_id = (
            project_id
        )

        self.panel_id = (
            panel_id
        )

        self.relay_id = (
            relay_id
        )

        self.test_service = (
            test_service
        )

        # =================================================
        # NUMERICAL RELAY
        #
        # component = relay being tested
        # =================================================

        self.component = (
            component
        )

        # =================================================
        # SELECTED CT
        #
        # ct_component = CT selected by tester in
        # RelayTestingDialog.
        # =================================================

        self.ct_component = (
            ct_component
        )

        # =================================================
        # CT SECONDARY = RELAY NOMINAL CURRENT In
        # =================================================

        self.nominal_current = (
            self.get_ct_nominal_current(
                self.ct_component
            )
        )

        # =================================================
        # PROTECTION FUNCTION
        # =================================================

        self.protection_function = (
            normalize_protection_code(
                protection_function
            )
        )

        # =================================================
        # TEST DATA
        # =================================================

        self.fields = {}

        self.test_type = (
            "functional"
        )

        # =================================================
        # UI
        # =================================================

        self.setObjectName(
            "TestingView"
        )

        self.setMinimumWidth(
            650
        )

        # =================================================
        # BUILD
        # =================================================

        self.build_ui()

    # =====================================================
    # CT NOMINAL CURRENT
    # =====================================================

    @staticmethod
    def get_ct_nominal_current(
        ct_component
    ):
        """
        Return CT secondary current.

        This is the relay nominal current In.

        Examples:

            1000/5 -> 5 A
            1000/1 -> 1 A
        """

        if ct_component is None:

            return 0.0

        # -------------------------------------------------
        # Preferred:
        # explicit CT secondary
        # -------------------------------------------------

        try:

            secondary = float(
                getattr(
                    ct_component,
                    "ct_secondary",
                    0
                )
                or 0
            )

            if secondary > 0:

                return secondary

        except (
            TypeError,
            ValueError
        ):

            pass

        # -------------------------------------------------
        # Backward compatibility:
        #
        # ct_ratio = "1000/5"
        # ct_ratio = "1000/1"
        # -------------------------------------------------

        ratio = str(
            getattr(
                ct_component,
                "ct_ratio",
                ""
            )
            or ""
        ).strip()

        if "/" in ratio:

            try:

                secondary = float(
                    ratio.split(
                        "/",
                        1
                    )[1].strip()
                )

                if secondary > 0:

                    return secondary

            except (
                TypeError,
                ValueError,
                IndexError
            ):

                pass

        return 0.0

    # =====================================================
    # CT PRIMARY
    # =====================================================

    def get_ct_primary(
        self
    ):
        """
        Return selected CT primary current.
        """

        if self.ct_component is None:

            return 0.0

        try:

            return float(
                getattr(
                    self.ct_component,
                    "ct_primary",
                    0
                )
                or 0
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0

    # =====================================================
    # CT RATIO
    # =====================================================

    def get_current_ct_ratio(
        self
    ):
        """
        Return selected CT ratio.

        Example:

            1000/5
            1000/1
        """

        if self.ct_component is None:

            return ""

        primary = (
            self.get_ct_primary()
        )

        secondary = (
            self.nominal_current
        )

        if (
            primary > 0
            and secondary > 0
        ):

            return (
                f"{primary:g}/"
                f"{secondary:g}"
            )

        return str(
            getattr(
                self.ct_component,
                "ct_ratio",
                ""
            )
            or ""
        ).strip()

    # =====================================================
    # xIn -> AMPS
    # =====================================================

    def xin_to_amps(
        self,
        value
    ):
        """
        Convert xIn to actual CT secondary current.

            I = xIn × In

        Example:

            CT = 1000/5
            In = 5 A

            1.2 xIn = 6 A
        """

        if self.nominal_current <= 0:

            raise ValueError(
                "No CT has been selected or the selected "
                "CT secondary current is not configured."
            )

        return (
            float(value)
            *
            self.nominal_current
        )

    # =====================================================
    # AMPS -> xIn
    # =====================================================

    def amps_to_xin(
        self,
        value
    ):
        """
        Convert actual CT secondary current to xIn.
        """

        if self.nominal_current <= 0:

            raise ValueError(
                "No CT has been selected or the selected "
                "CT secondary current is not configured."
            )

        return (
            float(value)
            /
            self.nominal_current
        )

    # =====================================================
    # CURRENT BASED TEST
    # =====================================================

    def is_current_based_test(
        self
    ):

        return self.test_type in (
            "idmt",
            "current_pickup_time",
            "directional_current",
            "differential",
        )

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(
        self
    ):

        main_layout = QVBoxLayout(
            self
        )

        # =================================================
        # GET FUNCTION
        # =================================================

        function = (
            get_protection_function(
                self.protection_function
            )
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

        self.test_type = (
            function.get(
                "test_type",
                "functional"
            )
        )

        # =================================================
        # CT INFORMATION
        # =================================================

        if self.is_current_based_test():

            self.create_ct_information(
                main_layout
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
        # ENGINEERING VALIDATION
        #
        # IMPORTANT:
        # This is created BEFORE create_function_fields().
        # =================================================

        self.tolerance_group = QGroupBox(
            "Engineering Validation"
        )

        tolerance_layout = QFormLayout()

        self.tolerance_widget = QLineEdit()

        self.tolerance_widget.setText(
            str(
                DEFAULT_TOLERANCE
            )
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
        # CREATE FUNCTION FIELDS
        # =================================================

        self.create_function_fields()

        # =================================================
        # ADD TOLERANCE
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
    # CREATE CT INFORMATION
    # =====================================================

    def create_ct_information(
        self,
        main_layout
    ):

        ct_group = QGroupBox(
            "Relay Current Reference"
        )

        ct_layout = QFormLayout()

        # -------------------------------------------------
        # CT NAME
        # -------------------------------------------------

        self.ct_name_display = QLineEdit()

        self.ct_name_display.setReadOnly(
            True
        )

        ct_name = ""

        if self.ct_component is not None:

            ct_name = str(
                getattr(
                    self.ct_component,
                    "name",
                    ""
                )
                or ""
            )

        self.ct_name_display.setText(
            ct_name
            or
            "No CT selected"
        )

        ct_layout.addRow(
            "Selected CT",
            self.ct_name_display
        )

        # -------------------------------------------------
        # CT RATIO
        # -------------------------------------------------

        self.ct_ratio_display = QLineEdit()

        self.ct_ratio_display.setReadOnly(
            True
        )

        self.ct_ratio_display.setText(
            self.get_current_ct_ratio()
            or
            "NOT CONFIGURED"
        )

        ct_layout.addRow(
            "CT Ratio",
            self.ct_ratio_display
        )

        # -------------------------------------------------
        # NOMINAL CURRENT
        # -------------------------------------------------

        self.nominal_current_display = QLineEdit()

        self.nominal_current_display.setReadOnly(
            True
        )

        if self.nominal_current > 0:

            nominal_text = (
                f"{self.nominal_current:g} A"
            )

        else:

            nominal_text = (
                "NOT CONFIGURED"
            )

        self.nominal_current_display.setText(
            nominal_text
        )

        ct_layout.addRow(
            "Nominal Current (In)",
            self.nominal_current_display
        )

        # -------------------------------------------------
        # WARNING
        # -------------------------------------------------

        if self.nominal_current <= 0:

            warning = QLabel(
                "WARNING: No valid CT secondary current "
                "has been configured for this relay test."
            )

            warning.setWordWrap(
                True
            )

            warning.setStyleSheet(
                """
                QLabel {
                    font-weight: bold;
                    padding: 6px;
                }
                """
            )

            ct_layout.addRow(
                warning
            )

        ct_group.setLayout(
            ct_layout
        )

        main_layout.addWidget(
            ct_group
        )

    # =====================================================
    # CREATE FUNCTION FIELDS
    # =====================================================

    def create_function_fields(
        self
    ):

        test_type = (
            self.test_type
        )

        # =================================================
        # IDMT / 51
        # =================================================

        if test_type == "idmt":

            self.add_number(
                "pickup_current",
                "Pickup Current",
                "xIn",
                True
            )

            self.add_number(
                "test_current",
                "Test Current",
                "xIn",
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
                "pickup_current_a",
                "Pickup Current",
                "A"
            )

            self.add_readonly(
                "test_current_a",
                "Test Current",
                "A"
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
        # CURRENT PICKUP / 50 / 50N / 51N
        # =================================================

        if test_type == "current_pickup_time":

            self.add_number(
                "pickup_current",
                "Pickup Current Setting",
                "xIn",
                True
            )

            self.add_number(
                "test_current",
                "Measured Pickup Current",
                "xIn",
                True
            )

            self.add_readonly(
                "pickup_current_a",
                "Pickup Setting",
                "A"
            )

            self.add_readonly(
                "test_current_a",
                "Measured Pickup",
                "A"
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
                "xIn",
                True
            )

            self.add_number(
                "test_current",
                "Test Current",
                "xIn",
                True
            )

            self.add_readonly(
                "pickup_current_a",
                "Pickup Current",
                "A"
            )

            self.add_readonly(
                "test_current_a",
                "Test Current",
                "A"
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
                "xIn",
                True
            )

            self.add_number(
                "current_2",
                "Current Input 2",
                "xIn",
                True
            )

            self.add_readonly(
                "current_1_a",
                "Current Input 1",
                "A"
            )

            self.add_readonly(
                "current_2_a",
                "Current Input 2",
                "A"
            )

            self.add_readonly(
                "differential_current",
                "Differential Current",
                "xIn"
            )

            self.add_readonly(
                "differential_current_a",
                "Differential Current",
                "A"
            )

            self.add_number(
                "expected_differential",
                "Expected Differential",
                "xIn",
                True
            )

            self.add_readonly(
                "expected_differential_a",
                "Expected Differential",
                "A"
            )

            self.add_readonly(
                "error_percent",
                "Differential Error",
                "%"
            )

            self.connect_differential()

            return
        if self.test_type == "thermal":

            self.create_thermal_fields()

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

    def add_curve(
        self
    ):

        widget = QComboBox()

        try:

            curves = get_curves(
                "51"
            )

        except Exception:

            curves = {}

        if curves:

            for curve_code in (
                curves.keys()
            ):

                widget.addItem(
                    str(
                        curve_code
                    )
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

    def make_label(
        self,
        label,
        unit,
        required
    ):

        text = str(
            label
        )

        if unit:

            text += (
                f" ({unit})"
            )

        if required:

            text += " *"

        return QLabel(
            text
        )

    # =====================================================
    # IDMT SIGNALS
    # =====================================================

    def connect_idmt(
        self
    ):

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
    # IDMT CALCULATION
    # =====================================================

    def calculate_idmt(
        self
    ):

        try:

            pickup_xin = float(
                self.fields[
                    "pickup_current"
                ].text()
            )

            test_xin = float(
                self.fields[
                    "test_current"
                ].text()
            )

            pickup_a = (
                self.xin_to_amps(
                    pickup_xin
                )
            )

            test_a = (
                self.xin_to_amps(
                    test_xin
                )
            )

            # -------------------------------------------------
            # Display actual current
            # -------------------------------------------------

            self.fields[
                "pickup_current_a"
            ].setText(
                f"{pickup_a:.4f}"
            )

            self.fields[
                "test_current_a"
            ].setText(
                f"{test_a:.4f}"
            )

            # -------------------------------------------------
            # Calculator
            # -------------------------------------------------

            calculation = (
                ProtectionCalculator
                .calculate_51_time(

                    curve_code=(
                        self.fields[
                            "curve"
                        ].currentText()
                    ),

                    pickup_xin=(
                        pickup_xin
                    ),

                    test_xin=(
                        test_xin
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
                "pickup_current_a"
            ].clear()

            self.fields[
                "test_current_a"
            ].clear()

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
    # IDMT RESULT
    # =====================================================

    def calculate_idmt_result(
        self
    ):

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

                    expected_time=(
                        expected_time
                    ),

                    actual_time=(
                        actual_time
                    ),

                    tolerance_percent=(
                        tolerance
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
    # CURRENT PICKUP SIGNALS
    # =====================================================

    def connect_current_pickup(
        self
    ):

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
    # CURRENT PICKUP CALCULATION
    # =====================================================

    def calculate_current_pickup(
        self
    ):

        try:

            pickup_xin = float(
                self.fields[
                    "pickup_current"
                ].text()
            )

            test_xin = float(
                self.fields[
                    "test_current"
                ].text()
            )

            pickup_a = (
                self.xin_to_amps(
                    pickup_xin
                )
            )

            test_a = (
                self.xin_to_amps(
                    test_xin
                )
            )

            # -------------------------------------------------
            # Display actual current
            # -------------------------------------------------

            self.fields[
                "pickup_current_a"
            ].setText(
                f"{pickup_a:.4f}"
            )

            self.fields[
                "test_current_a"
            ].setText(
                f"{test_a:.4f}"
            )

            tolerance = float(
                self.tolerance_widget.text()
            )

            result = (
                ProtectionCalculator
                .evaluate_current_pickup(

                    expected_xin=(
                        pickup_xin
                    ),

                    actual_xin=(
                        test_xin
                    ),

                    tolerance_percent=(
                        tolerance
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
                "pickup_current_a"
            ].clear()

            self.fields[
                "test_current_a"
            ].clear()

            self.fields[
                "pickup_error_percent"
            ].clear()

            self.result_widget.clear()

    # =====================================================
    # VOLTAGE SIGNALS
    # =====================================================

    def connect_voltage_threshold(
        self
    ):

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
    # VOLTAGE
    # =====================================================

    def calculate_voltage(
        self
    ):

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
    # FREQUENCY SIGNALS
    # =====================================================

    def connect_frequency(
        self
    ):

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
    # FREQUENCY
    # =====================================================

    def calculate_frequency(
        self
    ):

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
    # ROCOF SIGNALS
    # =====================================================

    def connect_rocof(
        self
    ):

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
    # ROCOF
    # =====================================================

    def calculate_rocof(
        self
    ):

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
    # DIRECTIONAL SIGNALS
    # =====================================================

    def connect_directional(
        self
    ):

        for field_id in [
            "pickup_current",
            "test_current",
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
    # DIRECTIONAL
    # =====================================================

    def calculate_directional(
        self
    ):

        try:

            pickup_xin = float(
                self.fields[
                    "pickup_current"
                ].text()
            )

            test_xin = float(
                self.fields[
                    "test_current"
                ].text()
            )

            pickup_a = (
                self.xin_to_amps(
                    pickup_xin
                )
            )

            test_a = (
                self.xin_to_amps(
                    test_xin
                )
            )

            self.fields[
                "pickup_current_a"
            ].setText(
                f"{pickup_a:.4f}"
            )

            self.fields[
                "test_current_a"
            ].setText(
                f"{test_a:.4f}"
            )

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
            TypeError,
            ZeroDivisionError
        ):

            self.fields[
                "pickup_current_a"
            ].clear()

            self.fields[
                "test_current_a"
            ].clear()

            self.fields[
                "angle_error"
            ].clear()

            self.result_widget.clear()

    # =====================================================
    # FUNCTIONAL SIGNALS
    # =====================================================

    def connect_functional(
        self
    ):

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
    # FUNCTIONAL
    # =====================================================

    def calculate_functional(
        self
    ):

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
    # DIFFERENTIAL SIGNALS
    # =====================================================

    def connect_differential(
        self
    ):

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
    # DIFFERENTIAL
    # =====================================================

    def calculate_differential(
        self
    ):

        try:

            current_1_xin = float(
                self.fields[
                    "current_1"
                ].text()
            )

            current_2_xin = float(
                self.fields[
                    "current_2"
                ].text()
            )

            expected_xin = float(
                self.fields[
                    "expected_differential"
                ].text()
            )

            current_1_a = (
                self.xin_to_amps(
                    current_1_xin
                )
            )

            current_2_a = (
                self.xin_to_amps(
                    current_2_xin
                )
            )

            expected_a = (
                self.xin_to_amps(
                    expected_xin
                )
            )

            # -------------------------------------------------
            # Display actual currents
            # -------------------------------------------------

            self.fields[
                "current_1_a"
            ].setText(
                f"{current_1_a:.4f}"
            )

            self.fields[
                "current_2_a"
            ].setText(
                f"{current_2_a:.4f}"
            )

            # -------------------------------------------------
            # Calculate differential current
            # -------------------------------------------------

            differential_xin = (
                ProtectionCalculator
                .calculate_differential_current(

                    current_1_xin=(
                        current_1_xin
                    ),

                    current_2_xin=(
                        current_2_xin
                    )
                )
            )

            differential_a = (
                self.xin_to_amps(
                    differential_xin
                )
            )

            self.fields[
                "differential_current"
            ].setText(
                f"{differential_xin:.4f}"
            )

            self.fields[
                "differential_current_a"
            ].setText(
                f"{differential_a:.4f}"
            )

            self.fields[
                "expected_differential_a"
            ].setText(
                f"{expected_a:.4f}"
            )

            # -------------------------------------------------
            # Evaluate
            # -------------------------------------------------

            result = (
                ProtectionCalculator
                .evaluate_differential_test(

                    expected_xin=(
                        expected_xin
                    ),

                    actual_differential_xin=(
                        differential_xin
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
                "current_1_a"
            ].clear()

            self.fields[
                "current_2_a"
            ].clear()

            self.fields[
                "differential_current"
            ].clear()

            self.fields[
                "differential_current_a"
            ].clear()

            self.fields[
                "expected_differential_a"
            ].clear()

            self.fields[
                "error_percent"
            ].clear()

            self.result_widget.clear()

    # =====================================================
    # GET FIELD VALUES
    # =====================================================

    def get_field_values(
        self
    ):

        values = {}

        # -------------------------------------------------
        # Normal fields
        # -------------------------------------------------

        for field_id, widget in (
            self.fields.items()
        ):

            if isinstance(
                widget,
                QLineEdit
            ):

                values[
                    field_id
                ] = (
                    widget
                    .text()
                    .strip()
                )

            elif isinstance(
                widget,
                QComboBox
            ):

                values[
                    field_id
                ] = (
                    widget
                    .currentText()
                )

        # -------------------------------------------------
        # Engineering validation
        # -------------------------------------------------

        values[
            "tolerance_percent"
        ] = (
            self.tolerance_widget
            .text()
            .strip()
        )

        # -------------------------------------------------
        # Remarks
        # -------------------------------------------------

        values[
            "remarks"
        ] = (
            self.remarks_widget
            .text()
            .strip()
        )

        # -------------------------------------------------
        # Result
        # -------------------------------------------------

        values[
            "result"
        ] = (
            self.result_widget
            .text()
            .strip()
        )

        # -------------------------------------------------
        # Nominal current
        # -------------------------------------------------

        values[
            "nominal_current_a"
        ] = self.nominal_current

        values[
            "nominal_current_unit"
        ] = "A"

        # -------------------------------------------------
        # CT information
        # -------------------------------------------------

        if self.ct_component is not None:

            values[
                "ct_id"
            ] = getattr(
                self.ct_component,
                "component_id",
                ""
            )

            values[
                "ct_name"
            ] = getattr(
                self.ct_component,
                "name",
                ""
            )

            values[
                "ct_primary_a"
            ] = self.get_ct_primary()

            values[
                "ct_secondary_a"
            ] = self.nominal_current

            values[
                "ct_ratio"
            ] = self.get_current_ct_ratio()

        else:

            values[
                "ct_id"
            ] = ""

            values[
                "ct_name"
            ] = ""

            values[
                "ct_primary_a"
            ] = 0

            values[
                "ct_secondary_a"
            ] = self.nominal_current

            values[
                "ct_ratio"
            ] = ""

        return values

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate_fields(
        self,
        values
    ):

        required_fields = []

        # =================================================
        # REQUIRED FIELDS BY TEST TYPE
        # =================================================

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
        # REQUIRED VALUE CHECK
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
                        field_id
                        .replace(
                            "_",
                            " "
                        )
                        .title()
                    )
                )

                return False

        # =================================================
        # CT CHECK
        # =================================================

        if (
            self.is_current_based_test()
            and self.nominal_current <= 0
        ):

            QMessageBox.warning(
                self,
                "CT Configuration Missing",
                (
                    "No valid CT secondary current has "
                    "been configured for this test.\n\n"
                    "Select a CT with a valid secondary "
                    "current such as 1 A or 5 A."
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
    # SAVE TEST
    # =====================================================

    def save_test(
        self
    ):

        values = (
            self.get_field_values()
        )

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

        # =================================================
        # SETTINGS
        # =================================================

        settings = {

            "nominal_current_a":
                self.nominal_current,

            "nominal_current_unit":
                "A",

            "input_current_unit":
                (
                    "xIn"
                    if self.is_current_based_test()
                    else ""
                ),

            "ct_id":
                values.get(
                    "ct_id",
                    ""
                ),

            "ct_name":
                values.get(
                    "ct_name",
                    ""
                ),

            "ct_primary_a":
                values.get(
                    "ct_primary_a",
                    0
                ),

            "ct_secondary_a":
                values.get(
                    "ct_secondary_a",
                    self.nominal_current
                ),

            "ct_ratio":
                values.get(
                    "ct_ratio",
                    ""
                ),
        }

        # =================================================
        # SAVE
        # =================================================

        try:

            test_id = (
                self.test_service
                .save_protection_test(

                    project_id=(
                        self.project_id
                    ),

                    panel_id=(
                        self.panel_id
                    ),

                    relay_id=(
                        self.relay_id
                    ),

                    protection_code=(
                        self.protection_function
                    ),

                    settings=settings,

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
                    "Protection test saved "
                    "successfully.\n\n"
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

    def clear_fields(
        self
    ):

        for widget in (
            self.fields.values()
        ):

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
            str(
                DEFAULT_TOLERANCE
            )
        )

        self.remarks_widget.clear()

        self.result_widget.clear()

    # =====================================================
    # CHANGE CT CONTEXT
    # =====================================================

    def set_ct_context(
        self,
        ct_component
    ):
        """
        Called by RelayTestingDialog when the tester
        selects a different CT.

        Existing xIn entries are preserved.

        Only their actual ampere equivalents and
        calculations are refreshed.
        """

        self.ct_component = (
            ct_component
        )

        self.nominal_current = (
            self.get_ct_nominal_current(
                ct_component
            )
        )

        self.update_ct_display()

        self.recalculate_current_fields()

    # =====================================================
    # UPDATE CT DISPLAY
    # =====================================================

    def update_ct_display(
        self
    ):

        if hasattr(
            self,
            "ct_name_display"
        ):

            if self.ct_component is not None:

                self.ct_name_display.setText(
                    str(
                        getattr(
                            self.ct_component,
                            "name",
                            ""
                        )
                        or
                        "Unnamed CT"
                    )
                )

            else:

                self.ct_name_display.setText(
                    "No CT selected"
                )

        if hasattr(
            self,
            "ct_ratio_display"
        ):

            self.ct_ratio_display.setText(
                self.get_current_ct_ratio()
                or
                "NOT CONFIGURED"
            )

        if hasattr(
            self,
            "nominal_current_display"
        ):

            if self.nominal_current > 0:

                self.nominal_current_display.setText(
                    f"{self.nominal_current:g} A"
                )

            else:

                self.nominal_current_display.setText(
                    "NOT CONFIGURED"
                )

    # =====================================================
    # RECALCULATE CURRENT FIELDS
    # =====================================================

    def recalculate_current_fields(
        self
    ):
        """
        Recalculate all current-dependent calculations
        after changing the selected CT.

        User-entered values remain in xIn.
        """

        try:

            if self.test_type == "idmt":

                self.calculate_idmt()

            elif self.test_type == "current_pickup_time":

                self.calculate_current_pickup()

            elif self.test_type == "directional_current":

                self.calculate_directional()

            elif self.test_type == "differential":

                self.calculate_differential()

        except Exception:

            # Do not crash the GUI merely because a
            # field is incomplete while switching CTs.
            pass

    def create_thermal_fields(self):

        self.add_readonly(
            "thermal_info",
            "Thermal Testing"
        )

        self.add_number(
            "test_current",
            "Test Current",
            "xIn",
            True
        )

        self.add_number(
            "actual_time",
            "Actual Operating Time",
            "s",
            True
        )

        self.add_readonly(
            "expected_time",
            "Expected Operating Time",
            "s"
        )

        self.add_readonly(
            "error",
            "Error",
            "%"
        )