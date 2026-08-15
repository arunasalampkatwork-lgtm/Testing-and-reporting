from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QFileDialog,
)


class ReportDialog(QDialog):

    def __init__(self, report_service, test_id, parent=None):
        super().__init__(parent)
        self.report_service = report_service
        self.test_id = test_id
        self.setWindowTitle("Generate Protection Test Report")
        self.resize(520, 220)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Generate Protection Test Report")
        title.setStyleSheet(
            "QLabel { font-size: 18px; font-weight: bold; }"
        )
        layout.addWidget(title)

        layout.addWidget(QLabel(
            f"Test ID: {self.test_id}\n"
            "Output: Microsoft Word (.docx)"
        ))

        buttons = QHBoxLayout()
        generate = QPushButton("Generate Report")
        cancel = QPushButton("Cancel")

        generate.clicked.connect(self.generate_report)
        cancel.clicked.connect(self.reject)

        buttons.addWidget(generate)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)

    def generate_report(self):
        default_name = f"Protection_Test_{self.test_id}.docx"

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Protection Test Report",
            str(Path.home() / "Documents" / default_name),
            "Word Document (*.docx)",
        )

        if not output_path:
            return

        try:
            path = self.report_service.generate_protection_test_report(
                self.test_id,
                output_path,
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Report Generation Failed",
                str(error),
            )
            return

        QMessageBox.information(
            self,
            "Report Generated",
            f"Report generated successfully:\n\n{path}",
        )
        self.accept()
