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
)

from PySide6.QtCore import QDate, Signal

from app.services.project_manager import ProjectManager
from app.config.settings import PROJECTS_DIR


class NewProjectDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Create New Project")

        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # Project title
        # ---------------------------------------------------------

        title_label = QLabel("Project Title")

        self.title_input = QLineEdit()

        self.title_input.setPlaceholderText(
            "Example: August 2026 Shutdown"
        )

        layout.addWidget(title_label)
        layout.addWidget(self.title_input)

        # ---------------------------------------------------------
        # Project date
        # ---------------------------------------------------------

        date_label = QLabel("Project Date")

        self.date_input = QDateEdit()

        self.date_input.setCalendarPopup(True)

        self.date_input.setDate(
            QDate.currentDate()
        )

        layout.addWidget(date_label)
        layout.addWidget(self.date_input)

        # ---------------------------------------------------------
        # Buttons
        # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # Return entered data
    # ---------------------------------------------------------

    def get_data(self):

        title = self.title_input.text().strip()

        date = self.date_input.date().toString(
            "dd-MM-yyyy"
        )

        return title, date


class ProjectView(QWidget):

    # ---------------------------------------------------------
    # Signal emitted when a project is opened
    # ---------------------------------------------------------

    project_opened = Signal(object)

    def __init__(self, parent=None):

        super().__init__(parent)

        # -----------------------------------------------------
        # Project manager
        # -----------------------------------------------------

        self.project_manager = ProjectManager(
            PROJECTS_DIR
        )

        # -----------------------------------------------------
        # Main layout
        # -----------------------------------------------------

        self.layout = QVBoxLayout(self)

        # -----------------------------------------------------
        # Title
        # -----------------------------------------------------

        title = QLabel(
            "Protection Testing Projects"
        )

        title.setStyleSheet(
            """
            font-size: 22px;
            font-weight: bold;
            padding: 10px;
            """
        )

        self.layout.addWidget(title)

        # -----------------------------------------------------
        # Project list
        # -----------------------------------------------------

        self.project_list = QListWidget()

        self.project_list.setMinimumHeight(
            300
        )

        # Double-click opens project

        self.project_list.itemDoubleClicked.connect(
            self.open_project
        )

        self.layout.addWidget(
            self.project_list
        )

        # -----------------------------------------------------
        # New Project button
        # -----------------------------------------------------

        self.new_project_button = QPushButton(
            "+ New Project"
        )

        self.new_project_button.clicked.connect(
            self.create_project
        )

        self.layout.addWidget(
            self.new_project_button
        )

        # -----------------------------------------------------
        # Open Project button
        # -----------------------------------------------------

        self.open_project_button = QPushButton(
            "Open Project"
        )

        self.open_project_button.clicked.connect(
            self.open_selected_project
        )

        self.layout.addWidget(
            self.open_project_button
        )

        # -----------------------------------------------------
        # Load existing projects
        # -----------------------------------------------------

        self.load_projects()

    # =========================================================
    # LOAD PROJECTS
    # =========================================================

    def load_projects(self):

        self.project_list.clear()

        projects = self.project_manager.load_projects()

        for project in projects:

            item_text = (
                f"{project.title}"
                f"   |   "
                f"{project.date}"
            )

            self.project_list.addItem(
                item_text
            )

    # =========================================================
    # CREATE PROJECT
    # =========================================================

    def create_project(self):

        dialog = NewProjectDialog(
            self
        )

        result = dialog.exec()

        if result != QDialog.DialogCode.Accepted:

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

            project = (
                self.project_manager.create_project(
                    title,
                    date
                )
            )

            # Add the newly created project
            # immediately to the list

            self.project_list.addItem(
                f"{project.title}"
                f"   |   "
                f"{project.date}"
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Cannot Create Project",
                str(error)
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Unexpected Error",
                f"Could not create project:\n\n{error}"
            )

    # =========================================================
    # OPEN PROJECT BY DOUBLE CLICK
    # =========================================================

    def open_project(self, item):

        if item is None:

            return

        row = self.project_list.row(
            item
        )

        projects = (
            self.project_manager.load_projects()
        )

        if row < 0 or row >= len(projects):

            QMessageBox.warning(
                self,
                "Project Error",
                "The selected project could not be found."
            )

            return

        project = projects[row]

        # Tell MainWindow that a project
        # has been opened

        self.project_opened.emit(
            project
        )

    # =========================================================
    # OPEN PROJECT BUTTON
    # =========================================================

    def open_selected_project(self):

        item = self.project_list.currentItem()

        if item is None:

            QMessageBox.information(
                self,
                "Open Project",
                "Please select a project first."
            )

            return

        self.open_project(
            item
        )