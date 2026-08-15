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
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from app.ui.ct_testing_dialog import (
    CTTestingDialog
)

from app.services.ct_report_service import (
    CTReportService
)


class CTTestDetailView(QDialog):

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
            f"CT Test Details - {test_id}"
        )

        self.resize(
            1100,
            800
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

        main_layout = QVBoxLayout(
            self
        )

        # =================================================
        # HEADER
        # =================================================

        header = QLabel(
            "CURRENT TRANSFORMER TEST DETAILS"
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

        main_layout.addWidget(
            header
        )

        result = (
            self.record.get(
                "result",
                ""
            )
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

        main_layout.addWidget(
            result_label
        )

        # =================================================
        # SCROLL
        # =================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        container = QDialog()

        container_layout = QVBoxLayout(
            container
        )

        self.add_test_information(
            container_layout
        )

        measurements = (
            self.record.get(
                "measurements",
                {}
            )
            or {}
        )

        self.add_ct_information(
            container_layout,
            measurements
        )

        self.add_ratio_results(
            container_layout,
            measurements
        )

        self.add_other_results(
            container_layout,
            measurements
        )

        self.add_remarks(
            container_layout
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

        buttons = QHBoxLayout()

        self.edit_button = QPushButton(
            "Edit Test"
        )

        self.report_button = QPushButton(
            "Generate Report"
        )

        self.close_button = QPushButton(
            "Close"
        )

        self.edit_button.clicked.connect(
            self.edit_test
        )

        self.report_button.clicked.connect(
            self.generate_report
        )

        self.close_button.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            self.edit_button
        )

        buttons.addWidget(
            self.report_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.close_button
        )

        main_layout.addLayout(
            buttons
        )

    # =====================================================
    # TEST INFORMATION
    # =====================================================

    def add_test_information(
        self,
        layout
    ):

        group = QGroupBox(
            "Test Information"
        )

        form = QFormLayout(
            group
        )

        self.add_info(
            form,
            "Test ID",
            self.record.get(
                "test_id"
            )
        )

        self.add_info(
            form,
            "Test Type",
            self.record.get(
                "test_type"
            )
        )

        self.add_info(
            form,
            "Test Date",
            self.record.get(
                "test_date"
            )
        )

        self.add_info(
            form,
            "Project ID",
            self.record.get(
                "project_id"
            )
        )

        self.add_info(
            form,
            "Panel ID",
            self.record.get(
                "panel_id"
            )
        )

        self.add_info(
            form,
            "Component ID",
            self.record.get(
                "component_id"
            )
        )

        layout.addWidget(
            group
        )

    # =====================================================
    # CT INFORMATION
    # =====================================================

    def add_ct_information(
        self,
        layout,
        values
    ):

        group = QGroupBox(
            "CT Information"
        )

        form = QFormLayout(
            group
        )

        fields = [

            (
                "CT",
                values.get(
                    "ct_name",
                    ""
                )
            ),

            (
                "Manufacturer",
                values.get(
                    "manufacturer",
                    ""
                )
            ),

            (
                "Model",
                values.get(
                    "model",
                    ""
                )
            ),

            (
                "Serial Number",
                values.get(
                    "serial_number",
                    ""
                )
            ),

            (
                "CT Primary",
                values.get(
                    "ct_primary",
                    ""
                )
            ),

            (
                "CT Secondary",
                values.get(
                    "ct_secondary",
                    ""
                )
            ),

            (
                "CT Ratio",
                values.get(
                    "ct_ratio",
                    ""
                )
            ),

            (
                "Core",
                values.get(
                    "core",
                    ""
                )
            ),

            (
                "CT Class",
                values.get(
                    "ct_class",
                    ""
                )
            ),

            (
                "Rated Burden",
                values.get(
                    "burden",
                    ""
                )
            ),

            (
                "3-Phase CT",
                "Yes"
                if values.get(
                    "is_three_phase",
                    False
                )
                else
                "No"
            ),
        ]

        for label, value in fields:

            self.add_info(
                form,
                label,
                value
            )

        layout.addWidget(
            group
        )

    # =====================================================
    # RATIO RESULTS
    # =====================================================

    def add_ratio_results(
        self,
        layout,
        values
    ):

        group = QGroupBox(
            "CT Ratio Test"
        )

        group_layout = QVBoxLayout(
            group
        )

        table = QTableWidget()

        table.setColumnCount(
            5
        )

        table.setHorizontalHeaderLabels(
            [
                "Phase",
                "Injected Primary (A)",
                "Recorded Secondary (A)",
                "Measured Ratio",
                "Ratio Error (%)",
            ]
        )

        table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        table.setAlternatingRowColors(
            True
        )

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        phase_tests = (
            values.get(
                "phase_tests",
                []
            )
            or []
        )

        # Legacy test compatibility.

        if not phase_tests:

            phase_tests = [

                {
                    "phase": "R",

                    "primary_current":
                        values.get(
                            "primary_current",
                            ""
                        ),

                    "secondary_current":
                        values.get(
                            "secondary_current",
                            ""
                        ),

                    "measured_ratio":
                        values.get(
                            "measured_ratio",
                            ""
                        ),

                    "ratio_error":
                        values.get(
                            "ratio_error",
                            ""
                        ),
                }
            ]

        for phase_data in phase_tests:

            row = (
                table.rowCount()
            )

            table.insertRow(
                row
            )

            values_list = [

                phase_data.get(
                    "phase",
                    ""
                ),

                phase_data.get(
                    "primary_current",
                    ""
                ),

                phase_data.get(
                    "secondary_current",
                    ""
                ),

                phase_data.get(
                    "measured_ratio",
                    ""
                ),

                phase_data.get(
                    "ratio_error",
                    ""
                ),
            ]

            for column, value in enumerate(
                values_list
            ):

                table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(
                            value
                            if value is not None
                            else ""
                        )
                    )
                )

        group_layout.addWidget(
            table
        )

        layout.addWidget(
            group
        )

    # =====================================================
    # OTHER RESULTS
    # =====================================================

    def add_other_results(
        self,
        layout,
        values
    ):

        group = QGroupBox(
            "Other Test Results"
        )

        form = QFormLayout(
            group
        )

        fields = [

            (
                "Expected Polarity",
                "expected_polarity"
            ),

            (
                "Observed Polarity",
                "observed_polarity"
            ),

            (
                "Polarity Result",
                "polarity_result"
            ),

            (
                "Primary-Earth IR",
                "ir_primary_earth"
            ),

            (
                "Secondary-Earth IR",
                "ir_secondary_earth"
            ),

            (
                "Primary-Secondary IR",
                "ir_primary_secondary"
            ),

            (
                "IR Test Voltage",
                "ir_test_voltage"
            ),

            (
                "IR Test Duration",
                "ir_test_duration"
            ),

            (
                "Winding Resistance - Phase A",
                "resistance_phase_a"
            ),

            (
                "Winding Resistance - Phase B",
                "resistance_phase_b"
            ),

            (
                "Winding Resistance - Phase C",
                "resistance_phase_c"
            ),

            (
                "Knee Point Voltage",
                "knee_point_voltage"
            ),

            (
                "Knee Point Current",
                "knee_point_current"
            ),

            (
                "Excitation Test Voltage",
                "excitation_test_voltage"
            ),

            (
                "Excitation Test Current",
                "excitation_test_current"
            ),

            (
                "Burden Test Current",
                "burden_test_current"
            ),

            (
                "Measured Burden",
                "measured_burden"
            ),

            (
                "Burden Error",
                "burden_error"
            ),

            (
                "Tolerance",
                "tolerance_percent"
            ),
        ]

        for label, key in fields:

            if key not in values:

                continue

            self.add_info(
                form,
                label,
                values.get(
                    key,
                    ""
                )
            )

        layout.addWidget(
            group
        )

    # =====================================================
    # REMARKS
    # =====================================================

    def add_remarks(
        self,
        layout
    ):

        group = QGroupBox(
            "Remarks"
        )

        form = QFormLayout(
            group
        )

        remarks = (
            self.record.get(
                "remarks",
                ""
            )
            or
            self.record.get(
                "measurements",
                {}
            ).get(
                "remarks",
                ""
            )
        )

        self.add_info(
            form,
            "Remarks",
            remarks
        )

        layout.addWidget(
            group
        )

    # =====================================================
    # INFO FIELD
    # =====================================================

    @staticmethod
    def add_info(
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

        dialog = CTTestingDialog(

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

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        # Reload the record after editing.

        self.record = (
            self.test_service
            .get_component_test(
                self.test_id
            )
        )

        # Rebuild the page.

        old_layout = self.layout()

        if old_layout is not None:

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

            service = CTReportService(
                project_folder=(
                    self.project_folder
                )
            )

            service.generate_report(
                record=self.record,
                parent=self
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Report Generation Failed",
                str(error)
            )