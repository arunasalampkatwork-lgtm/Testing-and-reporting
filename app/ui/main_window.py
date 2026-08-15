
from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QToolBar,
)
from PySide6.QtGui import QAction

from app.ui.asset_browser_view import AssetBrowserView
from app.ui.project_view import ProjectView
from app.ui.asset_view import AssetView
from app.ui.report_generator_dialog import ReportGeneratorDialog

from app.config.settings import PROJECTS_DIR

from app.database.database import Database
from app.database.tables import create_tables

from app.services.test_service import TestService


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        # =================================================
        # WINDOW
        # =================================================

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

        # =================================================
        # ASSET BROWSER
        # =================================================

        self.asset_browser_view = AssetBrowserView(
            parent=self
        )

        self.stack.addWidget(
            self.asset_browser_view
        )

        # =================================================
        # CURRENT PROJECT VARIABLES
        # =================================================

        self.current_project = None
        self.current_project_folder = None
        self.database = None
        self.test_service = None
        self.asset_view = None

        # =================================================
        # TOOLBAR
        # =================================================

        self.build_toolbar()

        self.stack.setCurrentWidget(
            self.project_view
        )

    # =====================================================
    # TOOLBAR
    # =====================================================

    def build_toolbar(self):

        toolbar = QToolBar(
            "Navigation",
            self
        )

        toolbar.setMovable(
            False
        )

        self.addToolBar(
            toolbar
        )

        # -------------------------------------------------
        # PROJECTS
        # -------------------------------------------------

        project_action = QAction(
            "Projects",
            self
        )

        project_action.triggered.connect(
            self.show_project_view
        )

        toolbar.addAction(
            project_action
        )

        # -------------------------------------------------
        # ASSET DATABASE
        # -------------------------------------------------

        asset_browser_action = QAction(
            "Asset Database",
            self
        )

        asset_browser_action.triggered.connect(
            self.show_asset_browser
        )

        toolbar.addAction(
            asset_browser_action
        )

        # -------------------------------------------------
        # REPORTS
        # -------------------------------------------------

        report_action = QAction(
            "Reports",
            self
        )

        report_action.triggered.connect(
            self.open_report_generator
        )

        toolbar.addAction(
            report_action
        )

    # =====================================================
    # SHOW PROJECT VIEW
    # =====================================================

    def show_project_view(self):

        self.stack.setCurrentWidget(
            self.project_view
        )

    # =====================================================
    # SHOW ASSET BROWSER
    # =====================================================

    def show_asset_browser(self):

        try:

            if hasattr(
                self.asset_browser_view,
                "refresh"
            ):

                self.asset_browser_view.refresh()

        except Exception:
            pass

        self.stack.setCurrentWidget(
            self.asset_browser_view
        )

    # =====================================================
    # REPORT GENERATOR
    # =====================================================

    def open_report_generator(self):

        dialog = ReportGeneratorDialog(
            parent=self
        )

        dialog.exec()

    # =====================================================
    # OPEN PROJECT
    # =====================================================

    def open_project(
        self,
        project
    ):

        self.current_project = project

        project_folder = (
            PROJECTS_DIR
            /
            project.title
        )

        self.current_project_folder = (
            project_folder
        )

        project_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        # =================================================
        # DATABASE
        # =================================================

        database_path = (
            project_folder
            /
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
        # REMOVE OLD ASSET VIEW
        # =================================================

        if self.asset_view is not None:

            try:

                old_index = (
                    self.stack.indexOf(
                        self.asset_view
                    )
                )

                if old_index >= 0:

                    self.stack.removeWidget(
                        self.asset_view
                    )

                self.asset_view.deleteLater()

            except RuntimeError:
                pass

            self.asset_view = None

        # =================================================
        # CREATE ASSET VIEW
        # =================================================

        self.asset_view = AssetView(
            project_folder,
            project,
            self.test_service,
            parent=self
        )

        self.stack.addWidget(
            self.asset_view
        )

        self.stack.setCurrentWidget(
            self.asset_view
        )

        # =================================================
        # REFRESH GLOBAL ASSET BROWSER
        # =================================================

        try:

            if hasattr(
                self.asset_browser_view,
                "refresh"
            ):

                self.asset_browser_view.refresh()

        except Exception:
            pass

    # =====================================================
    # CLOSE CURRENT PROJECT
    # =====================================================

    def close_current_project(self):

        self.current_project = None
        self.current_project_folder = None
        self.database = None
        self.test_service = None

        if self.asset_view is not None:

            try:

                index = (
                    self.stack.indexOf(
                        self.asset_view
                    )
                )

                if index >= 0:

                    self.stack.removeWidget(
                        self.asset_view
                    )

                self.asset_view.deleteLater()

            except RuntimeError:
                pass

            self.asset_view = None

        self.stack.setCurrentWidget(
            self.project_view
        )

    # =====================================================
    # CLOSE EVENT
    # =====================================================

    def closeEvent(
        self,
        event
    ):

        if self.asset_view is not None:

            try:

                if hasattr(
                    self.asset_view,
                    "close_testing_dialog"
                ):

                    self.asset_view.close_testing_dialog()

            except Exception:
                pass

        event.accept()
