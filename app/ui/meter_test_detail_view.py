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
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)


class MeterTestEditDialog(QDialog):

    def __init__(
        self,
        test_service,
        record,
        parent=None
    ):

        super().__init__(parent)

        self.test_service = test_service
        self.record = record

        self.setWindowTitle(
            f"Edit Meter Test - "
            f"{record.get('test_id', '')}"
        )

        self.resize(850, 600)

        self.function_widgets = []

        self.build_ui()
        self.populate()

    # =====================================================
    # BUILD
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        header = QLabel(
            "Edit Meter Test"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(header)

        info = QGroupBox(
            "Test Information"
        )

        form = QFormLayout()

        self.meter_type = QLineEdit()
        self.meter_type.setReadOnly(True)

        self.test_date = QLineEdit()
        self.test_date.setReadOnly(True)

        form.addRow(
            "Meter Type",
            self.meter_type
        )

        form.addRow(
            "Test Date",
            self.test_date
        )

        info.setLayout(form)

        layout.addWidget(info)

        self.table = QTableWidget()

        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels(
            [
                "Function",
                "Applied",
                "Reading",
                "Tolerance %",
                "Error %",
                "Result",
            ]
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        layout.addWidget(self.table)

        buttons = QHBoxLayout()

        save_button = QPushButton(
            "Save Changes"
        )

        cancel_button = QPushButton(
            "Cancel"
        )

        save_button.clicked.connect(
            self.save
        )

        cancel_button.clicked.connect(
            self.reject
        )

        buttons.addWidget(save_button)
        buttons.addStretch()
        buttons.addWidget(cancel_button)

        layout.addLayout(buttons)

    # =====================================================
    # POPULATE
    # =====================================================

    def populate(self):

        measurements = (
            self.record.get(
                "measurements",
                {}
            )
            or {}
        )

        self.meter_type.setText(
            str(
                measurements.get(
                    "meter_type",
                    ""
                )
            )
        )

        self.test_date.setText(
            str(
                self.record.get(
                    "test_date",
                    ""
                )
            )
        )

        functions = (
            measurements.get(
                "functions",
                []
            )
            or []
        )

        self.table.setRowCount(
            len(functions)
        )

        self.function_widgets.clear()

        for row, function in enumerate(functions):

            if not isinstance(function, dict):
                continue

            function_name = str(
                function.get(
                    "measurement",
                    ""
                )
            )

            applied = self.make_spinbox(
                function.get(
                    "applied_value",
                    0
                )
            )

            reading = self.make_spinbox(
                function.get(
                    "meter_reading",
                    0
                )
            )

            tolerance = self.make_spinbox(
                function.get(
                    "tolerance_percent",
                    0.5
                )
            )

            error = QLineEdit()
            error.setReadOnly(True)

            result = QLineEdit()
            result.setReadOnly(True)

            self.table.setCellWidget(
                row, 0,
                QLineEdit(function_name)
            )

            function_widget = (
                self.table.cellWidget(row, 0)
            )
            function_widget.setReadOnly(True)

            self.table.setCellWidget(
                row, 1, applied
            )

            self.table.setCellWidget(
                row, 2, reading
            )

            self.table.setCellWidget(
                row, 3, tolerance
            )

            self.table.setCellWidget(
                row, 4, error
            )

            self.table.setCellWidget(
                row, 5, result
            )

            entry = {
                "measurement": function_name,
                "applied": applied,
                "reading": reading,
                "tolerance": tolerance,
                "error": error,
                "result": result,
            }

            self.function_widgets.append(entry)

            applied.valueChanged.connect(
                lambda value,
                e=entry: self.calculate(e)
            )

            reading.valueChanged.connect(
                lambda value,
                e=entry: self.calculate(e)
            )

            tolerance.valueChanged.connect(
                lambda value,
                e=entry: self.calculate(e)
            )

            self.calculate(entry)

    # =====================================================
    # SPINBOX
    # =====================================================

    @staticmethod
    def make_spinbox(value):

        widget = QDoubleSpinBox()

        widget.setDecimals(6)
        widget.setRange(
            -100000000,
            100000000
        )

        try:
            widget.setValue(
                float(value or 0)
            )
        except (
            TypeError,
            ValueError
        ):
            widget.setValue(0)

        return widget

    # =====================================================
    # CALCULATION
    # =====================================================

    @staticmethod
    def calculate(entry):

        applied = entry["applied"].value()
        reading = entry["reading"].value()
        tolerance = entry["tolerance"].value()

        if applied == 0:

            entry["error"].clear()
            entry["result"].clear()

            return

        error = (
            (reading - applied)
            /
            applied
        ) * 100.0

        entry["error"].setText(
            f"{error:.4f}"
        )

        entry["result"].setText(
            "PASS"
            if abs(error) <= tolerance
            else "FAIL"
        )

    # =====================================================
    # SAVE
    # =====================================================

    def save(self):

        functions = []

        overall = "PASS"

        for entry in self.function_widgets:

            applied = entry["applied"].value()
            reading = entry["reading"].value()
            tolerance = entry["tolerance"].value()

            if applied == 0:

                continue

            error = (
                (reading - applied)
                /
                applied
            ) * 100.0

            result = (
                "PASS"
                if abs(error) <= tolerance
                else "FAIL"
            )

            if result == "FAIL":
                overall = "FAIL"

            functions.append({
                "measurement": (
                    entry["measurement"]
                ),
                "applied_value": applied,
                "meter_reading": reading,
                "error_percent": round(
                    error,
                    6
                ),
                "tolerance_percent": tolerance,
                "result": result,
            })

        if not functions:

            QMessageBox.warning(
                self,
                "No Test Data",
                "At least one valid measurement is required."
            )

            return

        measurements = dict(
            self.record.get(
                "measurements",
                {}
            )
            or {}
        )

        measurements["functions"] = functions

        # -------------------------------------------------
        # Prefer a TestService update method if the project
        # has one. Otherwise update the known SQLite table
        # through the existing TestService database object.
        # -------------------------------------------------

        try:

            update_method = getattr(
                self.test_service,
                "update_component_test",
                None
            )

            if callable(update_method):

                update_method(
                    test_id=self.record["test_id"],
                    measurements=measurements,
                    result=overall,
                    remarks=self.record.get(
                        "remarks",
                        ""
                    )
                )

            else:

                database = getattr(
                    self.test_service,
                    "database",
                    None
                )

                if database is None:

                    raise RuntimeError(
                        "TestService does not expose a database "
                        "or update_component_test() method."
                    )

                import json

                database.execute(
                    """
                    UPDATE component_tests
                    SET
                        measurements_json = ?,
                        result = ?,
                        remarks = ?
                    WHERE test_id = ?
                    """,
                    (
                        json.dumps(
                            measurements
                        ),
                        overall,
                        self.record.get(
                            "remarks",
                            ""
                        ),
                        self.record["test_id"],
                    )
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error)
            )

            return

        self.accept()


class MeterTestDetailView(QDialog):

    def __init__(
        self,
        test_service,
        test_id,
        project_folder=None,
        parent=None
    ):

        super().__init__(parent)

        self.test_service = test_service
        self.test_id = test_id
        self.project_folder = project_folder
        self.record = None

        self.setWindowTitle(
            f"Meter Test Details - {test_id}"
        )

        self.resize(900, 650)

        self.build_ui()
        self.load_test()

    # =====================================================
    # BUILD
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        self.header = QLabel(
            "Meter Test Details"
        )

        self.header.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )

        layout.addWidget(self.header)

        self.table = QTableWidget()

        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels(
            [
                "Function",
                "Applied",
                "Reading",
                "Tolerance %",
                "Error %",
                "Result",
            ]
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.table)

        buttons = QHBoxLayout()

        self.edit_button = QPushButton(
            "Edit Test"
        )

        self.close_button = QPushButton(
            "Close"
        )

        self.edit_button.clicked.connect(
            self.edit_test
        )

        self.close_button.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            self.edit_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.close_button
        )

        layout.addLayout(buttons)

    # =====================================================
    # LOAD
    # =====================================================

    def load_test(self):

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

            return

        if self.record is None:

            QMessageBox.warning(
                self,
                "Not Found",
                f"Meter test '{self.test_id}' could not be found."
            )

            return

        self.render()

    # =====================================================
    # RENDER
    # =====================================================

    def render(self):

        measurements = (
            self.record.get(
                "measurements",
                {}
            )
            or {}
        )

        self.table.setRowCount(0)

        functions = (
            measurements.get(
                "functions",
                []
            )
            or []
        )

        for function in functions:

            if not isinstance(function, dict):
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)

            values = [
                function.get("measurement", ""),
                function.get("applied_value", ""),
                function.get("meter_reading", ""),
                function.get("tolerance_percent", ""),
                function.get("error_percent", ""),
                function.get("result", ""),
            ]

            for column, value in enumerate(values):

                self.table.setItem(
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

        self.table.resizeColumnsToContents()

        self.header.setText(
            (
                f"Meter Test Details - "
                f"{self.test_id} | "
                f"{measurements.get('meter_type', '')}"
            )
        )

    # =====================================================
    # EDIT
    # =====================================================

    def edit_test(self):

        dialog = MeterTestEditDialog(
            test_service=self.test_service,
            record=self.record,
            parent=self
        )

        if (
            dialog.exec()
            == QDialog.DialogCode.Accepted
        ):

            self.load_test()
