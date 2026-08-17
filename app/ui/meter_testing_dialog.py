from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QTabWidget,
    QWidget,
    QLabel,
    QDoubleSpinBox,
    QPushButton,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class MeterTestingDialog(QDialog):

    FUNCTION_INFO = {

        "VOLTAGE": {
            "label": "Voltage",
            "unit": "V",
        },

        "CURRENT": {
            "label": "Current",
            "unit": "A",
        },

        "FREQUENCY": {
            "label": "Frequency",
            "unit": "Hz",
        },

        "ACTIVE_POWER": {
            "label": "Active Power",
            "unit": "kW",
        },

        "REACTIVE_POWER": {
            "label": "Reactive Power",
            "unit": "kVAr",
        },

        "APPARENT_POWER": {
            "label": "Apparent Power",
            "unit": "kVA",
        },

        "POWER_FACTOR": {
            "label": "Power Factor",
            "unit": "",
        },
    }

    def __init__(
        self,
        project_id,
        panel_id,
        component,
        test_service,
        parent=None
    ):

        super().__init__(parent)

        self.project_id = project_id
        self.panel_id = panel_id
        self.component = component
        self.test_service = test_service

        self.function_widgets = {}

        self.setWindowTitle(
            f"Meter Testing - {component.name}"
        )

        self.resize(
            850,
            600
        )

        self.build_ui()

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        header = QLabel(
            f"{self.component.name} | "
            f"{getattr(self.component, 'meter_type', '')}"
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

        layout.addWidget(header)

        self.tabs = QTabWidget()

        functions = (
            getattr(
                self.component,
                "meter_functions",
                []
            )
            or []
        )

        if not functions:

            meter_type = getattr(
                self.component,
                "meter_type",
                ""
            )

            functions = self.default_functions(
                meter_type
            )

        for code in functions:

            if code not in self.FUNCTION_INFO:
                continue

            self.create_function_tab(
                code
            )

        layout.addWidget(
            self.tabs
        )

        buttons = QHBoxLayout()

        save_button = QPushButton(
            "Save Test"
        )

        close_button = QPushButton(
            "Close"
        )

        save_button.clicked.connect(
            self.save_test
        )

        close_button.clicked.connect(
            self.reject
        )

        buttons.addWidget(save_button)
        buttons.addStretch()
        buttons.addWidget(close_button)

        layout.addLayout(buttons)

    # =====================================================
    # DEFAULT FUNCTIONS
    # =====================================================

    @staticmethod
    def default_functions(
        meter_type
    ):

        value = str(
            meter_type or ""
        ).strip().upper()

        if value == "AMMETER":
            return ["CURRENT"]

        if value == "VOLTMETER":
            return ["VOLTAGE"]

        if value in (
            "MULTIFUNCTION METER",
            "MULTIFUNCTION_METER",
            "MULTIFUNCTION",
        ):

            return [
                "VOLTAGE",
                "CURRENT",
                "FREQUENCY",
                "ACTIVE_POWER",
                "REACTIVE_POWER",
                "APPARENT_POWER",
                "POWER_FACTOR",
            ]

        return []

    # =====================================================
    # FUNCTION TAB
    # =====================================================

    def create_function_tab(
        self,
        code
    ):

        info = self.FUNCTION_INFO[code]

        page = QWidget()
        layout = QVBoxLayout(page)

        form = QFormLayout()

        applied = QDoubleSpinBox()
        applied.setRange(
            -1000000,
            1000000
        )
        applied.setDecimals(6)
        applied.setValue(0)

        reading = QDoubleSpinBox()
        reading.setRange(
            -1000000,
            1000000
        )
        reading.setDecimals(6)
        reading.setValue(0)

        tolerance = QDoubleSpinBox()
        tolerance.setRange(
            0,
            100
        )
        tolerance.setDecimals(4)

        accuracy = self.parse_accuracy_class()

        if accuracy is not None:
            tolerance.setValue(accuracy)
        else:
            tolerance.setValue(0.5)

        error_label = QLabel(
            "Calculated error: --"
        )

        result_label = QLabel(
            "Result: NOT TESTED"
        )

        form.addRow(
            f"Applied {info['label']} ({info['unit']}):",
            applied
        )

        form.addRow(
            f"Meter Reading ({info['unit']}):",
            reading
        )

        form.addRow(
            "Permissible Error (%):",
            tolerance
        )

        form.addRow(
            "Calculated:",
            error_label
        )

        form.addRow(
            "Result:",
            result_label
        )

        layout.addLayout(form)
        layout.addStretch()

        applied.valueChanged.connect(
            lambda _:
                self.update_function_result(code)
        )

        reading.valueChanged.connect(
            lambda _:
                self.update_function_result(code)
        )

        tolerance.valueChanged.connect(
            lambda _:
                self.update_function_result(code)
        )

        self.function_widgets[code] = {

            "applied":
                applied,

            "reading":
                reading,

            "tolerance":
                tolerance,

            "error_label":
                error_label,

            "result_label":
                result_label,
        }

        self.tabs.addTab(
            page,
            info["label"]
        )

        self.update_function_result(
            code
        )

    # =====================================================
    # ACCURACY
    # =====================================================

    def parse_accuracy_class(self):

        value = str(
            getattr(
                self.component,
                "accuracy_class",
                ""
            )
            or ""
        ).strip()

        if not value:
            return None

        try:
            return float(value)
        except ValueError:
            return None

    # =====================================================
    # CALCULATION
    # =====================================================

    def update_function_result(
        self,
        code
    ):

        widgets = (
            self.function_widgets.get(
                code
            )
        )

        if widgets is None:
            return

        applied = widgets[
            "applied"
        ].value()

        reading = widgets[
            "reading"
        ].value()

        tolerance = widgets[
            "tolerance"
        ].value()

        if abs(applied) < 1e-12:

            widgets[
                "error_label"
            ].setText(
                "Calculated error: --"
            )

            widgets[
                "result_label"
            ].setText(
                "Result: NOT TESTED"
            )

            return

        error = (
            (
                reading -
                applied
            )
            /
            abs(applied)
        ) * 100

        passed = (
            abs(error)
            <= tolerance
        )

        widgets[
            "error_label"
        ].setText(
            f"Calculated error: {error:.4f} %"
        )

        widgets[
            "result_label"
        ].setText(
            "Result: PASS"
            if passed
            else
            "Result: FAIL"
        )

    # =====================================================
    # SAVE
    # =====================================================

    def save_test(self):

        functions = []

        overall = "PASS"

        for code, widgets in (
            self.function_widgets.items()
        ):

            applied = widgets[
                "applied"
            ].value()

            reading = widgets[
                "reading"
            ].value()

            tolerance = widgets[
                "tolerance"
            ].value()

            if abs(applied) < 1e-12:

                result = "NOT TESTED"
                error = None

            else:

                error = (
                    (
                        reading -
                        applied
                    )
                    /
                    abs(applied)
                ) * 100

                result = (
                    "PASS"
                    if abs(error) <= tolerance
                    else
                    "FAIL"
                )

            functions.append({

                "measurement":
                    code,

                "applied_value":
                    applied,

                "meter_reading":
                    reading,

                "tolerance_percent":
                    tolerance,

                "error_percent":
                    error,

                "result":
                    result,
            })

            if result == "FAIL":
                overall = "FAIL"

        if all(
            function["result"] == "NOT TESTED"
            for function in functions
        ):

            overall = "NOT TESTED"

        elif overall != "FAIL" and any(
            function["result"] == "NOT TESTED"
            for function in functions
        ):

            overall = "PARTIALLY TESTED"

        measurements = {

            "meter_type":
                getattr(
                    self.component,
                    "meter_type",
                    ""
                ),

            "accuracy_class":
                getattr(
                    self.component,
                    "accuracy_class",
                    ""
                ),

            "functions":
                functions,
        }

        try:

            test_id = (
                self.test_service
                .save_component_test(

                    project_id=self.project_id,

                    panel_id=self.panel_id,

                    component_id=(
                        self.component.component_id
                    ),

                    test_type="METER",

                    measurements=measurements,

                    result=overall,

                    remarks="",
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error)
            )

            return

        QMessageBox.information(
            self,
            "Test Saved",
            (
                f"Meter test saved successfully.\n\n"
                f"Test ID: {test_id}\n"
                f"Result: {overall}"
            )
        )

        self.accept()
