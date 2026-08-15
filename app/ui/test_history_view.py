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

from app.ui.test_detail_view import (
    TestDetailView
)
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

        super().__init__(
            parent
        )

        # =================================================
        # REFERENCES
        # =================================================

        self.test_service = (
            test_service
        )

        self.project_id = (
            project_id
        )

        self.panel_id = (
            panel_id
        )

        self.project_folder = (
            project_folder
        )

        # =================================================
        # WINDOW
        # =================================================

        self.setWindowTitle(
            "Test History"
        )

        self.resize(
            1100,
            650
        )

        # =================================================
        # UI
        # =================================================

        self.build_ui()

        self.load_tests()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(
        self
    ):

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
                "Test Type",
                "Protection / Component",
                "Result",
                "Remarks",
                "Record Type",
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

        # -------------------------------------------------
        # SINGLE DOUBLE-CLICK CONNECTION
        # -------------------------------------------------

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

        self.edit_button = QPushButton(
            "View / Edit Test"
        )

        self.close_button = QPushButton(
            "Close"
        )

        self.refresh_button.clicked.connect(
            self.load_tests
        )

        self.edit_button.clicked.connect(
            self.open_selected_test
        )

        self.close_button.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            self.refresh_button
        )

        buttons.addWidget(
            self.edit_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.close_button
        )

        layout.addLayout(
            buttons
        )

    # =====================================================
    # LOAD ALL TESTS
    # =====================================================

    def load_tests(
        self
    ):

        self.table.setRowCount(
            0
        )

        try:

            # -------------------------------------------------
            # PROTECTION TESTS
            # -------------------------------------------------

            protection_tests = (
                self.test_service
                .get_all_tests()
            )

            # -------------------------------------------------
            # COMPONENT TESTS
            # CT / AUX RELAY
            # -------------------------------------------------

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

        # =================================================
        # COMBINE
        # =================================================

        history = []

        # -------------------------------------------------
        # PROTECTION TESTS
        #
        # Structure:
        #
        # 0 test_id
        # 1 project_id
        # 2 panel_id
        # 3 relay_id
        # 4 protection_code
        # 5 test_date
        # 6 result
        # 7 remarks
        # -------------------------------------------------

        for row in protection_tests:

            if row[1] != self.project_id:
                continue

            if row[2] != self.panel_id:
                continue

            history.append(
                {
                    "test_id":
                        row[0],

                    "date":
                        row[5],

                    "test_type":
                        "PROTECTION",

                    "protection_component":
                        row[4],

                    "component_id":
                        row[3],

                    "result":
                        row[6],

                    "remarks":
                        row[7],

                    "record_type":
                        "PROTECTION",
                }
            )

        # -------------------------------------------------
        # COMPONENT TESTS
        #
        # Structure:
        #
        # 0 test_id
        # 1 project_id
        # 2 panel_id
        # 3 component_id
        # 4 test_type
        # 5 test_date
        # 6 measurements_json
        # 7 result
        # 8 remarks
        # -------------------------------------------------

        for row in component_tests:

            if row[1] != self.project_id:
                continue

            if row[2] != self.panel_id:
                continue

            history.append(
                {
                    "test_id":
                        row[0],

                    "date":
                        row[5],

                    "test_type":
                        row[4],

                    "protection_component":
                        row[3],

                    "component_id":
                        row[3],

                    "result":
                        row[7],

                    "remarks":
                        row[8],

                    "record_type":
                        "COMPONENT",
                }
            )

        # =================================================
        # SORT BY DATE
        # =================================================

        history.sort(
            key=lambda item:
                str(
                    item.get(
                        "date",
                        ""
                    )
                ),
            reverse=True
        )

        # =================================================
        # POPULATE TABLE
        # =================================================

        for record in history:

            row = (
                self.table.rowCount()
            )

            self.table.insertRow(
                row
            )

            values = [

                record.get(
                    "test_id",
                    ""
                ),

                record.get(
                    "date",
                    ""
                ),

                record.get(
                    "test_type",
                    ""
                ),

                record.get(
                    "protection_component",
                    ""
                ),

                record.get(
                    "result",
                    ""
                ),

                record.get(
                    "remarks",
                    ""
                ),

                record.get(
                    "record_type",
                    ""
                ),
            ]

            for column, value in enumerate(
                values
            ):

                item = QTableWidgetItem(
                    str(
                        value
                        if value is not None
                        else ""
                    )
                )

                self.table.setItem(
                    row,
                    column,
                    item
                )

        # =================================================
        # HIDE RECORD TYPE COLUMN
        #
        # We keep it internally because later we need it
        # to decide which detail view to open.
        # =================================================

        self.table.setColumnHidden(
            6,
            True
        )

        self.table.resizeColumnsToContents()

    # =====================================================
    # SELECTED TEST
    # =====================================================

    def get_selected_test_id(
        self
    ):

        row = (
            self.table.currentRow()
        )

        if row < 0:

            return None

        item = (
            self.table.item(
                row,
                0
            )
        )

        if item is None:

            return None

        test_id = (
            item
            .text()
            .strip()
        )

        if not test_id:

            return None

        return test_id

    # =====================================================
    # OPEN SELECTED TEST
    # =====================================================

    def open_selected_test(
        self
    ):

        test_id = (
            self.get_selected_test_id()
        )

        if not test_id:

            QMessageBox.warning(
                self,
                "No Test Selected",
                "Select a test first."
            )

            return

        self.show_test_detail(
            test_id
        )

    # =====================================================
    # DOUBLE CLICK
    # =====================================================

    def open_test_detail(
        self,
        row,
        column
    ):

        item = (
            self.table.item(
                row,
                0
            )
        )

        if item is None:

            return

        test_id = (
            item
            .text()
            .strip()
        )

        if not test_id:

            return

        self.show_test_detail(
            test_id
        )

    # =====================================================
    # SHOW DETAIL
    # =====================================================

    def show_test_detail(
        self,
        test_id
    ):

        # -------------------------------------------------
        # Determine record type.
        #
        # We cannot assume every TEST-XXXXXXXX belongs
        # to protection_tests.
        # -------------------------------------------------

        try:

            protection_record = (
                self.test_service
                .get_test(
                    test_id
                )
            )

        except Exception:

            protection_record = None

        if protection_record is not None:

            self.test_detail_view = (
                TestDetailView(

                    test_service=(
                        self.test_service
                    ),

                    test_id=(
                        test_id
                    ),

                    project_folder=(
                        self.project_folder
                    ),

                    parent=self
                )
            )

            self.test_detail_view.exec()

            self.load_tests()

            return

        # -------------------------------------------------
        # COMPONENT TEST
        # -------------------------------------------------

        try:

            component_record = (
                self.test_service
                .get_component_test(
                    test_id
                )
            )

        except Exception:

            component_record = None

        if component_record is not None:

            self.show_component_test_detail(
                component_record
            )

            return

        # -------------------------------------------------
        # NOT FOUND
        # -------------------------------------------------

        QMessageBox.warning(
            self,
            "Test Not Found",
            (
                f"Unable to find test record:\n\n"
                f"{test_id}"
            )
        )
        component_test = (
            self.test_service
            .get_component_test(
                test_id
            )
        )

        if component_test is not None:

            test_type = str(
                component_test.get(
                    "test_type",
                    ""
                )
            ).upper()

            if test_type == "CT":

                self.test_detail_view = (
                    CTTestDetailView(
                        test_service=self.test_service,
                        test_id=test_id,
                        project_folder=self.project_folder,
                        parent=self
                    )
                )

            elif test_type == "AUX_RELAY":

                self.test_detail_view = (
                    AuxRelayTestDetailView(
                        test_service=self.test_service,
                        test_id=test_id,
                        project_folder=self.project_folder,
                        parent=self
                    )
                )

            else:

                # Existing generic component detail view
                self.test_detail_view = TestDetailView(
                    test_service=self.test_service,
                    test_id=test_id,
                    project_folder=self.project_folder,
                    parent=self
                )

            self.test_detail_view.exec()

            self.load_tests()

            return

    # =====================================================
    # COMPONENT TEST DETAIL
    # =====================================================

    def show_component_test_detail(
        self,
        record
    ):

        test_type = str(
            record.get(
                "test_type",
                ""
            )
        ).strip().upper()

        # -------------------------------------------------
        # CT
        # -------------------------------------------------

        if test_type == "CT":

            try:

                from app.ui.ct_test_detail_view import (
                    CTTestDetailView
                )

                self.component_test_detail_view = (
                    CTTestDetailView(

                        test_service=(
                            self.test_service
                        ),

                        test_id=(
                            record.get(
                                "test_id"
                            )
                        ),

                        project_folder=(
                            self.project_folder
                        ),

                        parent=self
                    )
                )

                self.component_test_detail_view.exec()

                self.load_tests()

                return

            except ImportError:

                pass

        # -------------------------------------------------
        # FALLBACK
        # -------------------------------------------------
        #
        # Until CTTestDetailView exists, display the
        # stored component-test data instead of crashing.
        # -------------------------------------------------

        measurements = (
            record.get(
                "measurements",
                {}
            )
        )

        text = (
            f"Test ID: "
            f"{record.get('test_id', '')}\n\n"

            f"Test Type: "
            f"{record.get('test_type', '')}\n\n"

            f"Component ID: "
            f"{record.get('component_id', '')}\n\n"

            f"Date: "
            f"{record.get('test_date', '')}\n\n"

            f"Result: "
            f"{record.get('result', '')}\n\n"

            f"Remarks: "
            f"{record.get('remarks', '')}\n\n"

            f"Measurements:\n"
            f"{measurements}"
        )

    def show_component_test_detail(
        self,
        record
    ):

        test_type = str(
            record.get(
                "test_type",
                ""
            )
        ).strip().upper()

        # =================================================
        # CT TEST
        # =================================================

        if test_type == "CT":

            try:

                from app.ui.ct_test_detail_view import (
                    CTTestDetailView
                )

                self.component_test_detail_view = (
                    CTTestDetailView(

                        test_service=(
                            self.test_service
                        ),

                        test_id=(
                            record.get(
                                "test_id"
                            )
                        ),

                        project_folder=(
                            self.project_folder
                        ),

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

        # =================================================
        # UNKNOWN COMPONENT TEST
        # =================================================

        QMessageBox.information(
            self,
            "Component Test",
            (
                "Detailed view is not yet available "
                "for component test type:\n\n"
                f"{test_type}"
            )
        )

        self.load_tests()