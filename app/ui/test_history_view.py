from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QLabel,
    QHeaderView,
    QTextEdit,
)
from app.ui.test_detail_view import TestDetailView

class TestHistoryView(QDialog):

    def __init__(
        self,
        test_service,
        project_id,
        panel_id,
        parent=None
    ):

        super().__init__(parent)

        self.test_service = (
            test_service
        )

        self.project_id = (
            project_id
        )

        self.panel_id = (
            panel_id
        )

        self.records = []

        self.setWindowTitle(
            "Test History"
        )

        self.resize(
            1100,
            650
        )

        self.build_ui()

        self.load_tests()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )

        # =================================================
        # HEADER
        # =================================================

        header = QLabel(
            "Test History"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            header
        )

        # =================================================
        # TABLE
        # =================================================

        self.table = QTableWidget()

        self.table.setColumnCount(
            7
        )

        self.table.setHorizontalHeaderLabels(
            [
                "Test ID",
                "Date",
                "Type",
                "Protection / Test",
                "Component / Relay",
                "Result",
                "Remarks",
            ]
        )

        self.table.setSelectionBehavior(
            QTableWidget
            .SelectionBehavior
            .SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget
            .SelectionMode
            .SingleSelection
        )

        self.table.setEditTriggers(
            QTableWidget
            .EditTrigger
            .NoEditTriggers
        )

        self.table.setAlternatingRowColors(
            True
        )

        self.table.setSortingEnabled(
            False
        )

        self.table.cellDoubleClicked.connect(
            self.open_test_detail
        )

        layout.addWidget(
            self.table
        )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        self.refresh_button = QPushButton(
            "Refresh"
        )

        self.detail_button = QPushButton(
            "View Details"
        )

        self.close_button = QPushButton(
            "Close"
        )

        self.detail_button.setEnabled(
            False
        )

        self.refresh_button.clicked.connect(
            self.load_tests
        )

        self.detail_button.clicked.connect(
            self.open_selected_detail
        )

        self.close_button.clicked.connect(
            self.accept
        )

        self.table.itemSelectionChanged.connect(
            self.update_buttons
        )

        buttons.addWidget(
            self.refresh_button
        )

        buttons.addWidget(
            self.detail_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.close_button
        )

        layout.addLayout(
            buttons
        )

    # =====================================================
    # LOAD TESTS
    # =====================================================

    def load_tests(self):

        self.table.setRowCount(
            0
        )

        self.records = []

        try:

            self.records = (
                self.test_service
                .get_panel_test_history(
                    self.project_id,
                    self.panel_id
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                str(error)
            )

            return

        # =================================================
        # POPULATE
        # =================================================

        for record in self.records:

            row = (
                self.table.rowCount()
            )

            self.table.insertRow(
                row
            )

            record_type = str(
                record.get(
                    "record_type",
                    ""
                )
            ).upper()

            # -------------------------------------------------
            # TEST ID
            # -------------------------------------------------

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(
                        record.get(
                            "test_id",
                            ""
                        )
                    )
                )
            )

            # -------------------------------------------------
            # DATE
            # -------------------------------------------------

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(
                        record.get(
                            "test_date",
                            ""
                        )
                    )
                )
            )

            # -------------------------------------------------
            # TYPE
            # -------------------------------------------------

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    (
                        "PROTECTION"
                        if record_type
                        == "PROTECTION"
                        else
                        "COMPONENT"
                    )
                )
            )

            # -------------------------------------------------
            # PROTECTION / TEST
            # -------------------------------------------------

            if record_type == "PROTECTION":

                test_name = str(
                    record.get(
                        "protection_code",
                        ""
                    )
                )

            else:

                test_name = str(
                    record.get(
                        "test_type",
                        ""
                    )
                )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    test_name
                )
            )

            # -------------------------------------------------
            # RELAY / COMPONENT
            # -------------------------------------------------

            if record_type == "PROTECTION":

                component_name = str(
                    record.get(
                        "relay_id",
                        ""
                    )
                )

            else:

                component_name = str(
                    record.get(
                        "component_id",
                        ""
                    )
                )

            self.table.setItem(
                row,
                4,
                QTableWidgetItem(
                    component_name
                )
            )

            # -------------------------------------------------
            # RESULT
            # -------------------------------------------------

            result_item = QTableWidgetItem(
                str(
                    record.get(
                        "result",
                        ""
                    )
                )
            )

            self.table.setItem(
                row,
                5,
                result_item
            )

            # -------------------------------------------------
            # REMARKS
            # -------------------------------------------------

            self.table.setItem(
                row,
                6,
                QTableWidgetItem(
                    str(
                        record.get(
                            "remarks",
                            ""
                        )
                    )
                )
            )

            # -------------------------------------------------
            # Store complete record in row
            # -------------------------------------------------

            self.table.item(
                row,
                0
            ).setData(
                Qt.ItemDataRole.UserRole,
                record
            )

        self.table.resizeColumnsToContents()

        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        self.update_buttons()

    # =====================================================
    # BUTTON STATE
    # =====================================================

    def update_buttons(self):

        self.detail_button.setEnabled(
            self.table.currentRow()
            >= 0
        )

    # =====================================================
    # GET SELECTED RECORD
    # =====================================================

    def get_selected_record(self):

        row = (
            self.table.currentRow()
        )

        if row < 0:

            return None

        item = self.table.item(
            row,
            0
        )

        if item is None:

            return None

        return item.data(
            Qt.ItemDataRole.UserRole
        )

    # =====================================================
    # OPEN SELECTED DETAIL
    # =====================================================

    def open_selected_detail(self):

        record = (
            self.get_selected_record()
        )

        if record is None:

            QMessageBox.warning(
                self,
                "No Test Selected",
                "Select a test first."
            )

            return

        self.show_test_detail(
            record
        )

    # =====================================================
    # DOUBLE CLICK
    # =====================================================

    def open_test_detail(
        self,
        row,
        column
    ):

        item = self.table.item(
            row,
            0
        )

        if item is None:

            return

        record = item.data(
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            record,
            dict
        ):

            return

        self.show_test_detail(
            record
        )

    # =====================================================
    # TEST DETAIL
    # =====================================================

    def show_test_detail(
        self,
        record
    ):

        if not isinstance(
            record,
            dict
        ):

            QMessageBox.warning(
                self,
                "Invalid Test",
                "The selected test record is invalid."
            )

            return

        record_type = str(
            record.get(
                "record_type",
                ""
            )
        ).upper()

        self.test_detail_view = TestDetailView(
            test_service=self.test_service,
            test_id=record.get(
                "test_id",
                ""
            ),
            record_type=record_type,
            parent=self
        )

        self.test_detail_view.exec()
# =========================================================
# TEST RECORD DETAIL DIALOG
# =========================================================

class TestRecordDetailDialog(QDialog):

    def __init__(
        self,
        record,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.record = (
            record or {}
        )

        self.setWindowTitle(
            "Test Details"
        )

        self.resize(
            750,
            600
        )

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )

        record = self.record

        record_type = str(
            record.get(
                "record_type",
                ""
            )
        )

        # =================================================
        # SUMMARY
        # =================================================

        summary = QLabel(
            self.build_summary()
        )

        summary.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                padding: 8px;
            }
            """
        )

        layout.addWidget(
            summary
        )

        # =================================================
        # SETTINGS
        # =================================================

        if record_type == "PROTECTION":

            settings = record.get(
                "settings",
                {}
            )

        else:

            settings = {}

        measurements = record.get(
            "measurements",
            {}
        )

        # =================================================
        # DETAILS TEXT
        # =================================================

        details = QTextEdit()

        details.setReadOnly(
            True
        )

        text = []

        text.append(
            "SETTINGS"
        )

        text.append(
            "------------------------------"
        )

        if settings:

            for key, value in settings.items():

                text.append(
                    f"{self.pretty_name(key)}: "
                    f"{value}"
                )

        else:

            text.append(
                "No separate settings stored."
            )

        text.append(
            ""
        )

        text.append(
            "MEASUREMENTS"
        )

        text.append(
            "------------------------------"
        )

        if measurements:

            for key, value in measurements.items():

                text.append(
                    f"{self.pretty_name(key)}: "
                    f"{value}"
                )

        else:

            text.append(
                "No measurements stored."
            )

        text.append(
            ""
        )

        text.append(
            "RESULT"
        )

        text.append(
            "------------------------------"
        )

        text.append(
            str(
                record.get(
                    "result",
                    ""
                )
            )
        )

        text.append(
            ""
        )

        text.append(
            "REMARKS"
        )

        text.append(
            "------------------------------"
        )

        text.append(
            str(
                record.get(
                    "remarks",
                    ""
                )
            )
        )

        details.setPlainText(
            "\n".join(
                text
            )
        )

        layout.addWidget(
            details
        )

        # =================================================
        # CLOSE
        # =================================================

        buttons = QHBoxLayout()

        buttons.addStretch()

        close_button = QPushButton(
            "Close"
        )

        close_button.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            close_button
        )

        layout.addLayout(
            buttons
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def build_summary(self):

        record = self.record

        record_type = str(
            record.get(
                "record_type",
                ""
            )
        )

        if record_type == "PROTECTION":

            test_name = record.get(
                "protection_code",
                ""
            )

            equipment = record.get(
                "relay_id",
                ""
            )

        else:

            test_name = record.get(
                "test_type",
                ""
            )

            equipment = record.get(
                "component_id",
                ""
            )

        return (
            f"Test ID: "
            f"{record.get('test_id', '')}\n"

            f"Date: "
            f"{record.get('test_date', '')}\n"

            f"Type: "
            f"{record_type}\n"

            f"Test: "
            f"{test_name}\n"

            f"Component / Relay: "
            f"{equipment}\n"

            f"Panel: "
            f"{record.get('panel_id', '')}"
        )

    # =====================================================
    # PRETTY FIELD NAME
    # =====================================================

    @staticmethod
    def pretty_name(
        value
    ):

        return str(
            value
        ).replace(
            "_",
            " "
        ).title()