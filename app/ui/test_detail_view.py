from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QScrollArea,
    QWidget,
    QGroupBox,
)

from app.ui.test_edit_dialog import (
    TestEditDialog
)
from app.services.report_service import ProtectionReportService
from app.ui.report_dialog import ReportDialog

class TestDetailView(QDialog):

    def __init__(self, test_service, test_id, project_folder=None, parent=None):

        super().__init__(
            parent
        )

        self.test_service = (
            test_service
        )

        self.test_id = (
            test_id
        )

        self.record = None
        self.project_folder = project_folder

        self.setWindowTitle(
            f"Test Details - {test_id}"
        )

        self.resize(
            900,
            700
        )

        self.build_ui()

        self.load_test()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(
        self
    ):

        layout = QVBoxLayout(
            self
        )

        self.header = QLabel(
            "Protection Test Details"
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

        layout.addWidget(
            self.header
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        self.container = QWidget()

        self.content_layout = QVBoxLayout(
            self.container
        )

        scroll.setWidget(
            self.container
        )

        layout.addWidget(
            scroll
        )

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

        layout.addLayout(
            buttons
        )

        self.report_button = QPushButton("Generate Report")
        self.report_button.clicked.connect(self.generate_report)
        buttons.addWidget(self.report_button)


    # =====================================================
    # LOAD
    # =====================================================

    def load_test(
        self
    ):

        try:

            self.record = (
                self.test_service
                .get_test(
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
                (
                    f"Test '{self.test_id}' "
                    "could not be found."
                )
            )

            return

        self.render()

    # =====================================================
    # CLEAR
    # =====================================================

    def clear_content(
        self
    ):

        while (
            self.content_layout.count()
        ):

            item = (
                self.content_layout
                .takeAt(0)
            )

            widget = (
                item.widget()
            )

            if widget is not None:

                widget.deleteLater()

    # =====================================================
    # RENDER
    # =====================================================

    def render(
        self
    ):

        self.clear_content()

        record = (
            self.record
        )

        # =================================================
        # BASIC INFORMATION
        # =================================================

        group = QGroupBox(
            "Test Information"
        )

        form = QFormLayout()

        self.add_readonly(
            form,
            "Test ID",
            record.get(
                "test_id",
                ""
            )
        )

        self.add_readonly(
            form,
            "Project",
            record.get(
                "project_id",
                ""
            )
        )

        self.add_readonly(
            form,
            "Panel",
            record.get(
                "panel_id",
                ""
            )
        )

        self.add_readonly(
            form,
            "Relay",
            record.get(
                "relay_id",
                ""
            )
        )

        self.add_readonly(
            form,
            "Protection",
            record.get(
                "protection_code",
                ""
            )
        )

        self.add_readonly(
            form,
            "Test Date",
            record.get(
                "test_date",
                ""
            )
        )

        group.setLayout(
            form
        )

        self.content_layout.addWidget(
            group
        )

        # =================================================
        # SETTINGS
        # =================================================

        settings = (
            record.get(
                "settings",
                {}
            )
            or {}
        )

        if settings:

            group = QGroupBox(
                "CT / Test Configuration"
            )

            form = QFormLayout()

            for key, value in settings.items():

                self.add_readonly(
                    form,
                    self.pretty_name(
                        key
                    ),
                    value
                )

            group.setLayout(
                form
            )

            self.content_layout.addWidget(
                group
            )

        # =================================================
        # MEASUREMENTS
        # =================================================

        measurements = (
            record.get(
                "measurements",
                {}
            )
            or {}
        )

        if measurements:

            group = QGroupBox(
                "Test Values and Calculations"
            )

            form = QFormLayout()

            for key, value in measurements.items():

                self.add_readonly(
                    form,
                    self.pretty_name(
                        key
                    ),
                    value
                )

            group.setLayout(
                form
            )

            self.content_layout.addWidget(
                group
            )

        # =================================================
        # RESULT
        # =================================================

        group = QGroupBox(
            "Result"
        )

        form = QFormLayout()

        self.add_readonly(
            form,
            "Result",
            record.get(
                "result",
                ""
            )
        )

        self.add_readonly(
            form,
            "Remarks",
            record.get(
                "remarks",
                ""
            )
        )

        group.setLayout(
            form
        )

        self.content_layout.addWidget(
            group
        )

        self.content_layout.addStretch()

    # =====================================================
    # READONLY
    # =====================================================

    @staticmethod
    def add_readonly(
        form,
        label,
        value
    ):

        widget = QLineEdit()

        widget.setText(
            str(
                value
                if value is not None
                else ""
            )
        )

        widget.setReadOnly(
            True
        )

        form.addRow(
            str(label),
            widget
        )

    # =====================================================
    # EDIT TEST
    # =====================================================

    def edit_test(
        self
    ):

        dialog = TestEditDialog(

            test_service=(
                self.test_service
            ),

            test_id=(
                self.test_id
            ),

            parent=self
        )

        result = (
            dialog.exec()
        )

        if result == (
            QDialog.DialogCode.Accepted
        ):

            # Reload the updated record.

            self.record = (
                self.test_service
                .get_test(
                    self.test_id
                )
            )

            self.render()

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
            .title()
        )

# Add this method to TestDetailView:
#
    def generate_report(self):

        if not self.project_folder:

            QMessageBox.warning(
                self,
                "Project Folder Missing",
                "The current project folder is not available."
            )

            return

        try:

            report_service = ProtectionReportService(
                test_service=self.test_service,
                project_folder=self.project_folder
            )

            dialog = ReportDialog(
                report_service=report_service,
                test_id=self.test_id,
                parent=self
            )

            dialog.exec()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Report Error",
                str(error)
            )