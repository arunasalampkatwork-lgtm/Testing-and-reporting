import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QMessageBox,
)


class TestDetailView(QDialog):

    def __init__(
        self,
        test_service,
        test_id,
        record_type=None,
        parent=None,
    ):

        super().__init__(parent)

        self.test_service = test_service
        self.test_id = str(test_id)
        self.record_type = (
            str(record_type).upper()
            if record_type
            else None
        )

        self.setWindowTitle(
            "Test Details"
        )

        self.resize(
            800,
            650,
        )

        self.build_ui()

        self.load_test()

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

        self.header = QLabel(
            "Test Details"
        )

        self.header.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
                padding: 6px;
            }
            """
        )

        layout.addWidget(
            self.header
        )

        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        self.summary = QLabel()

        self.summary.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                padding: 6px;
            }
            """
        )

        layout.addWidget(
            self.summary
        )

        # -------------------------------------------------
        # SETTINGS
        # -------------------------------------------------

        self.settings_label = QLabel(
            "Settings"
        )

        self.settings_label.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding-top: 8px;
            }
            """
        )

        layout.addWidget(
            self.settings_label
        )

        self.settings_table = (
            QTableWidget()
        )

        self.settings_table.setColumnCount(
            2
        )

        self.settings_table.setHorizontalHeaderLabels(
            [
                "Parameter",
                "Value",
            ]
        )

        self.configure_table(
            self.settings_table
        )

        layout.addWidget(
            self.settings_table
        )

        # -------------------------------------------------
        # MEASUREMENTS
        # -------------------------------------------------

        self.measurements_label = QLabel(
            "Measurements / Results"
        )

        self.measurements_label.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding-top: 8px;
            }
            """
        )

        layout.addWidget(
            self.measurements_label
        )

        self.measurements_table = (
            QTableWidget()
        )

        self.measurements_table.setColumnCount(
            2
        )

        self.measurements_table.setHorizontalHeaderLabels(
            [
                "Parameter",
                "Value",
            ]
        )

        self.configure_table(
            self.measurements_table
        )

        layout.addWidget(
            self.measurements_table
        )

        # -------------------------------------------------
        # REMARKS
        # -------------------------------------------------

        self.remarks_label = QLabel(
            "Remarks"
        )

        self.remarks_label.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding-top: 8px;
            }
            """
        )

        layout.addWidget(
            self.remarks_label
        )

        self.remarks = QLabel()

        self.remarks.setWordWrap(
            True
        )

        self.remarks.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        self.remarks.setStyleSheet(
            """
            QLabel {
                padding: 8px;
                border: 1px solid #cccccc;
                background: #f5f5f5;
            }
            """
        )

        layout.addWidget(
            self.remarks
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

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
    # TABLE CONFIGURATION
    # =====================================================

    @staticmethod
    def configure_table(
        table
    ):

        table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        table.setAlternatingRowColors(
            True
        )

        table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents
        )

        table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

    # =====================================================
    # LOAD TEST
    # =====================================================

    def load_test(self):

        try:

            record = self.get_record()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                str(error),
            )

            return

        if not record:

            QMessageBox.warning(
                self,
                "Test Not Found",
                (
                    "The selected test record "
                    "could not be found."
                ),
            )

            return

        self.record = record

        self.populate_summary()

        self.populate_settings()

        self.populate_measurements()

        self.remarks.setText(
            str(
                record.get(
                    "remarks",
                    ""
                )
                or ""
            )
        )

    # =====================================================
    # GET RECORD
    # =====================================================

    def get_record(self):

        # -------------------------------------------------
        # Explicit record type
        # -------------------------------------------------

        if self.record_type == "COMPONENT":

            if hasattr(
                self.test_service,
                "get_component_test"
            ):

                return (
                    self.test_service
                    .get_component_test(
                        self.test_id
                    )
                )

        # -------------------------------------------------
        # Protection
        # -------------------------------------------------

        if self.record_type == "PROTECTION":

            return (
                self.test_service
                .get_test(
                    self.test_id
                )
            )

        # -------------------------------------------------
        # Backward-compatible lookup
        # -------------------------------------------------

        try:

            record = (
                self.test_service
                .get_test(
                    self.test_id
                )
            )

            if record:

                return record

        except Exception:

            pass

        if hasattr(
            self.test_service,
            "get_component_test"
        ):

            return (
                self.test_service
                .get_component_test(
                    self.test_id
                )
            )

        return None

    # =====================================================
    # SUMMARY
    # =====================================================

    def populate_summary(self):

        record = self.record

        record_type = str(
            record.get(
                "record_type",
                ""
            )
        ).upper()

        if record_type == "COMPONENT":

            test_type = record.get(
                "test_type",
                ""
            )

            equipment = record.get(
                "component_id",
                ""
            )

        else:

            record_type = "PROTECTION"

            test_type = record.get(
                "protection_code",
                ""
            )

            equipment = record.get(
                "relay_id",
                ""
            )

        self.header.setText(
            (
                f"{test_type} - "
                f"{record_type} Test"
            )
        )

        self.summary.setText(
            (
                f"<b>Test ID:</b> "
                f"{record.get('test_id', '')}"
                f"<br>"
                f"<b>Date:</b> "
                f"{record.get('test_date', '')}"
                f"<br>"
                f"<b>Project:</b> "
                f"{record.get('project_id', '')}"
                f"<br>"
                f"<b>Panel:</b> "
                f"{record.get('panel_id', '')}"
                f"<br>"
                f"<b>Component / Relay:</b> "
                f"{equipment}"
                f"<br>"
                f"<b>Test Type:</b> "
                f"{test_type}"
                f"<br>"
                f"<b>Result:</b> "
                f"<b>{record.get('result', '')}</b>"
            )
        )

    # =====================================================
    # SETTINGS
    # =====================================================

    def populate_settings(self):

        settings = self.record.get(
            "settings",
            {}
        )

        if not isinstance(
            settings,
            dict
        ):

            settings = self.decode_json(
                settings
            )

        self.populate_table(
            self.settings_table,
            settings
        )

        # Component tests currently store their
        # configuration/test inputs inside measurements.
        if not settings:

            self.settings_label.setText(
                "Configuration"
            )

        else:

            self.settings_label.setText(
                "Settings"
            )

    # =====================================================
    # MEASUREMENTS
    # =====================================================

    def populate_measurements(self):

        measurements = self.record.get(
            "measurements",
            {}
        )

        if not isinstance(
            measurements,
            dict
        ):

            measurements = self.decode_json(
                measurements
            )

        self.populate_table(
            self.measurements_table,
            measurements
        )

    # =====================================================
    # POPULATE TABLE
    # =====================================================

    def populate_table(
        self,
        table,
        data
    ):

        table.setRowCount(
            0
        )

        if not isinstance(
            data,
            dict
        ):

            return

        for key, value in data.items():

            row = (
                table.rowCount()
            )

            table.insertRow(
                row
            )

            table.setItem(
                row,
                0,
                QTableWidgetItem(
                    self.pretty_name(
                        key
                    )
                )
            )

            table.setItem(
                row,
                1,
                QTableWidgetItem(
                    self.format_value(
                        value
                    )
                )
            )

        table.resizeRowsToContents()

    # =====================================================
    # JSON DECODER
    # =====================================================

    @staticmethod
    def decode_json(
        value
    ):

        if isinstance(
            value,
            dict
        ):

            return value

        if not value:

            return {}

        try:

            decoded = json.loads(
                value
            )

            if isinstance(
                decoded,
                dict
            ):

                return decoded

        except (
            json.JSONDecodeError,
            TypeError
        ):

            pass

        return {}

    # =====================================================
    # FORMAT VALUE
    # =====================================================

    @staticmethod
    def format_value(
        value
    ):

        if value is None:

            return ""

        if isinstance(
            value,
            bool
        ):

            return (
                "Yes"
                if value
                else
                "No"
            )

        if isinstance(
            value,
            (dict, list)
        ):

            try:

                return json.dumps(
                    value,
                    indent=2
                )

            except TypeError:

                return str(
                    value
                )

        return str(
            value
        )

    # =====================================================
    # PRETTY NAME
    # =====================================================

    @staticmethod
    def pretty_name(
        value
    ):

        return (
            str(value)
            .replace(
                "_",
                " "
            )
            .strip()
            .title()
        )