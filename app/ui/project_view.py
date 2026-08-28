from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QDialog,
    QLineEdit,
    QDateEdit,
    QDialogButtonBox,
    QMessageBox,
    QFileDialog,
    QHBoxLayout,
    QComboBox,
    QFormLayout,
)
from PySide6.QtCore import QDate, Signal

from app.services.project_manager import ProjectManager
from app.services.project_transfer_service import (
    ProjectTransferService
)
from app.services.project_merge_service import (
    ProjectMergeService
)
from app.services.mapped_project_merge_service import (
    MappedProjectMergeService
)
from app.ui.project_merge_dialog import (
    ProjectMergeDialog
)
from app.services.asset_manager import AssetManager
from app.config.settings import PROJECTS_DIR


class NewProjectDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(
            "Create New Project"
        )

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel("Project Title")
        )

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText(
            "Example: August 2026 Shutdown"
        )
        layout.addWidget(
            self.title_input
        )

        layout.addWidget(
            QLabel("Project Date")
        )

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(
            QDate.currentDate()
        )
        layout.addWidget(
            self.date_input
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self.accept
        )
        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(buttons)

    def get_data(self):

        return (
            self.title_input.text().strip(),
            self.date_input.date().toString(
                "dd-MM-yyyy"
            )
        )


class ProjectView(QWidget):

    project_opened = Signal(object)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.project_manager = ProjectManager(
            PROJECTS_DIR
        )

        self.project_transfer = ProjectTransferService(
            PROJECTS_DIR
        )

        self.project_merge = ProjectMergeService(
            PROJECTS_DIR
        )

        self.mapped_project_merge = (
            MappedProjectMergeService(
                PROJECTS_DIR
            )
        )

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(
            30, 25, 30, 25
        )
        self.layout.setSpacing(12)

        title = QLabel(
            "Protection Testing Projects"
        )
        title.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: bold;
                padding: 10px;
            }
            """
        )
        self.layout.addWidget(title)

        self.project_list = QListWidget()
        self.project_list.setMinimumHeight(300)
        self.project_list.itemDoubleClicked.connect(
            self.open_project
        )
        self.layout.addWidget(
            self.project_list
        )

        basic_buttons = QHBoxLayout()

        self.new_project_button = QPushButton(
            "+ New Project"
        )
        self.open_project_button = QPushButton(
            "Open Project"
        )

        self.new_project_button.clicked.connect(
            self.create_project
        )
        self.open_project_button.clicked.connect(
            self.open_selected_project
        )

        basic_buttons.addWidget(
            self.new_project_button
        )
        basic_buttons.addWidget(
            self.open_project_button
        )

        self.layout.addLayout(
            basic_buttons
        )

        transfer_buttons = QHBoxLayout()

        self.import_project_button = QPushButton(
            "Import Project"
        )
        self.export_project_button = QPushButton(
            "Export Selected Project"
        )
        self.merge_project_button = QPushButton(
            "Compare & Merge Project..."
        )

        self.import_project_button.clicked.connect(
            self.import_project
        )
        self.export_project_button.clicked.connect(
            self.export_selected_project
        )
        self.merge_project_button.clicked.connect(
            self.merge_project_into_existing
        )

        transfer_buttons.addWidget(
            self.import_project_button
        )
        transfer_buttons.addWidget(
            self.export_project_button
        )
        transfer_buttons.addWidget(
            self.merge_project_button
        )

        self.layout.addLayout(
            transfer_buttons
        )

        self.layout.addStretch()

        self.load_projects()

    # =========================================================
    # PROJECT LIST
    # =========================================================

    def load_projects(self):

        self.project_list.clear()

        for project in (
            self.project_manager.load_projects()
        ):

            self.project_list.addItem(
                f"{project.title}"
                f"   |   "
                f"{project.date}"
            )

    def create_project(self):

        dialog = NewProjectDialog(self)

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        title, date = dialog.get_data()

        if not title:

            QMessageBox.warning(
                self,
                "Invalid Project",
                "Please enter a project title."
            )
            return

        try:

            self.project_manager.create_project(
                title,
                date
            )
            self.load_projects()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Cannot Create Project",
                str(error)
            )

    def open_project(self, item):

        if item is None:
            return

        row = self.project_list.row(item)

        projects = (
            self.project_manager.load_projects()
        )

        if 0 <= row < len(projects):
            self.project_opened.emit(
                projects[row]
            )

    def open_selected_project(self):

        item = self.project_list.currentItem()

        if item is None:
            QMessageBox.information(
                self,
                "Open Project",
                "Please select a project first."
            )
            return

        self.open_project(item)

    # =========================================================
    # EXPORT
    # =========================================================

    def export_selected_project(self):

        item = self.project_list.currentItem()

        if item is None:
            QMessageBox.information(
                self,
                "Export Project",
                "Please select a project first."
            )
            return

        row = self.project_list.row(item)
        projects = (
            self.project_manager.load_projects()
        )

        if not 0 <= row < len(projects):
            return

        project = projects[row]

        project_folder = (
            PROJECTS_DIR /
            project.title
        )

        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Export Project",
            str(
                PROJECTS_DIR /
                f"{project.title}.ptsproject"
            ),
            "Protection Testing Project (*.ptsproject);;"
            "ZIP Archive (*.zip)"
        )

        if not output_file:
            return

        if not output_file.lower().endswith(
            (".ptsproject", ".zip")
        ):
            output_file += ".ptsproject"

        try:

            self.project_transfer.export_project(
                project_folder,
                output_file
            )

            QMessageBox.information(
                self,
                "Project Exported",
                f"Project exported successfully.\n\n"
                f"{output_file}"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Export Failed",
                str(error)
            )

    # =========================================================
    # IMPORT AS NEW PROJECT
    # =========================================================

    def import_project(self):

        archive_file, _ = QFileDialog.getOpenFileName(
            self,
            "Import Project",
            "",
            "Protection Testing Project (*.ptsproject *.zip);;"
            "All Files (*.*)"
        )

        if not archive_file:
            return

        try:

            import zipfile
            import json

            with zipfile.ZipFile(
                archive_file,
                "r"
            ) as archive:

                manifest = json.loads(
                    archive.read(
                        "project_manifest.json"
                    ).decode(
                        "utf-8"
                    )
                )

            original_title = str(
                manifest.get(
                    "project",
                    {}
                ).get(
                    "title",
                    "Imported Project"
                )
                or "Imported Project"
            ).strip()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Import Failed",
                str(error)
            )
            return

        destination = (
            PROJECTS_DIR /
            original_title
        )

        project_name = original_title

        if destination.exists():

            dialog = QDialog(self)
            dialog.setWindowTitle(
                "Project Already Exists"
            )

            dialog_layout = QVBoxLayout(dialog)

            dialog_layout.addWidget(
                QLabel(
                    f"A project named '{original_title}' "
                    "already exists.\n\n"
                    "Enter another name for this imported copy:"
                )
            )

            name_input = QLineEdit(
                original_title + " - Imported"
            )

            dialog_layout.addWidget(
                name_input
            )

            buttons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok
                | QDialogButtonBox.StandardButton.Cancel
            )

            buttons.accepted.connect(
                dialog.accept
            )
            buttons.rejected.connect(
                dialog.reject
            )

            dialog_layout.addWidget(
                buttons
            )

            if (
                dialog.exec()
                != QDialog.DialogCode.Accepted
            ):
                return

            project_name = (
                name_input.text().strip()
            )

            if not project_name:
                return

            destination = (
                PROJECTS_DIR /
                project_name
            )

            if destination.exists():

                QMessageBox.warning(
                    self,
                    "Import Project",
                    f"A project named '{project_name}' "
                    "already exists."
                )
                return

        try:

            self.project_transfer.import_project(
                archive_file,
                project_name=project_name
            )

            self.load_projects()

            QMessageBox.information(
                self,
                "Project Imported",
                f"Project '{project_name}' imported successfully."
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Import Failed",
                str(error)
            )

    # =========================================================
    # VISUAL COMPARE & MERGE
    # =========================================================

    def merge_project_into_existing(self):

        archive_file, _ = QFileDialog.getOpenFileName(
            self,
            "Select Project to Merge",
            "",
            "Protection Testing Project (*.ptsproject *.zip);;"
            "All Files (*.*)"
        )

        if not archive_file:
            return

        projects = (
            self.project_manager.load_projects()
        )

        if not projects:

            QMessageBox.information(
                self,
                "Merge Project",
                "There are no existing projects."
            )
            return

        # -----------------------------------------------------
        # Read the source archive into a temporary folder.
        # -----------------------------------------------------

        import tempfile
        import zipfile
        import json

        try:

            temp_dir = tempfile.TemporaryDirectory(
                prefix="pts_compare_"
            )

            temp_root = (
                Path(temp_dir.name)
            )

            with zipfile.ZipFile(
                archive_file,
                "r"
            ) as archive:

                archive.extractall(
                    temp_root
                )

            source_assets_file = (
                temp_root /
                "assets.json"
            )

            if not source_assets_file.exists():

                temp_dir.cleanup()

                raise ValueError(
                    "The selected archive does not contain "
                    "assets.json."
                )

            with open(
                source_assets_file,
                "r",
                encoding="utf-8"
            ) as file:
                source_nodes = json.load(file)

            if isinstance(
                source_nodes,
                dict
            ):
                source_nodes = source_nodes.get(
                    "assets",
                    []
                )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Cannot Read Project",
                str(error)
            )
            return

        # -----------------------------------------------------
        # Select destination project.
        # -----------------------------------------------------

        project_dialog = QDialog(self)
        project_dialog.setWindowTitle(
            "Select Destination Project"
        )
        project_dialog.resize(
            500,
            180
        )

        layout = QVBoxLayout(
            project_dialog
        )

        layout.addWidget(
            QLabel(
                "Select the existing project into which "
                "the imported hierarchy will be merged."
            )
        )

        project_combo = QComboBox()

        for project in projects:
            project_combo.addItem(
                f"{project.title}   |   {project.date}",
                project
            )

        layout.addWidget(
            project_combo
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            project_dialog.accept
        )
        buttons.rejected.connect(
            project_dialog.reject
        )

        layout.addWidget(
            buttons
        )

        if (
            project_dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            temp_dir.cleanup()
            return

        destination_project = (
            project_combo.currentData()
        )

        destination_folder = (
            PROJECTS_DIR /
            destination_project.title
        )

        try:

            destination_assets_file = (
                destination_folder /
                "assets.json"
            )

            with open(
                destination_assets_file,
                "r",
                encoding="utf-8"
            ) as file:
                destination_nodes = json.load(file)

            if isinstance(
                destination_nodes,
                dict
            ):
                destination_nodes = destination_nodes.get(
                    "assets",
                    []
                )

            comparison = ProjectMergeDialog(
                source_nodes=source_nodes,
                destination_nodes=destination_nodes,
                parent=self
            )

            if (
                comparison.exec()
                != QDialog.DialogCode.Accepted
            ):

                temp_dir.cleanup()
                return

            mapping = comparison.get_mapping()

            summary = (
                self.mapped_project_merge.merge(
                    source_project_folder=temp_root,
                    destination_project_folder=destination_folder,
                    mapping=mapping
                )
            )

            temp_dir.cleanup()

            QMessageBox.information(
                self,
                "Project Merged",
                "Project merge completed successfully.\n\n"
                f"Nodes created: "
                f"{summary['nodes_created']}\n"
                f"Nodes reused: "
                f"{summary['nodes_reused']}\n"
                f"Components added: "
                f"{summary['components_created']}\n"
                f"Tests imported: "
                f"{summary['tests_imported']}\n"
                f"Physical assets merged: "
                f"{summary['assets_merged']}\n"
                f"Artifacts copied: "
                f"{summary['artifacts_copied']}"
            )

        except Exception as error:

            try:
                temp_dir.cleanup()
            except Exception:
                pass

            QMessageBox.critical(
                self,
                "Merge Failed",
                str(error)
            )
