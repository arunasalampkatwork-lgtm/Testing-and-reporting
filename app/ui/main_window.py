from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QToolBar,
    QMessageBox,
    QLabel,
    QWidget,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
)

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

    # =========================================================
    # INITIALISATION
    # =========================================================

    def __init__(self):

        super().__init__()

        # -----------------------------------------------------
        # WINDOW
        # -----------------------------------------------------

        self.setWindowTitle(
            "Protection Testing Suite"
        )

        self.resize(
            1400,
            850
        )

        self.setMinimumSize(
            1100,
            700
        )

        # -----------------------------------------------------
        # CURRENT PROJECT
        # -----------------------------------------------------

        self.current_project = None
        self.current_project_folder = None

        self.database = None
        self.test_service = None

        self.asset_manager = None
        self.component_manager = None

        # -----------------------------------------------------
        # PROJECT-SPECIFIC VIEW
        # -----------------------------------------------------

        self.asset_view = None

        # -----------------------------------------------------
        # GLOBAL VIEWS
        #
        # These do NOT belong to a project.
        # -----------------------------------------------------

        self.asset_explorer_view = None
        self.dashboard_view = None

        # -----------------------------------------------------
        # GLOBAL ASSET SERVICE
        # -----------------------------------------------------

        self.global_asset_service = (
            GlobalAssetService(
                PROJECTS_DIR
            )
        )

        # -----------------------------------------------------
        # CENTRAL STACK
        # -----------------------------------------------------

        self.stack = QStackedWidget()

        self.stack.setObjectName(
            "MainStack"
        )

        self.setCentralWidget(
            self.stack
        )

        # -----------------------------------------------------
        # PROJECT VIEW
        # -----------------------------------------------------

        self.project_view = ProjectView()

        self.stack.addWidget(
            self.project_view
        )

        self.project_view.project_opened.connect(
            self.open_project
        )

        # -----------------------------------------------------
        # TOOLBAR
        # -----------------------------------------------------

        self.build_toolbar()

        # -----------------------------------------------------
        # STATUS BAR
        # -----------------------------------------------------

        self.build_status_bar()

        # -----------------------------------------------------
        # APPLICATION STYLE
        # -----------------------------------------------------

        self.apply_application_style()

        # -----------------------------------------------------
        # INITIAL PAGE
        # -----------------------------------------------------

        self.stack.setCurrentWidget(
            self.project_view
        )

        self.update_status_bar()

    # =========================================================
    # TOOLBAR
    # =========================================================

    def build_toolbar(self):

        toolbar = QToolBar(
            "Main Navigation",
            self
        )

        toolbar.setObjectName(
            "MainToolbar"
        )

        toolbar.setMovable(
            False
        )

        toolbar.setFloatable(
            False
        )

        toolbar.setIconSize(
            self.style().pixelMetric(
                self.style().PixelMetric.PM_ToolBarIconSize
            ) * 1.1
            * Qt.QSize(1, 1)
            if False
            else toolbar.iconSize()
        )

        toolbar.setContentsMargins(
            8,
            4,
            8,
            4
        )

        self.addToolBar(
            Qt.ToolBarArea.TopToolBarArea,
            toolbar
        )

        # =====================================================
        # BRAND
        # =====================================================

        brand_widget = QWidget()

        brand_layout = QHBoxLayout(
            brand_widget
        )

        brand_layout.setContentsMargins(
            12,
            4,
            20,
            4
        )

        brand_layout.setSpacing(
            10
        )

        brand_icon = QLabel(
            "⚡"
        )

        brand_icon.setObjectName(
            "BrandIcon"
        )

        brand_icon.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        brand_title = QLabel(
            "Protection Testing Suite"
        )

        brand_title.setObjectName(
            "BrandTitle"
        )

        brand_title.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Preferred
        )

        brand_layout.addWidget(
            brand_icon
        )

        brand_layout.addWidget(
            brand_title
        )

        toolbar.addWidget(
            brand_widget
        )

        # -----------------------------------------------------
        # SEPARATOR
        # -----------------------------------------------------

        toolbar.addSeparator()

        # =====================================================
        # PROJECTS
        # =====================================================

        self.project_action = QAction(
            "Projects",
            self
        )

        self.project_action.setToolTip(
            "Open and manage testing projects"
        )

        self.project_action.triggered.connect(
            self.show_project_view
        )

        toolbar.addAction(
            self.project_action
        )

        # =====================================================
        # ASSET MANAGEMENT
        # =====================================================

        self.asset_management_action = QAction(
            "Asset Management",
            self
        )

        self.asset_management_action.setToolTip(
            "Browse the global asset register, configurations and test history"
        )

        self.asset_management_action.triggered.connect(
            self.show_asset_management
        )

        toolbar.addAction(
            self.asset_management_action
        )

        # =====================================================
        # REPORTS
        # =====================================================

        self.report_action = QAction(
            "Reports",
            self
        )

        self.report_action.setToolTip(
            "Generate testing reports"
        )

        self.report_action.triggered.connect(
            self.open_report_generator
        )

        toolbar.addAction(
            self.report_action
        )

        # =====================================================
        # DASHBOARD
        # =====================================================

        self.dashboard_action = QAction(
            "Dashboard",
            self
        )

        self.dashboard_action.setToolTip(
            "View testing statistics and operational overview"
        )

        self.dashboard_action.triggered.connect(
            self.show_dashboard
        )

        toolbar.addAction(
            self.dashboard_action
        )

        # =====================================================
        # SPACER
        # =====================================================

        spacer = QWidget()

        spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )

        toolbar.addWidget(
            spacer
        )

        # =====================================================
        # CURRENT PROJECT INDICATOR
        # =====================================================

        self.project_indicator = QLabel(
            "No project open"
        )

        self.project_indicator.setObjectName(
            "ProjectIndicator"
        )

        self.project_indicator.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.project_indicator.setMinimumWidth(
            180
        )

        toolbar.addWidget(
            self.project_indicator
        )

    # =========================================================
    # STATUS BAR
    # =========================================================

    def build_status_bar(self):

        status_bar = self.statusBar()

        status_bar.setObjectName(
            "MainStatusBar"
        )

        status_bar.showMessage(
            "Ready"
        )

        # -----------------------------------------------------
        # LEFT STATUS
        # -----------------------------------------------------

        self.status_message = QLabel(
            "Ready"
        )

        self.status_message.setObjectName(
            "StatusMessage"
        )

        status_bar.addWidget(
            self.status_message,
            1
        )

        # -----------------------------------------------------
        # PROJECT STATUS
        # -----------------------------------------------------

        self.status_project = QLabel(
            "Project: None"
        )

        self.status_project.setObjectName(
            "StatusProject"
        )

        status_bar.addPermanentWidget(
            self.status_project
        )

        # -----------------------------------------------------
        # VERSION
        # -----------------------------------------------------

        self.status_version = QLabel(
            "Protection Testing Suite"
        )

        self.status_version.setObjectName(
            "StatusVersion"
        )

        status_bar.addPermanentWidget(
            self.status_version
        )

    # =========================================================
    # GLOBAL STYLE
    # =========================================================

    def apply_application_style(self):

        self.setStyleSheet(
            """
            /* =================================================
               MAIN WINDOW
               ================================================= */

            QMainWindow {
                background: #1b1d20;
            }

            QStackedWidget#MainStack {
                background: #1b1d20;
            }


            /* =================================================
               TOOLBAR
               ================================================= */

            QToolBar#MainToolbar {
                background: #202328;
                border: none;
                border-bottom: 1px solid #34383d;
                padding: 6px 10px;
                spacing: 5px;
            }

            QToolBar#MainToolbar::separator {
                background: #3b4046;
                width: 1px;
                margin: 7px 8px;
            }


            /* =================================================
               BRAND
               ================================================= */

            QLabel#BrandIcon {
                background: #f39c12;
                color: #151515;
                border-radius: 7px;
                font-size: 18px;
                font-weight: 900;
                min-width: 32px;
                min-height: 32px;
                max-width: 32px;
                max-height: 32px;
            }

            QLabel#BrandTitle {
                color: #f2f2f2;
                font-size: 15px;
                font-weight: 700;
                padding-right: 6px;
            }


            /* =================================================
               NAVIGATION BUTTONS
               ================================================= */

            QToolBar#MainToolbar QToolButton {
                color: #cfd3d8;
                background: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 8px 12px;
                margin: 1px;
                font-size: 13px;
                font-weight: 600;
            }

            QToolBar#MainToolbar QToolButton:hover {
                background: #2d3238;
                color: #ffffff;
                border: 1px solid #3e444b;
            }

            QToolBar#MainToolbar QToolButton:pressed {
                background: #343a41;
            }

            QToolBar#MainToolbar QToolButton:checked {
                background: #3a3f45;
                color: #ffffff;
            }


            /* =================================================
               PROJECT INDICATOR
               ================================================= */

            QLabel#ProjectIndicator {
                color: #e6e6e6;
                background: #2b3035;
                border: 1px solid #41474e;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 600;
            }


            /* =================================================
               STATUS BAR
               ================================================= */

            QStatusBar#MainStatusBar {
                background: #202328;
                border-top: 1px solid #34383d;
                color: #9da3aa;
            }

            QLabel#StatusMessage {
                color: #9da3aa;
                padding-left: 8px;
            }

            QLabel#StatusProject {
                color: #c9cdd1;
                padding: 0 12px;
                border-left: 1px solid #3a3f44;
            }

            QLabel#StatusVersion {
                color: #777d84;
                padding: 0 10px;
                border-left: 1px solid #3a3f44;
            }


            /* =================================================
               GENERAL WIDGETS
               ================================================= */

            QWidget {
                font-family: "Segoe UI";
                font-size: 13px;
            }

            QLineEdit,
            QComboBox,
            QSpinBox,
            QDoubleSpinBox {
                background: #25292e;
                color: #e8e8e8;
                border: 1px solid #3c4248;
                border-radius: 6px;
                padding: 5px 8px;
                min-height: 28px;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QSpinBox:focus,
            QDoubleSpinBox:focus {
                border: 1px solid #f39c12;
            }

            QPushButton {
                background: #2b3035;
                color: #e5e5e5;
                border: 1px solid #41474e;
                border-radius: 6px;
                padding: 7px 14px;
                min-height: 28px;
            }

            QPushButton:hover {
                background: #343a40;
                border-color: #565d65;
            }

            QPushButton:pressed {
                background: #25292d;
            }

            QPushButton:disabled {
                color: #666b70;
                background: #24272a;
                border-color: #303438;
            }


            /* =================================================
               TABLES
               ================================================= */

            QTableWidget,
            QTableView {
                background: #24272b;
                alternate-background-color: #292d32;
                color: #e1e1e1;
                gridline-color: #383d43;
                border: 1px solid #3c4248;
                border-radius: 6px;
                selection-background-color: #3d4147;
                selection-color: #ffffff;
            }

            QHeaderView::section {
                background: #2d3237;
                color: #dfe3e6;
                border: none;
                border-right: 1px solid #41474d;
                border-bottom: 1px solid #41474d;
                padding: 7px;
                font-weight: 600;
            }


            /* =================================================
               TREE
               ================================================= */

            QTreeWidget,
            QTreeView {
                background: #24272b;
                color: #e1e1e1;
                border: 1px solid #3c4248;
                border-radius: 6px;
                outline: none;
            }

            QTreeWidget::item {
                padding: 5px;
                min-height: 25px;
            }

            QTreeWidget::item:hover {
                background: #30353a;
            }

            QTreeWidget::item:selected {
                background: #3b4046;
                color: #ffffff;
                border-left: 3px solid #f39c12;
            }


            /* =================================================
               SCROLLBARS
               ================================================= */

            QScrollBar:vertical {
                background: #202328;
                width: 10px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #444a50;
                border-radius: 5px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #565d64;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0;
            }

            QScrollBar:horizontal {
                background: #202328;
                height: 10px;
            }

            QScrollBar::handle:horizontal {
                background: #444a50;
                border-radius: 5px;
                min-width: 30px;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0;
            }


            /* =================================================
               TOOLTIP
               ================================================= */

            QToolTip {
                background: #292e33;
                color: #eeeeee;
                border: 1px solid #50575e;
                padding: 5px 7px;
            }


            /* =================================================
               MESSAGE BOX
               ================================================= */

            QMessageBox {
                background: #25292e;
            }

            QMessageBox QLabel {
                color: #eeeeee;
            }
            """
        )

    # =========================================================
    # PROJECT VIEW
    # =========================================================

    def show_project_view(self):

        self.stack.setCurrentWidget(
            self.project_view
        )

        self.status_message.setText(
            "Project management"
        )

        self.update_status_bar()

    # =========================================================
    # ASSET MANAGEMENT
    # =========================================================

    def show_asset_management(self):

        try:

            self.global_asset_service.refresh()

            if self.asset_explorer_view is None:

                self.asset_explorer_view = (
                    AssetExplorerView(
                        global_asset_service=
                            self.global_asset_service,
                        parent=self
                    )
                )

                self.stack.addWidget(
                    self.asset_explorer_view
                )

            else:

                self.asset_explorer_view.refresh()

            self.stack.setCurrentWidget(
                self.asset_explorer_view
            )

            self.status_message.setText(
                "Global asset management"
            )

            self.update_status_bar()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Asset Management Failed",
                (
                    "Unable to open Asset Management.\n\n"
                    f"{error}"
                )
            )

    # =========================================================
    # REPORT GENERATOR
    # =========================================================

    def open_report_generator(self):

        dialog = ReportGeneratorDialog(
            parent=self
        )

        dialog.exec()

        self.status_message.setText(
            "Report generator"
        )

        self.update_status_bar()

    # =========================================================
    # DASHBOARD
    # =========================================================

    def show_dashboard(self):

        try:

            self.global_asset_service.refresh()

            if self.dashboard_view is None:

                self.dashboard_view = (
                    DashboardView(
                        global_asset_service=
                            self.global_asset_service,
                        parent=self
                    )
                )

                self.stack.addWidget(
                    self.dashboard_view
                )

            else:

                self.dashboard_view.refresh()

            self.stack.setCurrentWidget(
                self.dashboard_view
            )

            self.status_message.setText(
                "Testing dashboard"
            )

            self.update_status_bar()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Dashboard Failed",
                (
                    "Unable to open Dashboard.\n\n"
                    f"{error}"
                )
            )

    # =========================================================
    # OPEN PROJECT
    # =========================================================

    def open_project(
        self,
        project
    ):

        try:

            self.current_project = project

            project_folder = (
                PROJECTS_DIR /
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
            # ASSET MANAGERS
            # =================================================

            self.asset_manager = AssetManager(
                project_folder
            )

            self.component_manager = (
                ComponentManager(
                    project_folder
                )
            )

            # =================================================
            # REMOVE OLD PROJECT ASSET VIEW
            # =================================================

            if self.asset_view is not None:

                self._remove_widget(
                    self.asset_view
                )

                self.asset_view = None

            # =================================================
            # CREATE NEW PROJECT ASSET VIEW
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
            # REFRESH GLOBAL DATA
            # =================================================

            try:

                self.global_asset_service.refresh()

                if (
                    self.asset_explorer_view
                    is not None
                ):

                    self.asset_explorer_view.refresh()

                if (
                    self.dashboard_view
                    is not None
                ):

                    self.dashboard_view.refresh()

            except Exception:
                pass

            # =================================================
            # STATUS
            # =================================================

            self.status_message.setText(
                "Project opened"
            )

            self.update_status_bar()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Open Project Failed",
                (
                    "Unable to open the project.\n\n"
                    f"{error}"
                )
            )

            raise

    # =========================================================
    # UPDATE STATUS BAR
    # =========================================================

    def update_status_bar(self):

        if self.current_project is None:

            project_name = "None"

        else:

            project_name = str(
                getattr(
                    self.current_project,
                    "title",
                    "Unknown"
                )
            )

        self.project_indicator.setText(
            f"Project: {project_name}"
        )

        self.status_project.setText(
            f"Project: {project_name}"
        )

    # =========================================================
    # REMOVE WIDGET
    # =========================================================

    def _remove_widget(
        self,
        widget
    ):

        if widget is None:
            return

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

    # =========================================================
    # CLOSE CURRENT PROJECT
    # =========================================================

    def close_current_project(self):

        # -----------------------------------------------------
        # Remove only project-specific objects.
        #
        # Asset Management and Dashboard are global.
        # -----------------------------------------------------

        self.current_project = None
        self.current_project_folder = None

        self.database = None
        self.test_service = None

        self.asset_manager = None
        self.component_manager = None

        # -----------------------------------------------------
        # Asset View
        # -----------------------------------------------------

        if self.asset_view is not None:

            self._remove_widget(
                self.asset_view
            )

            self.asset_view = None

        # -----------------------------------------------------
        # Return to projects
        # -----------------------------------------------------

        self.stack.setCurrentWidget(
            self.project_view
        )

        self.status_message.setText(
            "Project closed"
        )

        self.update_status_bar()

    # =========================================================
    # CLOSE EVENT
    # =========================================================

    def closeEvent(
        self,
        event
    ):

        # -----------------------------------------------------
        # Close any active testing dialog.
        # -----------------------------------------------------

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