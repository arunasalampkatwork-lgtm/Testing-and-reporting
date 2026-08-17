from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QToolBar,
    QMessageBox,
)
from PySide6.QtGui import QAction

from app.ui.asset_browser_view import AssetBrowserView
from app.ui.project_view import ProjectView
from app.ui.asset_view import AssetView
from app.ui.report_generator_dialog import ReportGeneratorDialog
from app.ui.asset_explorer_view import AssetExplorerView
from app.ui.dashboard_view import DashboardView

from app.config.settings import PROJECTS_DIR

from app.database.database import Database
from app.database.tables import create_tables

from app.services.test_service import TestService
from app.services.asset_manager import AssetManager
from app.services.component_manager import ComponentManager
from app.services.global_asset_service import (
    GlobalAssetService
)

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

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # =================================================
        # PROJECT VIEW
        # =================================================

        self.project_view = ProjectView()
        self.stack.addWidget(self.project_view)

        self.project_view.project_opened.connect(
            self.open_project
        )
        self.global_asset_service = (
            GlobalAssetService(
                PROJECTS_DIR
            )
        )

        # =================================================
        # GLOBAL ASSET DATABASE
        # =================================================

        self.asset_browser_view = AssetBrowserView(
            parent=self
        )

        self.stack.addWidget(
            self.asset_browser_view
        )

        # =================================================
        # CURRENT PROJECT
        # =================================================

        self.current_project = None
        self.current_project_folder = None
        self.database = None
        self.test_service = None
        self.asset_view = None

        self.asset_manager = None
        self.component_manager = None
        self.asset_explorer_view = None
        self.dashboard_view = None

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

        toolbar.setMovable(False)
        self.addToolBar(toolbar)

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

        toolbar.addAction(project_action)

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

        toolbar.addAction(asset_browser_action)

        # -------------------------------------------------
        # ASSET EXPLORER
        # -------------------------------------------------

        self.asset_explorer_action = QAction(
            "Asset Explorer",
            self
        )

        self.asset_explorer_action.triggered.connect(
            self.show_asset_explorer
        )

        toolbar.addAction(
            self.asset_explorer_action
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

        toolbar.addAction(report_action)

        # -------------------------------------------------
        # DASHBOARD
        # -------------------------------------------------

        self.dashboard_action = QAction(
            "Dashboard",
            self
        )

        self.dashboard_action.triggered.connect(
            self.show_dashboard
        )

        toolbar.addAction(
            self.dashboard_action
        )

    # =====================================================
    # PROJECT VIEW
    # =====================================================

    def show_project_view(self):
        self.stack.setCurrentWidget(
            self.project_view
        )

    # =====================================================
    # ASSET DATABASE
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
    # ASSET EXPLORER
    # =====================================================

    # =====================================================
    # ASSET EXPLORER
    # =====================================================

    def show_asset_explorer(self):

        try:

            # -------------------------------------------------
            # UNIVERSAL EXPLORER
            #
            # No project needs to be selected.
            # The explorer uses GlobalAssetService.
            # -------------------------------------------------

            self.global_asset_service.refresh()

            # -------------------------------------------------
            # CREATE VIEW
            # -------------------------------------------------

            if self.asset_explorer_view is None:

                self.asset_explorer_view = AssetExplorerView(
                    global_asset_service=self.global_asset_service,
                    parent=self
                )

                self.stack.addWidget(
                    self.asset_explorer_view
                )

            # -------------------------------------------------
            # REFRESH EXISTING VIEW
            # -------------------------------------------------

            else:

                self.asset_explorer_view.refresh()

            # -------------------------------------------------
            # SHOW
            # -------------------------------------------------

            self.stack.setCurrentWidget(
                self.asset_explorer_view
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Asset Explorer Failed",
                f"Unable to open Asset Explorer:\n\n{error}"
            )

            raise
    # =====================================================
    # REPORT GENERATOR
    # =====================================================

    def open_report_generator(self):

        dialog = ReportGeneratorDialog(
            parent=self
        )

        dialog.exec()

    # =====================================================
    # DASHBOARD
    # =====================================================

    def show_dashboard(self):

        try:

            self.global_asset_service.refresh()

            if self.dashboard_view is None:

                self.dashboard_view = DashboardView(
                    global_asset_service=self.global_asset_service,
                    parent=self
                )

                self.stack.addWidget(
                    self.dashboard_view
                )

            else:

                self.dashboard_view.refresh()

            self.stack.setCurrentWidget(
                self.dashboard_view
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Dashboard Failed",
                f"Unable to open Dashboard:\n\n{error}"
            )
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
            / project.title
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
            / "testing.db"
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
        # ASSET MANAGERS
        # =================================================

        self.asset_manager = AssetManager(
            project_folder
        )

        self.component_manager = ComponentManager(
            project_folder
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
        # REMOVE OLD EXPLORER
        # =================================================

        if self.asset_explorer_view is not None:

            try:
                index = (
                    self.stack.indexOf(
                        self.asset_explorer_view
                    )
                )

                if index >= 0:
                    self.stack.removeWidget(
                        self.asset_explorer_view
                    )

                self.asset_explorer_view.deleteLater()

            except RuntimeError:
                pass

            self.asset_explorer_view = None

        # =================================================
        # REMOVE OLD DASHBOARD
        # =================================================

        if self.dashboard_view is not None:

            try:
                index = (
                    self.stack.indexOf(
                        self.dashboard_view
                    )
                )

                if index >= 0:
                    self.stack.removeWidget(
                        self.dashboard_view
                    )

                self.dashboard_view.deleteLater()

            except RuntimeError:
                pass

            self.dashboard_view = None

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
        self.asset_manager = None
        self.component_manager = None

        for attribute_name in (
            "asset_view",
            "asset_explorer_view",
            "dashboard_view",
        ):

            widget = getattr(
                self,
                attribute_name,
                None
            )

            if widget is None:
                continue

            try:

                index = (
                    self.stack.indexOf(
                        widget
                    )
                )

                if index >= 0:
                    self.stack.removeWidget(
                        widget
                    )

                widget.deleteLater()

            except RuntimeError:
                pass

            setattr(
                self,
                attribute_name,
                None
            )

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
