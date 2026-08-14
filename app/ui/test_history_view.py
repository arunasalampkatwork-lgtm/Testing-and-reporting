from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QMessageBox,
    QLabel
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

        self.test_service = test_service
        self.project_id = project_id
        self.panel_id = panel_id

        self.setWindowTitle(
            "Protection Test History"
        )

        self.resize(
            900,
            600
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

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = QLabel(
            "Protection Test History"
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

        # -------------------------------------------------
        # TABLE
        # -------------------------------------------------

        self.table = QTableWidget()

        self.table.setColumnCount(
            6
        )

        self.table.setHorizontalHeaderLabels(
            [
                "Test ID",
                "Date",
                "Protection",
                "Relay / Component",
                "Result",
                "Remarks"
            ]
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setAlternatingRowColors(
            True
        )

        self.table.cellDoubleClicked.connect(
            self.open_test_detail
        )

        layout.addWidget(
            self.table
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        buttons = QHBoxLayout()

        refresh_button = QPushButton(
            "Refresh"
        )

        close_button = QPushButton(
            "Close"
        )

        refresh_button.clicked.connect(
            self.load_tests
        )

        close_button.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            refresh_button
        )

        buttons.addStretch()

        buttons.addWidget(
            close_button
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

        try:

            tests = (
                self.test_service
                .get_all_tests()
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                str(error)
            )

            return

        # -------------------------------------------------
        # FILTER PROJECT / PANEL
        # -------------------------------------------------

        filtered_tests = []

        for row in tests:

            # Expected structure:
            #
            # 0 test_id
            # 1 project_id
            # 2 panel_id
            # 3 relay_id
            # 4 protection_code
            # 5 test_date
            # 6 result
            # 7 remarks

            if row[1] != self.project_id:
                continue

            if row[2] != self.panel_id:
                continue

            filtered_tests.append(
                row
            )

        # -------------------------------------------------
        # POPULATE TABLE
        # -------------------------------------------------

        for row_data in filtered_tests:

            row = self.table.rowCount()

            self.table.insertRow(
                row
            )

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(row_data[0])
                )
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(row_data[5])
                )
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(row_data[4])
                )
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    str(row_data[3])
                )
            )

            self.table.setItem(
                row,
                4,
                QTableWidgetItem(
                    str(row_data[6])
                )
            )

            self.table.setItem(
                row,
                5,
                QTableWidgetItem(
                    str(row_data[7])
                )
            )

        # -------------------------------------------------
        # RESIZE
        # -------------------------------------------------

        self.table.resizeColumnsToContents()

    # =====================================================
    # OPEN TEST DETAIL
    # =====================================================

    def open_test_detail(
        self,
        row,
        column
    ):

        test_id_item = self.table.item(
            row,
            0
        )

        if test_id_item is None:
            return

        test_id = (
            test_id_item.text()
            .strip()
        )

        if not test_id:
            return

        self.test_detail_view = TestDetailView(
            test_service=self.test_service,
            test_id=test_id,
            parent=self
        )

        self.test_detail_view.exec()