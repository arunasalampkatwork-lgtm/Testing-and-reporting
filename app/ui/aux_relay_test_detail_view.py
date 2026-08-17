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
)

from app.ui.aux_relay_testing_dialog import (
    AuxRelayTestingDialog
)

from app.services.aux_relay_report_service import (
    AuxRelayReportService
)


class AuxRelayTestDetailView(QDialog):

    def __init__(
        self,
        test_service,
        test_id,
        project_folder=None,
        parent=None,
    ):

        super().__init__(
            parent
        )

        self.test_service = (
            test_service
        )

        self.test_id = (
            test_id
        )

        self.project_folder = (
            project_folder
        )

        self.record = None

        self.setWindowTitle(
            f"Auxiliary Relay Test - {test_id}"
        )

        self.resize(
            950,
            750
        )

        self.load_test()

    # =====================================================
    # LOAD
    # =====================================================

    def load_test(
        self
    ):

        try:

            self.record = (
                self.test_service
                .get_component_test(
                    self.test_id
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                str(error)
            )

            self.reject()

            return

        if self.record is None:

            QMessageBox.warning(
                self,
                "Test Not Found",
                f"Test '{self.test_id}' was not found."
            )

            self.reject()

            return

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(
        self
    ):

        layout = QVBoxLayout(
            self
        )

        header = QLabel(
            "AUXILIARY RELAY TEST DETAILS"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 21px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )

        layout.addWidget(
            header
        )

        result = self.record.get(
            "result",
            ""
        )

        result_label = QLabel(
            f"Overall Result: {result}"
        )

        result_label.setStyleSheet(
            """
            QLabel {
                font-size: 17px;
                font-weight: bold;
                padding: 6px;
            }
            """
        )

        layout.addWidget(
            result_label
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        container = QDialog()

        container_layout = QVBoxLayout(
            container
        )

        measurements = (
            self.record.get(
                "measurements",
                {}
            )
            or
            {}
        )

        self.add_information(
            container_layout
        )

        self.add_measurements(
            container_layout,
            measurements
        )

        container_layout.addStretch()

        scroll.setWidget(
            container
        )

        layout.addWidget(
            scroll
        )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        edit_button = QPushButton(
            "Edit Test"
        )

        report_button = QPushButton(
            "Generate Report"
        )

        close_button = QPushButton(
            "Close"
        )

        edit_button.clicked.connect(
            self.edit_test
        )

        report_button.clicked.connect(
            self.generate_report
        )

        close_button.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            edit_button
        )

        buttons.addWidget(
            report_button
        )

        buttons.addStretch()

        buttons.addWidget(
            close_button
        )

        layout.addLayout(
            buttons
        )

    # =====================================================
    # TEST INFORMATION
    # =====================================================

    def add_information(
        self,
        layout
    ):

        group = QGroupBox(
            "Test Information"
        )

        form = QFormLayout(
            group
        )

        self.add_row(
            form,
            "Test ID",
            self.record.get(
                "test_id"
            )
        )

        self.add_row(
            form,
            "Test Type",
            self.record.get(
                "test_type"
            )
        )

        self.add_row(
            form,
            "Date",
            self.record.get(
                "test_date"
            )
        )

        self.add_row(
            form,
            "Project",
            self.record.get(
                "project_id"
            )
        )

        self.add_row(
            form,
            "Panel",
            self.record.get(
                "panel_id"
            )
        )

        self.add_row(
            form,
            "Component",
            self.record.get(
                "component_id"
            )
        )

        layout.addWidget(
            group
        )

    # =====================================================
    # MEASUREMENTS
    # =====================================================

    def add_measurements(
        self,
        layout,
        measurements
    ):

        group = QGroupBox(
            "Test Measurements"
        )

        form = QFormLayout(
            group
        )

        preferred_order = [

            (
                "manufacturer",
                "Manufacturer"
            ),

            (
                "model",
                "Model"
            ),

            (
                "serial_number",
                "Serial Number"
            ),

            (
                "coil_voltage",
                "Configured Coil Voltage"
            ),

            (
                "contact_configuration",
                "Contact Configuration"
            ),

            (
                "rated_voltage",
                "Rated Coil Voltage (V)"
            ),

            (
                "pickup_voltage",
                "Measured Pickup Voltage (V)"
            ),

            (
                "pickup_voltage_percent",
                "Pickup Voltage (%)"
            ),

            (
                "dropout_voltage",
                "Measured Dropout Voltage (V)"
            ),

            (
                "dropout_voltage_percent",
                "Dropout Voltage (%)"
            ),

            (
                "expected_pickup_time",
                "Expected Pickup Time (s)"
            ),

            (
                "pickup_time",
                "Measured Pickup Time (s)"
            ),

            (
                "pickup_time_error",
                "Pickup Time Error (%)"
            ),

            (
                "expected_dropout_time",
                "Expected Dropout Time (s)"
            ),

            (
                "dropout_time",
                "Measured Dropout Time (s)"
            ),

            (
                "dropout_time_error",
                "Dropout Time Error (%)"
            ),

            (
                "expected_operation",
                "Expected Operation"
            ),

            (
                "observed_operation",
                "Observed Operation"
            ),

            (
                "functional_result",
                "Functional Result"
            ),

            (
                "tolerance_percent",
                "Tolerance (%)"
            ),

        ]

        used = set()

        for key, label in preferred_order:

            if key not in measurements:

                continue

            self.add_row(
                form,
                label,
                measurements.get(
                    key
                )
            )

            used.add(
                key
            )

        # -------------------------------------------------
        # Future fields automatically appear
        # -------------------------------------------------

        for key, value in measurements.items():

            if key in used:

                continue

            if key in (
                "remarks",
                "result"
            ):

                continue

            self.add_row(
                form,
                key.replace(
                    "_",
                    " "
                ).title(),
                value
            )

        layout.addWidget(
            group
        )

        # -------------------------------------------------
        # REMARKS
        # -------------------------------------------------

        remarks_group = QGroupBox(
            "Remarks"
        )

        remarks_form = QFormLayout(
            remarks_group
        )

        self.add_row(
            remarks_form,
            "Remarks",
            self.record.get(
                "remarks",
                ""
            )
        )

        layout.addWidget(
            remarks_group
        )

    # =====================================================
    # ROW
    # =====================================================

    @staticmethod
    def add_row(
        form,
        label,
        value
    ):

        widget = QLineEdit()

        widget.setReadOnly(
            True
        )

        widget.setText(
            ""
            if value is None
            else str(value)
        )

        form.addRow(
            label,
            widget
        )

    # =====================================================
    # EDIT
    # =====================================================

    def edit_test(
        self
    ):

        dialog = (
            AuxRelayTestingDialog(

                project_id=(
                    self.record.get(
                        "project_id"
                    )
                ),

                panel_id=(
                    self.record.get(
                        "panel_id"
                    )
                ),

                component=None,

                test_service=(
                    self.test_service
                ),

                test_id=(
                    self.test_id
                ),

                existing_test=(
                    self.record
                ),

                parent=self
            )
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        self.record = (
            self.test_service
            .get_component_test(
                self.test_id
            )
        )

        # Rebuild.

        old_layout = (
            self.layout()
        )

        if old_layout:

            while old_layout.count():

                item = (
                    old_layout.takeAt(0)
                )

                widget = item.widget()

                if widget:

                    widget.deleteLater()

        self.build_ui()

    # =====================================================
    # REPORT
    # =====================================================

    def generate_report(
        self
    ):

        if not self.project_folder:

            QMessageBox.warning(
                self,
                "Project Folder Missing",
                "The current project folder is not available."
            )

            return

        try:

            service = (
                AuxRelayReportService(
                    self.project_folder
                )
            )

            service.generate_report(
                self.record,
                self
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Report Generation Failed",
                str(error)
            )