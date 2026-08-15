from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QLabel,
)

from app.ui.test_detail_view import TestDetailView
from app.ui.aux_relay_test_detail_view import (
    AuxRelayTestDetailView
)


class TestHistoryView(QDialog):

    def __init__(
        self,
        test_service,
        project_id,
        panel_id,
        project_folder=None,
        parent=None
    ):

        super().__init__(parent)

        self.test_service = test_service
        self.project_id = project_id
        self.panel_id = panel_id
        self.project_folder = project_folder

        self.setWindowTitle("Test History")
        self.resize(1100, 650)

        self.build_ui()
        self.load_tests()

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        header = QLabel("Test History")
        header.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
            }
            """
        )
        layout.addWidget(header)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "Test ID",
                "Date",
                "Test Type",
                "Protection / Component",
                "Test / Function",
                "Result",
                "Remarks",
            ]
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setAlternatingRowColors(True)

        self.table.cellDoubleClicked.connect(
            self.open_test_detail
        )

        layout.addWidget(self.table)

        buttons = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.edit_button = QPushButton("View / Edit Test")
        self.close_button = QPushButton("Close")

        self.refresh_button.clicked.connect(
            self.load_tests
        )
        self.edit_button.clicked.connect(
            self.open_selected_test
        )
        self.close_button.clicked.connect(
            self.accept
        )

        buttons.addWidget(self.refresh_button)
        buttons.addWidget(self.edit_button)
        buttons.addStretch()
        buttons.addWidget(self.close_button)

        layout.addLayout(buttons)

    # =====================================================
    # LOAD
    # =====================================================

    def load_tests(self):

        self.table.setRowCount(0)

        try:

            protection_tests = (
                self.test_service.get_all_tests()
            )

            component_tests = (
                self.test_service
                .get_all_component_tests()
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                str(error)
            )
            return

        history = []

        # -------------------------------------------------
        # PROTECTION TESTS
        # -------------------------------------------------

        for row in protection_tests:

            if row[1] != self.project_id:
                continue

            if row[2] != self.panel_id:
                continue

            history.append({
                "test_id": row[0],
                "date": row[5],
                "test_type": "PROTECTION",
                "component": row[3],
                "test": row[4],
                "result": row[6],
                "remarks": row[7],
                "record_type": "PROTECTION",
            })

        # -------------------------------------------------
        # COMPONENT TESTS
        # -------------------------------------------------

        for row in component_tests:

            if row[1] != self.project_id:
                continue

            if row[2] != self.panel_id:
                continue

            test_id = row[0]
            test_type = str(row[4] or "").upper()

            # Get full record so METER functions can be
            # represented as individual history rows.
            try:
                record = (
                    self.test_service
                    .get_component_test(test_id)
                )
            except Exception:
                record = None

            component_id = row[3]
            result = row[7]
            remarks = row[8]

            if test_type == "METER" and record:

                measurements = (
                    record.get("measurements", {})
                    or {}
                )

                functions = (
                    measurements.get("functions", [])
                    or []
                )

                if functions:

                    for function in functions:

                        if not isinstance(function, dict):
                            continue

                        measurement = str(
                            function.get(
                                "measurement",
                                ""
                            )
                        )

                        history.append({
                            "test_id": test_id,
                            "date": row[5],
                            "test_type": "METER",
                            "component": component_id,
                            "test": measurement,
                            "result": function.get(
                                "result",
                                result
                            ),
                            "remarks": remarks,
                            "record_type": "METER",
                        })

                    continue

            # CT / AUX / any other component test
            history.append({
                "test_id": test_id,
                "date": row[5],
                "test_type": test_type,
                "component": component_id,
                "test": test_type,
                "result": result,
                "remarks": remarks,
                "record_type": "COMPONENT",
            })

        history.sort(
            key=lambda item: str(
                item.get("date", "")
            ),
            reverse=True
        )

        for record in history:

            row = self.table.rowCount()
            self.table.insertRow(row)

            values = [
                record.get("test_id", ""),
                record.get("date", ""),
                record.get("test_type", ""),
                record.get("component", ""),
                record.get("test", ""),
                record.get("result", ""),
                record.get("remarks", ""),
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

    # =====================================================
    # SELECTED TEST
    # =====================================================

    def get_selected_test_id(self):

        row = self.table.currentRow()

        if row < 0:
            return None

        item = self.table.item(row, 0)

        if item is None:
            return None

        value = item.text().strip()

        return value or None

    # =====================================================
    # OPEN
    # =====================================================

    def open_selected_test(self):

        test_id = self.get_selected_test_id()

        if not test_id:

            QMessageBox.warning(
                self,
                "No Test Selected",
                "Select a test first."
            )
            return

        self.show_test_detail(test_id)

    def open_test_detail(
        self,
        row,
        column
    ):

        item = self.table.item(row, 0)

        if item is None:
            return

        test_id = item.text().strip()

        if test_id:
            self.show_test_detail(test_id)

    # =====================================================
    # DETAIL ROUTING
    # =====================================================

    def show_test_detail(self, test_id):

        # Protection test
        try:
            protection_record = (
                self.test_service.get_test(test_id)
            )
        except Exception:
            protection_record = None

        if protection_record is not None:

            self.test_detail_view = TestDetailView(
                test_service=self.test_service,
                test_id=test_id,
                project_folder=self.project_folder,
                parent=self
            )

            self.test_detail_view.exec()
            self.load_tests()
            return

        # Component test
        try:
            component_record = (
                self.test_service
                .get_component_test(test_id)
            )
        except Exception:
            component_record = None

        if component_record is None:

            QMessageBox.warning(
                self,
                "Test Not Found",
                f"Unable to find test record:\n\n{test_id}"
            )
            return

        self.show_component_test_detail(
            component_record
        )

    # =====================================================
    # COMPONENT DETAIL ROUTING
    # =====================================================

    def show_component_test_detail(self, record):

        test_type = str(
            record.get("test_type", "")
        ).strip().upper()

        if test_type == "CT":

            try:

                from app.ui.ct_test_detail_view import (
                    CTTestDetailView
                )

                self.component_test_detail_view = (
                    CTTestDetailView(
                        test_service=self.test_service,
                        test_id=record.get("test_id"),
                        project_folder=self.project_folder,
                        parent=self
                    )
                )

                self.component_test_detail_view.exec()
                self.load_tests()
                return

            except Exception as error:

                QMessageBox.critical(
                    self,
                    "CT Test Detail Error",
                    str(error)
                )
                return

        if test_type == "AUX_RELAY":

            try:

                self.component_test_detail_view = (
                    AuxRelayTestDetailView(
                        test_service=self.test_service,
                        test_id=record.get("test_id"),
                        project_folder=self.project_folder,
                        parent=self
                    )
                )

                self.component_test_detail_view.exec()
                self.load_tests()
                return

            except Exception as error:

                QMessageBox.critical(
                    self,
                    "Auxiliary Relay Detail Error",
                    str(error)
                )
                return

        if test_type == "METER":

            try:

                from app.ui.meter_test_detail_view import (
                    MeterTestDetailView
                )

                self.component_test_detail_view = (
                    MeterTestDetailView(
                        test_service=self.test_service,
                        test_id=record.get("test_id"),
                        project_folder=self.project_folder,
                        parent=self
                    )
                )

                self.component_test_detail_view.exec()
                self.load_tests()
                return

            except Exception as error:

                QMessageBox.critical(
                    self,
                    "Meter Test Detail Error",
                    str(error)
                )
                return

        # Existing generic fallback

        self.component_test_detail_view = TestDetailView(
            test_service=self.test_service,
            test_id=record.get("test_id"),
            project_folder=self.project_folder,
            parent=self
        )

        self.component_test_detail_view.exec()
        self.load_tests()
