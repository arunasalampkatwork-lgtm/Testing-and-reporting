import json

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QWidget,
    QGroupBox,
    QMessageBox
)


class TestDetailView(QDialog):

    def __init__(
        self,
        test_service,
        test_id,
        parent=None
    ):

        super().__init__(parent)

        self.test_service = test_service
        self.test_id = test_id

        self.setWindowTitle(
            f"Test Details - {test_id}"
        )

        self.resize(
            700,
            750
        )

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        # =================================================
        # GET TEST
        # =================================================

        test = self.test_service.get_test(
            self.test_id
        )

        if test is None:

            QMessageBox.critical(
                self,
                "Error",
                "The selected test could not be found."
            )

            self.reject()

            return

        self.test = test

        # =================================================
        # HEADER
        # =================================================

        header = QLabel(
            "Protection Test Details"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
            }
            """
        )

        main_layout.addWidget(
            header
        )

        # =================================================
        # TEST INFORMATION
        # =================================================

        information_group = QGroupBox(
            "Test Information"
        )

        information_layout = QFormLayout()

        self.add_readonly_field(
            information_layout,
            "Test ID",
            test.get("test_id", "")
        )

        self.add_readonly_field(
            information_layout,
            "Project ID",
            test.get("project_id", "")
        )

        self.add_readonly_field(
            information_layout,
            "Panel ID",
            test.get("panel_id", "")
        )

        self.add_readonly_field(
            information_layout,
            "Relay / Component ID",
            test.get("relay_id", "")
        )

        self.add_readonly_field(
            information_layout,
            "Protection Function",
            test.get("protection_code", "")
        )

        self.add_readonly_field(
            information_layout,
            "Test Date",
            test.get("test_date", "")
        )

        information_group.setLayout(
            information_layout
        )

        main_layout.addWidget(
            information_group
        )

        # =================================================
        # SETTINGS
        # =================================================

        settings_group = QGroupBox(
            "Test Settings"
        )

        settings_layout = QFormLayout()

        settings = test.get(
            "settings",
            {}
        )

        if settings:

            for key, value in settings.items():

                self.add_readonly_field(
                    settings_layout,
                    self.format_label(key),
                    value
                )

        else:

            settings_layout.addRow(
                QLabel("No settings recorded.")
            )

        settings_group.setLayout(
            settings_layout
        )

        main_layout.addWidget(
            settings_group
        )

        # =================================================
        # MEASUREMENTS
        # =================================================

        measurements_group = QGroupBox(
            "Test Measurements"
        )

        measurements_layout = QFormLayout()

        measurements = test.get(
            "measurements",
            {}
        )

        if measurements:

            for key, value in measurements.items():

                self.add_readonly_field(
                    measurements_layout,
                    self.format_label(key),
                    value
                )

        else:

            measurements_layout.addRow(
                QLabel(
                    "No measurements recorded."
                )
            )

        measurements_group.setLayout(
            measurements_layout
        )

        # =================================================
        # SCROLL AREA
        # =================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll_container = QWidget()

        scroll_layout = QVBoxLayout(
            scroll_container
        )

        scroll_layout.addWidget(
            measurements_group
        )

        scroll.setWidget(
            scroll_container
        )

        main_layout.addWidget(
            scroll
        )

        # =================================================
        # RESULT
        # =================================================

        result_group = QGroupBox(
            "Test Result"
        )

        result_layout = QFormLayout()

        result = test.get(
            "result",
            ""
        )

        result_field = QLineEdit(
            str(result)
        )

        result_field.setReadOnly(
            True
        )

        # Highlight result

        if str(result).upper() == "PASS":

            result_field.setStyleSheet(
                """
                QLineEdit {
                    font-weight: bold;
                    background-color: #d4edda;
                }
                """
            )

        elif str(result).upper() == "FAIL":

            result_field.setStyleSheet(
                """
                QLineEdit {
                    font-weight: bold;
                    background-color: #f8d7da;
                }
                """
            )

        result_layout.addRow(
            "Result",
            result_field
        )

        remarks_field = QLineEdit(
            str(
                test.get(
                    "remarks",
                    ""
                )
            )
        )

        remarks_field.setReadOnly(
            True
        )

        result_layout.addRow(
            "Remarks",
            remarks_field
        )

        result_group.setLayout(
            result_layout
        )

        main_layout.addWidget(
            result_group
        )

        # =================================================
        # CLOSE BUTTON
        # =================================================

        buttons = QHBoxLayout()

        close_button = QPushButton(
            "Close"
        )

        close_button.clicked.connect(
            self.accept
        )

        buttons.addStretch()

        buttons.addWidget(
            close_button
        )

        main_layout.addLayout(
            buttons
        )

    # =====================================================
    # ADD READ ONLY FIELD
    # =====================================================

    def add_readonly_field(
        self,
        layout,
        label,
        value
    ):

        field = QLineEdit(
            str(value)
        )

        field.setReadOnly(
            True
        )

        layout.addRow(
            label,
            field
        )

    # =====================================================
    # FORMAT LABEL
    # =====================================================

    def format_label(
        self,
        key
    ):

        return (
            str(key)
            .replace("_", " ")
            .title()
        )