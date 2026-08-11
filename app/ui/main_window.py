from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget
)

from app.ui.project_view import ProjectView
from app.ui.asset_view import AssetView

from app.config.settings import PROJECTS_DIR

from app.database.database import Database
from app.database.tables import create_tables

from app.services.test_service import TestService


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Protection Testing Suite"
        )

        self.resize(
            1200,
            800
        )

        # =================================================
        # MAIN STACK
        # =================================================

        self.stack = QStackedWidget()

        self.setCentralWidget(
            self.stack
        )

        # =================================================
        # PROJECT VIEW
        # =================================================

        self.project_view = ProjectView()

        self.stack.addWidget(
            self.project_view
        )

        self.project_view.project_opened.connect(
            self.open_project
        )

        self.stack.setCurrentWidget(
            self.project_view
        )

        # =================================================
        # CURRENT PROJECT VARIABLES
        # =================================================

        self.current_project = None

        self.current_project_folder = None

        self.database = None

        self.test_service = None

        self.asset_view = None

    # =====================================================
    # OPEN PROJECT
    # =====================================================

    def open_project(self, project):

        self.current_project = project

        project_folder = (
            PROJECTS_DIR /
            project.title
        )

        self.current_project_folder = (
            project_folder
        )

        # =================================================
        # DATABASE
        # =================================================

        database_path = (
            project_folder /
            "testing.db"
        )

        self.database = Database(
            database_path
        )

        create_tables(
            self.database
        )

        self.test_service = TestService(
            self.database
        )

        # =================================================
        # ASSET VIEW
        # =================================================

        self.asset_view = AssetView(
            project_folder,
            project,
            self.test_service
        )

        self.stack.addWidget(
            self.asset_view
        )

        self.stack.setCurrentWidget(
            self.asset_view
        )