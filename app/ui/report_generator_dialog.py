
from pathlib import Path
import json

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QComboBox,
    QDateEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QCheckBox,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QLineEdit,
)

from app.config.settings import PROJECTS_DIR
from app.database.database import Database
from app.database.tables import create_tables
from app.services.test_service import TestService
from app.services.asset_manager import AssetManager
from app.services.component_manager import ComponentManager
from app.services.panel_report_service import PanelReportService


class ReportGeneratorDialog(QDialog):

    """
    Batch panel report generator.

    Workflow:
        Project -> Test Date -> Panels Tested -> Select All
        -> Output Folder -> Generate Selected Reports

    Only panels having at least one protection/component test on the
    selected date are displayed.
    """

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(parent)

        self.setWindowTitle(
            "Panel Report Generator"
        )

        self.resize(
            1050,
            720
        )

        self.project_contexts = {}

        self.build_ui()
        self.load_projects()

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = QLabel(
            "PANEL REPORT GENERATOR"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: bold;
                padding: 8px 4px;
            }
            """
        )

        layout.addWidget(header)

        description = QLabel(
            "Select a project and test date. The list below contains "
            "only panels with tests recorded on that date."
        )

        description.setWordWrap(True)
        description.setStyleSheet(
            """
            QLabel {
                color: #999999;
                padding: 0 4px 10px 4px;
            }
            """
        )

        layout.addWidget(description)

        # -------------------------------------------------
        # FILTERS
        # -------------------------------------------------

        filter_form = QFormLayout()

        self.project_combo = QComboBox()

        self.project_combo.currentIndexChanged.connect(
            self.on_project_changed
        )

        filter_form.addRow(
            "Project:",
            self.project_combo
        )

        self.date_edit = QDateEdit()

        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat(
            "dd-MM-yyyy"
        )
        self.date_edit.setDate(
            QDate.currentDate()
        )

        self.date_edit.dateChanged.connect(
            self.load_panels
        )

        filter_form.addRow(
            "Test Date:",
            self.date_edit
        )

        layout.addLayout(filter_form)

        # -------------------------------------------------
        # PANEL TABLE
        # -------------------------------------------------

        self.select_all = QCheckBox(
            "Select All"
        )

        self.select_all.setTristate(True)

        self.select_all.stateChanged.connect(
            self.toggle_select_all
        )

        layout.addWidget(
            self.select_all
        )

        self.panel_table = QTableWidget()

        self.panel_table.setColumnCount(
            5
        )

        self.panel_table.setHorizontalHeaderLabels(
            [
                "",
                "Panel",
                "Switchboard",
                "Substation",
                "Tests",
            ]
        )

        self.panel_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.panel_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.panel_table.setAlternatingRowColors(
            True
        )

        self.panel_table.verticalHeader().setVisible(
            False
        )

        header = self.panel_table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Fixed
        )

        self.panel_table.setColumnWidth(
            0,
            45
        )

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Stretch
        )

        header.setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.Fixed
        )

        self.panel_table.setColumnWidth(
            4,
            80
        )

        self.panel_table.itemChanged.connect(
            self.update_select_all_state
        )

        layout.addWidget(
            self.panel_table,
            1
        )

        # -------------------------------------------------
        # SELECTED COUNT
        # -------------------------------------------------

        self.selected_label = QLabel(
            "Selected: 0 panels"
        )

        self.selected_label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                padding: 5px;
            }
            """
        )

        layout.addWidget(
            self.selected_label
        )

        # -------------------------------------------------
        # OUTPUT FOLDER
        # -------------------------------------------------

        output_layout = QHBoxLayout()

        self.output_edit = QLineEdit()

        self.output_edit.setPlaceholderText(
            "Select a folder for the generated reports"
        )

        browse_button = QPushButton(
            "Browse..."
        )

        browse_button.clicked.connect(
            self.choose_output_folder
        )

        output_layout.addWidget(
            self.output_edit,
            1
        )

        output_layout.addWidget(
            browse_button
        )

        layout.addLayout(output_layout)

        # -------------------------------------------------
        # PROGRESS
        # -------------------------------------------------

        self.progress = QProgressBar()

        self.progress.setRange(
            0,
            100
        )

        self.progress.setValue(
            0
        )

        self.progress.setVisible(
            False
        )

        layout.addWidget(
            self.progress
        )

        self.status_label = QLabel(
            "Ready"
        )

        self.status_label.setStyleSheet(
            "color: #999999;"
        )

        layout.addWidget(
            self.status_label
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        buttons = QHBoxLayout()

        self.refresh_button = QPushButton(
            "Refresh"
        )

        self.generate_button = QPushButton(
            "Generate Selected Reports"
        )

        close_button = QPushButton(
            "Close"
        )

        self.refresh_button.clicked.connect(
            self.load_panels
        )

        self.generate_button.clicked.connect(
            self.generate_reports
        )

        close_button.clicked.connect(
            self.reject
        )

        buttons.addWidget(
            self.refresh_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.generate_button
        )

        buttons.addWidget(
            close_button
        )

        layout.addLayout(buttons)

        self.setStyleSheet(
            """
            QDialog {
                background-color: #202020;
            }

            QTableWidget {
                border: 1px solid #454545;
                border-radius: 6px;
                background-color: #252525;
                gridline-color: #454545;
            }

            QHeaderView::section {
                background-color: #353535;
                padding: 9px;
                font-weight: bold;
                border: 1px solid #454545;
            }

            QTableWidget::item {
                padding: 7px;
            }

            QComboBox,
            QDateEdit,
            QLineEdit {
                min-height: 34px;
                padding: 4px 8px;
            }

            QPushButton {
                min-height: 36px;
                padding: 6px 14px;
            }
            """
        )

    # =====================================================
    # PROJECTS
    # =====================================================

    def load_projects(self):

        self.project_combo.blockSignals(True)
        self.project_combo.clear()

        projects_dir = Path(
            PROJECTS_DIR
        )

        if not projects_dir.exists():

            self.project_combo.blockSignals(False)

            self.status_label.setText(
                "Projects folder not found."
            )

            return

        project_folders = sorted(
            [
                path
                for path in projects_dir.iterdir()
                if path.is_dir()
            ],
            key=lambda path: path.name.lower()
        )

        for folder in project_folders:

            title = self.get_project_title(
                folder
            )

            self.project_combo.addItem(
                title,
                str(folder)
            )

        self.project_combo.blockSignals(False)

        if self.project_combo.count():

            self.on_project_changed()

        else:

            self.status_label.setText(
                "No projects found."
            )

    @staticmethod
    def get_project_title(
        project_folder
    ):

        project_file = (
            Path(project_folder)
            /
            "project.json"
        )

        if project_file.exists():

            try:

                with open(
                    project_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    data = json.load(file)

                title = (
                    data.get("title")
                    or
                    data.get("name")
                )

                if title:
                    return str(title)

            except (
                OSError,
                json.JSONDecodeError,
                TypeError
            ):
                pass

        return Path(
            project_folder
        ).name

    # =====================================================
    # PROJECT CHANGE
    # =====================================================

    def on_project_changed(
        self,
        index=None
    ):

        self.load_panels()

    # =====================================================
    # LOAD PROJECT CONTEXT
    # =====================================================

    def get_project_context(
        self,
        project_folder
    ):

        key = str(
            Path(project_folder).resolve()
        )

        if key in self.project_contexts:

            return self.project_contexts[key]

        project_folder = Path(
            project_folder
        )

        database_path = (
            project_folder
            /
            "testing.db"
        )

        if not database_path.exists():

            return None

        database = Database(
            database_path
        )

        create_tables(
            database
        )

        test_service = TestService(
            database
        )

        asset_manager = AssetManager(
            project_folder
        )

        component_manager = ComponentManager(
            project_folder
        )

        context = {
            "folder": project_folder,
            "database": database,
            "test_service": test_service,
            "asset_manager": asset_manager,
            "component_manager": component_manager,
        }

        self.project_contexts[key] = context

        return context

    # =====================================================
    # LOAD PANELS FOR DATE
    # =====================================================

    def load_panels(
        self
    ):

        self.panel_table.blockSignals(True)
        self.panel_table.setRowCount(0)
        self.panel_table.blockSignals(False)

        self.select_all.blockSignals(True)
        self.select_all.setCheckState(
            Qt.CheckState.Unchecked
        )
        self.select_all.blockSignals(False)

        self.update_selected_count()

        project_folder = (
            self.project_combo.currentData()
        )

        if not project_folder:

            return

        context = self.get_project_context(
            project_folder
        )

        if context is None:

            self.status_label.setText(
                "The selected project has no testing database."
            )

            return

        report_date = (
            self.date_edit
            .date()
            .toString(
                "yyyy-MM-dd"
            )
        )

        try:

            test_service = context[
                "test_service"
            ]

            asset_manager = context[
                "asset_manager"
            ]

            panel_ids = set()

            # -------------------------------------------------
            # PROTECTION TESTS
            # -------------------------------------------------

            for row in (
                test_service.get_all_tests()
                or []
            ):

                if len(row) < 6:
                    continue

                if self.date_matches(
                    row[5],
                    report_date
                ):

                    panel_ids.add(
                        row[2]
                    )

            # -------------------------------------------------
            # COMPONENT TESTS
            # -------------------------------------------------

            for row in (
                test_service.get_all_component_tests()
                or []
            ):

                if len(row) < 6:
                    continue

                if self.date_matches(
                    row[5],
                    report_date
                ):

                    panel_ids.add(
                        row[2]
                    )

            panels = []

            for panel_id in panel_ids:

                panel = (
                    asset_manager.get_node(
                        panel_id
                    )
                )

                if panel is None:
                    continue

                if str(
                    getattr(
                        panel,
                        "node_type",
                        ""
                    )
                ).upper() != "PANEL":

                    continue

                hierarchy = (
                    self.get_hierarchy(
                        asset_manager,
                        panel
                    )
                )

                test_count = (
                    self.count_tests_for_panel(
                        test_service,
                        panel_id,
                        report_date
                    )
                )

                panels.append({
                    "panel": panel,
                    "panel_id": panel_id,
                    "substation": hierarchy[
                        "substation"
                    ],
                    "switchboard": hierarchy[
                        "switchboard"
                    ],
                    "test_count": test_count,
                })

            panels.sort(
                key=lambda item: (
                    item["substation"].lower(),
                    item["switchboard"].lower(),
                    str(
                        getattr(
                            item["panel"],
                            "name",
                            ""
                        )
                    ).lower()
                )
            )

            self.panel_table.blockSignals(True)

            for data in panels:

                row = (
                    self.panel_table.rowCount()
                )

                self.panel_table.insertRow(
                    row
                )

                checkbox = QTableWidgetItem()

                checkbox.setFlags(
                    checkbox.flags()
                    |
                    Qt.ItemFlag.ItemIsUserCheckable
                )

                checkbox.setCheckState(
                    Qt.CheckState.Unchecked
                )

                checkbox.setData(
                    Qt.ItemDataRole.UserRole,
                    data
                )

                self.panel_table.setItem(
                    row,
                    0,
                    checkbox
                )

                self.set_table_item(
                    row,
                    1,
                    getattr(
                        data["panel"],
                        "name",
                        ""
                    )
                )

                self.set_table_item(
                    row,
                    2,
                    data["switchboard"]
                )

                self.set_table_item(
                    row,
                    3,
                    data["substation"]
                )

                self.set_table_item(
                    row,
                    4,
                    str(
                        data["test_count"]
                    )
                )

            self.panel_table.blockSignals(False)

            self.status_label.setText(
                f"{len(panels)} panel(s) tested on "
                f"{report_date}."
            )

            self.update_selected_count()

        except Exception as error:

            self.panel_table.blockSignals(False)

            self.status_label.setText(
                "Unable to load tested panels."
            )

            QMessageBox.critical(
                self,
                "Report Generator Error",
                str(error)
            )

    # =====================================================
    # TABLE HELPERS
    # =====================================================

    def set_table_item(
        self,
        row,
        column,
        value
    ):

        item = QTableWidgetItem(
            str(
                value
                if value is not None
                else ""
            )
        )

        self.panel_table.setItem(
            row,
            column,
            item
        )

    @staticmethod
    def date_matches(
        test_date,
        selected_date
    ):

        if not test_date:
            return False

        value = str(
            test_date
        ).strip()

        if "T" in value:
            value = value.split("T")[0]

        elif " " in value:
            value = value.split(" ")[0]

        return value == str(
            selected_date
        )

    def count_tests_for_panel(
        self,
        test_service,
        panel_id,
        report_date
    ):

        count = 0

        for row in (
            test_service.get_all_tests()
            or []
        ):

            if (
                len(row) >= 6
                and row[2] == panel_id
                and self.date_matches(
                    row[5],
                    report_date
                )
            ):

                count += 1

        for row in (
            test_service.get_all_component_tests()
            or []
        ):

            if (
                len(row) >= 6
                and row[2] == panel_id
                and self.date_matches(
                    row[5],
                    report_date
                )
            ):

                count += 1

        return count

    @staticmethod
    def get_hierarchy(
        asset_manager,
        panel
    ):

        substation = ""
        switchboard = ""

        current = panel

        for _ in range(10):

            if current is None:
                break

            node_type = str(
                getattr(
                    current,
                    "node_type",
                    ""
                )
            ).upper()

            name = str(
                getattr(
                    current,
                    "name",
                    ""
                )
                or ""
            ).strip()

            if node_type == "SWITCHBOARD":
                switchboard = name

            elif node_type == "SUBSTATION":
                substation = name

            parent_id = getattr(
                current,
                "parent_id",
                None
            )

            if parent_id is None:
                break

            current = asset_manager.get_node(
                parent_id
            )

        return {
            "substation": substation,
            "switchboard": switchboard,
        }

    # =====================================================
    # SELECT ALL
    # =====================================================

    def toggle_select_all(
        self,
        state
    ):

        if state == Qt.CheckState.PartiallyChecked.value:
            return

        checked = (
            state
            == Qt.CheckState.Checked.value
        )

        self.panel_table.blockSignals(True)

        for row in range(
            self.panel_table.rowCount()
        ):

            item = self.panel_table.item(
                row,
                0
            )

            if item is not None:

                item.setCheckState(
                    Qt.CheckState.Checked
                    if checked
                    else Qt.CheckState.Unchecked
                )

        self.panel_table.blockSignals(False)

        self.update_selected_count()

    def update_select_all_state(
        self,
        item
    ):

        if item.column() != 0:
            return

        self.update_selected_count()

        total = (
            self.panel_table.rowCount()
        )

        checked = 0

        for row in range(total):

            cell = self.panel_table.item(
                row,
                0
            )

            if (
                cell is not None
                and cell.checkState()
                == Qt.CheckState.Checked
            ):

                checked += 1

        self.select_all.blockSignals(True)

        if total == 0 or checked == 0:

            self.select_all.setCheckState(
                Qt.CheckState.Unchecked
            )

        elif checked == total:

            self.select_all.setCheckState(
                Qt.CheckState.Checked
            )

        else:

            self.select_all.setCheckState(
                Qt.CheckState.PartiallyChecked
            )

        self.select_all.blockSignals(False)

    def update_selected_count(
        self
    ):

        count = 0

        for row in range(
            self.panel_table.rowCount()
        ):

            item = self.panel_table.item(
                row,
                0
            )

            if (
                item is not None
                and item.checkState()
                == Qt.CheckState.Checked
            ):

                count += 1

        self.selected_label.setText(
            f"Selected: {count} panel(s)"
        )

    # =====================================================
    # OUTPUT FOLDER
    # =====================================================

    def choose_output_folder(
        self
    ):

        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Report Output Folder"
        )

        if folder:

            self.output_edit.setText(
                folder
            )

    # =====================================================
    # SELECTED PANELS
    # =====================================================

    def get_selected_panels(
        self
    ):

        selected = []

        for row in range(
            self.panel_table.rowCount()
        ):

            checkbox = self.panel_table.item(
                row,
                0
            )

            if (
                checkbox is None
                or checkbox.checkState()
                != Qt.CheckState.Checked
            ):

                continue

            data = checkbox.data(
                Qt.ItemDataRole.UserRole
            )

            if data:

                selected.append(
                    data
                )

        return selected

    # =====================================================
    # GENERATE
    # =====================================================

    def generate_reports(
        self
    ):

        selected = (
            self.get_selected_panels()
        )

        if not selected:

            QMessageBox.warning(
                self,
                "No Panels Selected",
                "Select at least one panel."
            )

            return

        output_folder = (
            self.output_edit
            .text()
            .strip()
        )

        if not output_folder:

            output_folder = QFileDialog.getExistingDirectory(
                self,
                "Select Report Output Folder"
            )

            if not output_folder:
                return

            self.output_edit.setText(
                output_folder
            )

        output_folder = Path(
            output_folder
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        report_date = (
            self.date_edit
            .date()
            .toString(
                "yyyy-MM-dd"
            )
        )

        self.progress.setVisible(True)
        self.progress.setValue(0)

        self.generate_button.setEnabled(False)
        self.refresh_button.setEnabled(False)

        generated = []
        failed = []

        try:

            total = len(
                selected
            )

            for index, data in enumerate(
                selected,
                start=1
            ):

                panel = data["panel"]

                project_folder = (
                    self.project_combo.currentData()
                )

                context = (
                    self.get_project_context(
                        project_folder
                    )
                )

                if context is None:

                    failed.append(
                        (
                            getattr(
                                panel,
                                "name",
                                data["panel_id"]
                            ),
                            "Project database unavailable"
                        )
                    )

                    continue

                test_service = context[
                    "test_service"
                ]

                component_manager = context[
                    "component_manager"
                ]

                asset_manager = context[
                    "asset_manager"
                ]

                components = (
                    component_manager
                    .get_panel_components(
                        data["panel_id"]
                    )
                )

                protection_tests = (
                    self.get_protection_tests(
                        test_service,
                        data["panel_id"],
                        report_date
                    )
                )

                component_tests = (
                    self.get_component_tests(
                        test_service,
                        data["panel_id"],
                        report_date
                    )
                )

                hierarchy = (
                    self.get_hierarchy(
                        asset_manager,
                        panel
                    )
                )

                report_filename = (
                    self.build_filename(
                        hierarchy["substation"],
                        hierarchy["switchboard"],
                        getattr(
                            panel,
                            "name",
                            data["panel_id"]
                        ),
                        report_date
                    )
                )

                output_path = (
                    output_folder
                    /
                    report_filename
                )

                try:

                    service = PanelReportService(
                        project_folder
                    )

                    result = (
                        service.generate_report(
                            panel=panel,
                            components=components,
                            protection_tests=protection_tests,
                            component_tests=component_tests,
                            report_date=report_date,
                            substation_name=hierarchy[
                                "substation"
                            ],
                            switchboard_name=hierarchy[
                                "switchboard"
                            ],
                            parent=None,
                            output_path=output_path,
                        )
                    )

                    if result:

                        generated.append(
                            output_path
                        )

                    else:

                        failed.append(
                            (
                                getattr(
                                    panel,
                                    "name",
                                    data["panel_id"]
                                ),
                                "Report service returned no output"
                            )
                        )

                except Exception as error:

                    failed.append(
                        (
                            getattr(
                                panel,
                                "name",
                                data["panel_id"]
                            ),
                            str(error)
                        )
                    )

                self.progress.setValue(
                    int(
                        index
                        /
                        total
                        *
                        100
                    )
                )

                self.status_label.setText(
                    f"Generating {index} of {total}..."
                )

                self.repaint()

        finally:

            self.generate_button.setEnabled(True)
            self.refresh_button.setEnabled(True)

        self.status_label.setText(
            f"Completed: {len(generated)} generated, "
            f"{len(failed)} failed."
        )

        if failed:

            details = "\n".join(
                f"• {name}: {error}"
                for name, error in failed
            )

            QMessageBox.warning(
                self,
                "Report Generation Completed",
                (
                    f"Generated: {len(generated)}\n"
                    f"Failed: {len(failed)}\n\n"
                    f"Failures:\n{details}"
                )
            )

        else:

            QMessageBox.information(
                self,
                "Reports Generated",
                (
                    f"{len(generated)} panel report(s) "
                    "generated successfully."
                )
            )

    # =====================================================
    # TEST RETRIEVAL
    # =====================================================

    def get_protection_tests(
        self,
        test_service,
        panel_id,
        report_date
    ):

        tests = []

        for row in (
            test_service.get_all_tests()
            or []
        ):

            if (
                len(row) < 6
                or row[2] != panel_id
                or not self.date_matches(
                    row[5],
                    report_date
                )
            ):

                continue

            test = test_service.get_test(
                row[0]
            )

            if test is not None:
                tests.append(test)

        return tests

    def get_component_tests(
        self,
        test_service,
        panel_id,
        report_date
    ):

        tests = []

        for row in (
            test_service.get_all_component_tests()
            or []
        ):

            if (
                len(row) < 6
                or row[2] != panel_id
                or not self.date_matches(
                    row[5],
                    report_date
                )
            ):

                continue

            test = (
                test_service.get_component_test(
                    row[0]
                )
            )

            if test is not None:
                tests.append(test)

        return tests

    # =====================================================
    # FILE NAME
    # =====================================================

    @staticmethod
    def safe_filename_part(
        value
    ):

        text = str(
            value or ""
        ).strip()

        for character in (
            "\\",
            "/",
            ":",
            "*",
            "?",
            '"',
            "<",
            ">",
            "|",
        ):

            text = text.replace(
                character,
                "-"
            )

        return text

    @classmethod
    def build_filename(
        cls,
        substation,
        switchboard,
        panel,
        report_date
    ):

        parts = [
            cls.safe_filename_part(
                substation
            ),
            cls.safe_filename_part(
                switchboard
            ),
            cls.safe_filename_part(
                panel
            ),
            "Test Report",
            cls.safe_filename_part(
                report_date
            ),
        ]

        parts = [
            part
            for part in parts
            if part
        ]

        return (
            " - ".join(parts)
            + ".docx"
        )
