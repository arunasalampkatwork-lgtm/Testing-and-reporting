from pathlib import Path
import json
import sqlite3

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QMessageBox,
    QSplitter,
    QHeaderView,
)

from app.config.settings import PROJECTS_DIR
from app.services.asset_library_manager import AssetLibraryManager


class AssetBrowserView(QWidget):

    """
    Global, project-independent asset browser.

    Assets are read from the existing global asset library.
    Test history is collected from all project databases by
    resolving each project's local panel node through asset_id.

    This means existing project/test architecture remains intact.
    """

    back_requested = Signal()

    def __init__(
        self,
        parent=None
    ):

        super().__init__(parent)

        self.asset_library = AssetLibraryManager()

        self.setWindowTitle(
            "Global Asset Database"
        )

        self.resize(
            1200,
            750
        )

        self.build_ui()
        self.refresh()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        header = QLabel(
            "Global Asset Database"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(header)

        splitter = QSplitter(
            Qt.Orientation.Vertical
        )

        # -------------------------------------------------
        # ASSET LIST
        # -------------------------------------------------

        self.asset_tree = QTreeWidget()

        self.asset_tree.setHeaderLabels(
            [
                "Asset",
                "Type",
                "Asset Tag",
                "Manufacturer",
                "Model",
                "Serial Number",
                "Asset ID",
            ]
        )

        self.asset_tree.setSelectionMode(
            QTreeWidget.SelectionMode.SingleSelection
        )

        self.asset_tree.itemSelectionChanged.connect(
            self.asset_selected
        )

        splitter.addWidget(
            self.asset_tree
        )

        # -------------------------------------------------
        # TEST HISTORY
        # -------------------------------------------------

        history_widget = QWidget()

        history_layout = QVBoxLayout(
            history_widget
        )

        history_label = QLabel(
            "Test History"
        )

        history_label.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
            }
            """
        )

        history_layout.addWidget(
            history_label
        )

        self.test_table = QTableWidget()

        self.test_table.setColumnCount(8)

        self.test_table.setHorizontalHeaderLabels(
            [
                "Date",
                "Project",
                "Panel",
                "Test Type",
                "Protection / Component",
                "Result",
                "Remarks",
                "Test ID",
            ]
        )

        self.test_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.test_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.test_table.setAlternatingRowColors(
            True
        )

        self.test_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        history_layout.addWidget(
            self.test_table
        )

        splitter.addWidget(
            history_widget
        )

        splitter.setSizes(
            [350, 350]
        )

        layout.addWidget(
            splitter
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        buttons = QHBoxLayout()

        self.refresh_button = QPushButton(
            "Refresh"
        )

        self.close_button = QPushButton(
            "Close"
        )

        self.refresh_button.clicked.connect(
            self.refresh
        )

        self.close_button.clicked.connect(
            self.back_requested.emit
        )

        buttons.addWidget(
            self.refresh_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.close_button
        )

        layout.addLayout(
            buttons
        )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(self):

        self.asset_library.load()

        self.load_assets()

    # =====================================================
    # LOAD ASSETS
    # =====================================================

    def load_assets(self):

        self.asset_tree.clear()
        self.test_table.setRowCount(0)

        assets = self.asset_library.get_all_assets()

        assets = sorted(
            assets,
            key=lambda asset: (
                str(
                    asset.get(
                        "asset_type",
                        ""
                    )
                ),
                str(
                    asset.get(
                        "asset_tag",
                        ""
                    )
                ),
            )
        )

        for asset in assets:

            item = QTreeWidgetItem()

            item.setText(
                0,
                str(
                    asset.get(
                        "name",
                        ""
                    )
                )
            )

            item.setText(
                1,
                str(
                    asset.get(
                        "asset_type",
                        ""
                    )
                )
            )

            item.setText(
                2,
                str(
                    asset.get(
                        "asset_tag",
                        ""
                    )
                )
            )

            item.setText(
                3,
                str(
                    asset.get(
                        "manufacturer",
                        ""
                    )
                )
            )

            item.setText(
                4,
                str(
                    asset.get(
                        "model",
                        ""
                    )
                )
            )

            item.setText(
                5,
                str(
                    asset.get(
                        "serial_number",
                        ""
                    )
                )
            )

            item.setText(
                6,
                str(
                    asset.get(
                        "asset_id",
                        ""
                    )
                )
            )

            item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                asset.get(
                    "asset_id"
                )
            )

            self.asset_tree.addTopLevelItem(
                item
            )

        self.asset_tree.resizeColumnToContents(0)
        self.asset_tree.resizeColumnToContents(1)
        self.asset_tree.resizeColumnToContents(2)

    # =====================================================
    # SELECTED ASSET
    # =====================================================

    def get_selected_asset(self):

        item = self.asset_tree.currentItem()

        if item is None:
            return None

        asset_id = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if not asset_id:
            return None

        return self.asset_library.get_asset(
            asset_id
        )

    # =====================================================
    # ASSET SELECTED
    # =====================================================

    def asset_selected(self):

        asset = self.get_selected_asset()

        if asset is None:

            self.test_table.setRowCount(0)

            return

        self.load_test_history(
            asset
        )

    # =====================================================
    # PROJECT NAME
    # =====================================================

    @staticmethod
    def get_project_name(
        project_folder
    ):

        project_file = (
            project_folder / "project.json"
        )

        if project_file.exists():

            try:

                with open(
                    project_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    data = json.load(file)

                return str(
                    data.get(
                        "title",
                        project_folder.name
                    )
                )

            except (
                json.JSONDecodeError,
                TypeError,
                OSError
            ):
                pass

        return project_folder.name

    # =====================================================
    # LOAD TEST HISTORY
    # =====================================================

    def load_test_history(
        self,
        asset
    ):

        self.test_table.setRowCount(0)

        asset_id = asset.get(
            "asset_id"
        )

        if not asset_id:
            return

        for project_folder in self.get_project_folders():

            assets_data = self.read_json(
                project_folder / "assets.json"
            )

            if not isinstance(
                assets_data,
                list
            ):
                continue

            panel_ids = []

            for node in assets_data:

                if str(
                    node.get(
                        "node_type",
                        ""
                    )
                ).upper() != "PANEL":
                    continue

                if (
                    node.get(
                        "asset_id"
                    )
                    == asset_id
                ):

                    panel_ids.append(
                        node.get(
                            "node_id"
                        )
                    )

            if not panel_ids:
                continue

            project_name = self.get_project_name(
                project_folder
            )

            components_data = self.read_json(
                project_folder / "components.json"
            )

            component_names = {}

            if isinstance(
                components_data,
                list
            ):

                component_names = {
                    item.get("component_id"):
                        item.get("name", "")
                    for item in components_data
                }

            database_file = (
                project_folder / "testing.db"
            )

            if not database_file.exists():
                continue

            try:

                connection = sqlite3.connect(
                    database_file
                )

                cursor = connection.cursor()

                for panel_id in panel_ids:

                    # -------------------------------------------------
                    # PROTECTION TESTS
                    # -------------------------------------------------

                    cursor.execute(
                        """
                        SELECT
                            test_id,
                            test_date,
                            protection_code,
                            relay_id,
                            result,
                            remarks
                        FROM protection_tests
                        WHERE panel_id = ?
                        ORDER BY test_date DESC
                        """,
                        (panel_id,)
                    )

                    for row in cursor.fetchall():

                        self.add_history_row(
                            date=row[1],
                            project=project_name,
                            panel=asset.get(
                                "name",
                                ""
                            ),
                            test_type="PROTECTION TEST",
                            protection_or_component=(
                                f"{row[2]} | "
                                f"{component_names.get(row[3], row[3])}"
                            ),
                            result=row[4],
                            remarks=row[5],
                            test_id=row[0]
                        )

                    # -------------------------------------------------
                    # COMPONENT TESTS
                    # -------------------------------------------------

                    cursor.execute(
                        """
                        SELECT
                            test_id,
                            test_date,
                            component_id,
                            test_type,
                            result,
                            remarks
                        FROM component_tests
                        WHERE panel_id = ?
                        ORDER BY test_date DESC
                        """,
                        (panel_id,)
                    )

                    for row in cursor.fetchall():

                        self.add_history_row(
                            date=row[1],
                            project=project_name,
                            panel=asset.get(
                                "name",
                                ""
                            ),
                            test_type="COMPONENT TEST",
                            protection_or_component=(
                                component_names.get(
                                    row[2],
                                    row[2]
                                )
                            ),
                            result=row[4],
                            remarks=row[5],
                            test_id=row[0]
                        )

                connection.close()

            except sqlite3.Error as error:

                QMessageBox.warning(
                    self,
                    "Database Error",
                    f"Could not read {project_folder.name}:\n{error}"
                )

    # =====================================================
    # PROJECT FOLDERS
    # =====================================================

    @staticmethod
    def get_project_folders():

        if not PROJECTS_DIR.exists():
            return []

        return [
            folder
            for folder in PROJECTS_DIR.iterdir()
            if folder.is_dir()
        ]

    # =====================================================
    # JSON HELPER
    # =====================================================

    @staticmethod
    def read_json(
        path
    ):

        if not path.exists():
            return None

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except (
            json.JSONDecodeError,
            TypeError,
            OSError
        ):

            return None

    # =====================================================
    # ADD HISTORY ROW
    # =====================================================

    def add_history_row(
        self,
        date,
        project,
        panel,
        test_type,
        protection_or_component,
        result,
        remarks,
        test_id
    ):

        row = self.test_table.rowCount()

        self.test_table.insertRow(
            row
        )

        values = [
            date,
            project,
            panel,
            test_type,
            protection_or_component,
            result,
            remarks,
            test_id
        ]

        for column, value in enumerate(values):

            self.test_table.setItem(
                row,
                column,
                QTableWidgetItem(
                    str(value or "")
                )
            )
