import sqlite3
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QFrame,
    QLineEdit,
    QComboBox,
    QPushButton,
    QSplitter,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFileDialog,
    QMessageBox,
)

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

from app.config.settings import PROJECTS_DIR


class AssetExplorerView(QWidget):

    """
    GLOBAL ASSET MANAGEMENT

    This replaces the old separation between:

        Asset Database
        Asset Explorer
        Asset Register

    It is completely independent of the currently opened
    project.

    Hierarchy:

        Substation
            └── Switchboard
                    └── Panel
                            └── Components

    Selecting an asset shows its configuration.

    Selecting a panel also shows:
        - components
        - test history

    Selecting a component shows:
        - component configuration
        - test history
    """

    def __init__(
        self,
        global_asset_service,
        parent=None,
    ):

        super().__init__(parent)

        self.global_asset_service = (
            global_asset_service
        )

        self._all_records = []

        self._tree_nodes = {}

        self._build_ui()

        self.refresh()

    # =========================================================
    # UI
    # =========================================================

    def _build_ui(self):

        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            16,
            16,
            16,
            16
        )

        root.setSpacing(
            10
        )

        # =====================================================
        # HEADER
        # =====================================================

        header_layout = QHBoxLayout()

        header = QLabel(
            "Asset Management"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 24px;
                font-weight: 700;
            }
            """
        )

        header_layout.addWidget(
            header
        )

        header_layout.addStretch()

        self.export_button = QPushButton(
            "Export Asset Register"
        )

        self.export_button.clicked.connect(
            self.export_asset_register
        )

        header_layout.addWidget(
            self.export_button
        )

        root.addLayout(
            header_layout
        )

        subtitle = QLabel(
            "Global asset configuration, hierarchy and test history"
        )

        subtitle.setStyleSheet(
            """
            QLabel {
                color: #999999;
                font-size: 13px;
            }
            """
        )

        root.addWidget(
            subtitle
        )

        # =====================================================
        # FILTER BAR
        # =====================================================

        filter_frame = QFrame()

        filter_layout = QHBoxLayout(
            filter_frame
        )

        filter_layout.setContentsMargins(
            8,
            6,
            8,
            6
        )

        self.search_edit = QLineEdit()

        self.search_edit.setPlaceholderText(
            "Search asset, tag, manufacturer, model, serial number..."
        )

        self.search_edit.textChanged.connect(
            self.apply_filters
        )

        filter_layout.addWidget(
            self.search_edit,
            1
        )

        self.type_filter = QComboBox()

        self.type_filter.addItems(
            [
                "All Assets",
                "Substations",
                "Switchboards",
                "Panels",
                "Components",
            ]
        )

        self.type_filter.currentIndexChanged.connect(
            self.apply_filters
        )

        filter_layout.addWidget(
            self.type_filter
        )

        expand_button = QPushButton(
            "Expand All"
        )

        expand_button.clicked.connect(
            self.expand_all
        )

        filter_layout.addWidget(
            expand_button
        )

        collapse_button = QPushButton(
            "Collapse All"
        )

        collapse_button.clicked.connect(
            self.collapse_all
        )

        filter_layout.addWidget(
            collapse_button
        )

        refresh_button = QPushButton(
            "Refresh"
        )

        refresh_button.clicked.connect(
            self.refresh
        )

        filter_layout.addWidget(
            refresh_button
        )

        root.addWidget(
            filter_frame
        )

        # =====================================================
        # SPLITTER
        # =====================================================

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        splitter.setChildrenCollapsible(
            False
        )

        # =====================================================
        # LEFT TREE
        # =====================================================

        tree_frame = QFrame()

        tree_layout = QVBoxLayout(
            tree_frame
        )

        tree_title = QLabel(
            "Asset Structure"
        )

        tree_title.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: 700;
                padding: 6px;
            }
            """
        )

        tree_layout.addWidget(
            tree_title
        )

        self.tree = QTreeWidget()

        self.tree.setHeaderLabels(
            [
                "Asset",
                "Type",
                "Asset Tag",
            ]
        )

        self.tree.setIndentation(
            22
        )

        self.tree.setAnimated(
            True
        )

        self.tree.setUniformRowHeights(
            True
        )

        self.tree.itemSelectionChanged.connect(
            self._selection_changed
        )

        tree_layout.addWidget(
            self.tree
        )

        splitter.addWidget(
            tree_frame
        )

        # =====================================================
        # RIGHT
        # =====================================================

        details_frame = QFrame()

        details_layout = QVBoxLayout(
            details_frame
        )

        self.details_title = QLabel(
            "Select an asset"
        )

        self.details_title.setStyleSheet(
            """
            QLabel {
                font-size: 21px;
                font-weight: 700;
                padding: 8px;
            }
            """
        )

        details_layout.addWidget(
            self.details_title
        )

        self.details_subtitle = QLabel(
            ""
        )

        self.details_subtitle.setStyleSheet(
            """
            QLabel {
                color: #999999;
                padding: 0 8px 8px 8px;
            }
            """
        )

        details_layout.addWidget(
            self.details_subtitle
        )

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.details_container = QWidget()

        self.details_form_layout = QVBoxLayout(
            self.details_container
        )

        self.details_form_layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        self.details_form_layout.setSpacing(
            8
        )

        scroll.setWidget(
            self.details_container
        )

        details_layout.addWidget(
            scroll
        )

        splitter.addWidget(
            details_frame
        )

        splitter.setStretchFactor(
            0,
            5
        )

        splitter.setStretchFactor(
            1,
            5
        )

        root.addWidget(
            splitter,
            1
        )

        # =====================================================
        # STYLE
        # =====================================================

        self.setStyleSheet(
            """
            QFrame {
                background: #292929;
                border-radius: 7px;
            }

            QTreeWidget {
                background: #242424;
                border: 1px solid #3d3d3d;
                border-radius: 7px;
                outline: none;
            }

            QTreeWidget::item {
                padding: 6px;
                min-height: 28px;
            }

            QTreeWidget::item:hover {
                background: #333333;
            }

            QTreeWidget::item:selected {
                background: #3b3b3b;
                border-left: 3px solid #f39c12;
            }

            QLineEdit,
            QComboBox {
                min-height: 32px;
                padding: 4px 8px;
                border: 1px solid #444444;
                border-radius: 6px;
                background: #303030;
            }

            QPushButton {
                min-height: 32px;
                padding: 5px 12px;
                border: 1px solid #444444;
                border-radius: 6px;
                background: #303030;
            }

            QPushButton:hover {
                background: #3a3a3a;
            }

            QLabel#Section {
                font-size: 15px;
                font-weight: 700;
                padding: 7px 4px;
            }

            QLabel#Value {
                padding: 7px;
                background: #303030;
                border-radius: 5px;
            }

            QTableWidget {
                background: #242424;
                border: 1px solid #444444;
            }
            """
        )

    # =========================================================
    # REFRESH
    # =========================================================

    def refresh(self):

        try:

            self.global_asset_service.refresh()

            self._load_records()

            self.apply_filters()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Asset Management",
                f"Unable to refresh assets:\n\n{error}"
            )

    # =========================================================
    # LOAD GLOBAL RECORDS
    # =========================================================

    def _load_records(self):

        self._all_records = []

        # -----------------------------------------------------
        # PHYSICAL ASSETS
        # -----------------------------------------------------

        for entry in (
            self.global_asset_service
            .get_all_nodes()
        ):

            node = entry.get(
                "node"
            )

            if node is None:
                continue

            node_type = self._normalise_type(
                getattr(
                    node,
                    "node_type",
                    ""
                )
            )

            if node_type not in (
                "SUBSTATION",
                "SWITCHBOARD",
                "PANEL",
            ):
                continue

            record = {

                "record_type":
                    "NODE",

                "project":
                    entry.get(
                        "project",
                        ""
                    ),

                "folder":
                    entry.get(
                        "folder"
                    ),

                "asset_manager":
                    entry.get(
                        "asset_manager"
                    ),

                "component_manager":
                    entry.get(
                        "component_manager"
                    ),

                "node":
                    node,

                "component":
                    None,

                "type":
                    node_type,

                "asset_id":
                    getattr(
                        node,
                        "asset_id",
                        ""
                    ),

                "name":
                    getattr(
                        node,
                        "name",
                        ""
                    ),
            }

            self._all_records.append(
                record
            )

        # -----------------------------------------------------
        # COMPONENTS
        # -----------------------------------------------------

        for entry in (
            self.global_asset_service
            .get_all_components()
        ):

            component = entry.get(
                "component"
            )

            panel = entry.get(
                "panel"
            )

            if component is None:
                continue

            component_type = (
                self._normalise_component_type(
                    getattr(
                        component,
                        "component_type",
                        ""
                    )
                )
            )

            record = {

                "record_type":
                    "COMPONENT",

                "project":
                    entry.get(
                        "project",
                        ""
                    ),

                "folder":
                    entry.get(
                        "folder"
                    ),

                "asset_manager":
                    entry.get(
                        "asset_manager"
                    ),

                "component_manager":
                    entry.get(
                        "component_manager"
                    ),

                "node":
                    panel,

                "component":
                    component,

                "type":
                    component_type,

                "asset_id":
                    getattr(
                        panel,
                        "asset_id",
                        ""
                    ),

                "component_id":
                    getattr(
                        component,
                        "component_id",
                        ""
                    ),

                "name":
                    getattr(
                        component,
                        "name",
                        ""
                    ),
            }

            self._all_records.append(
                record
            )

    # =========================================================
    # FILTER
    # =========================================================

    def apply_filters(self):

        self.tree.clear()

        search = (
            self.search_edit.text()
            .strip()
            .lower()
        )

        selected_type = (
            self.type_filter.currentText()
        )

        # -----------------------------------------------------
        # Group records by project.
        # -----------------------------------------------------

        projects = {}

        for record in self._all_records:

            if not self._record_matches(
                record,
                search,
                selected_type
            ):
                continue

            project = str(
                record.get(
                    "project",
                    ""
                )
            )

            projects.setdefault(
                project,
                []
            ).append(
                record
            )

        # -----------------------------------------------------
        # Build hierarchy from actual nodes.
        # -----------------------------------------------------

        node_records = [
            record
            for record in self._all_records
            if record["record_type"] == "NODE"
        ]

        component_records = [
            record
            for record in self._all_records
            if record["record_type"] == "COMPONENT"
        ]

        for project_name in sorted(
            projects.keys(),
            key=str.lower
        ):

            # Project is deliberately NOT shown as part of
            # the physical asset hierarchy.
            #
            # We use it only to prevent mixing identical
            # assets belonging to different projects.

            project_node_records = [
                record
                for record in node_records
                if record["project"] == project_name
            ]

            project_component_records = [
                record
                for record in component_records
                if record["project"] == project_name
            ]

            # -------------------------------------------------
            # ROOTS
            # -------------------------------------------------

            roots = []

            for record in project_node_records:

                node = record["node"]

                parent_id = getattr(
                    node,
                    "parent_id",
                    None
                )

                if parent_id is None:

                    roots.append(
                        record
                    )

            for record in sorted(
                roots,
                key=lambda r:
                    str(
                        r["name"]
                    ).lower()
            ):

                self._add_node(
                    None,
                    record,
                    project_node_records,
                    project_component_records,
                    search,
                    selected_type
                )

        # -----------------------------------------------------
        # Start collapsed.
        # -----------------------------------------------------

        self.collapse_all()

    # =========================================================
    # ADD NODE
    # =========================================================

    def _add_node(
        self,
        parent_item,
        record,
        node_records,
        component_records,
        search,
        selected_type
    ):

        node = record["node"]

        node_type = record["type"]

        item = QTreeWidgetItem()

        item.setText(
            0,
            str(
                record["name"]
            )
        )

        item.setText(
            1,
            node_type
        )

        item.setText(
            2,
            self._get_asset_tag(
                record
            )
        )

        item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            record
        )

        if parent_item is None:

            self.tree.addTopLevelItem(
                item
            )

        else:

            parent_item.addChild(
                item
            )

        # -----------------------------------------------------
        # CHILD NODES
        # -----------------------------------------------------

        children = []

        for child_record in node_records:

            child_node = (
                child_record["node"]
            )

            if getattr(
                child_node,
                "parent_id",
                None
            ) == getattr(
                node,
                "node_id",
                None
            ):

                if self._record_matches(
                    child_record,
                    search,
                    selected_type
                ):

                    children.append(
                        child_record
                    )

        for child in sorted(
            children,
            key=lambda r:
                str(
                    r["name"]
                ).lower()
        ):

            self._add_node(
                item,
                child,
                node_records,
                component_records,
                search,
                selected_type
            )

        # -----------------------------------------------------
        # COMPONENTS
        # -----------------------------------------------------

        if node_type == "PANEL":

            panel_id = getattr(
                node,
                "node_id",
                None
            )

            panel_components = []

            for component_record in (
                component_records
            ):

                component_panel = (
                    component_record["node"]
                )

                if getattr(
                    component_panel,
                    "node_id",
                    None
                ) != panel_id:
                    continue

                if self._record_matches(
                    component_record,
                    search,
                    selected_type
                ):

                    panel_components.append(
                        component_record
                    )

            for component_record in sorted(
                panel_components,
                key=lambda r:
                    str(
                        r["name"]
                    ).lower()
            ):

                self._add_component(
                    item,
                    component_record
                )

    # =========================================================
    # ADD COMPONENT
    # =========================================================

    def _add_component(
        self,
        parent_item,
        record
    ):

        component = (
            record["component"]
        )

        item = QTreeWidgetItem()

        item.setText(
            0,
            str(
                getattr(
                    component,
                    "name",
                    ""
                )
            )
        )

        item.setText(
            1,
            str(
                record["type"]
            )
        )

        item.setText(
            2,
            ""
        )

        item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            record
        )

        parent_item.addChild(
            item
        )

    # =========================================================
    # RECORD MATCHING
    # =========================================================

    def _record_matches(
        self,
        record,
        search,
        selected_type
    ):

        record_type = record.get(
            "record_type"
        )

        # -----------------------------------------------------
        # Type filter
        # -----------------------------------------------------

        if selected_type == "Substations":

            if record.get(
                "type"
            ) != "SUBSTATION":

                return False

        elif selected_type == "Switchboards":

            if record.get(
                "type"
            ) != "SWITCHBOARD":

                return False

        elif selected_type == "Panels":

            if record.get(
                "type"
            ) != "PANEL":

                return False

        elif selected_type == "Components":

            if record_type != "COMPONENT":

                return False

        # -----------------------------------------------------
        # Search
        # -----------------------------------------------------

        if not search:

            return True

        values = []

        node = record.get(
            "node"
        )

        component = record.get(
            "component"
        )

        if node is not None:

            for field in (
                "name",
                "asset_id",
                "asset_tag",
                "manufacturer",
                "model",
                "serial_number",
                "equipment_name",
                "equipment_type",
            ):

                values.append(
                    str(
                        getattr(
                            node,
                            field,
                            ""
                        )
                        or ""
                    )
                )

        if component is not None:

            for field in (
                "name",
                "component_id",
                "component_type",
                "manufacturer",
                "model",
                "serial_number",
                "description",
                "ct_ratio",
                "ct_class",
                "burden",
                "core",
                "vt_ratio",
                "firmware",
                "coil_voltage",
                "contact_configuration",
                "meter_type",
                "accuracy_class",
            ):

                values.append(
                    str(
                        getattr(
                            component,
                            field,
                            ""
                        )
                        or ""
                    )
                )

        values.append(
            str(
                record.get(
                    "project",
                    ""
                )
            )
        )

        return search in (
            " ".join(values)
            .lower()
        )

    # =========================================================
    # SELECTION
    # =========================================================

    def _selection_changed(self):

        item = self.tree.currentItem()

        if item is None:

            self._clear_details()

            return

        record = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            record,
            dict
        ):

            self._clear_details()

            return

        self._show_record(
            record
        )

    # =========================================================
    # SHOW RECORD
    # =========================================================

    def _show_record(
        self,
        record
    ):

        self._clear_detail_widgets()

        if record["record_type"] == "COMPONENT":

            component = (
                record["component"]
            )

            self.details_title.setText(
                str(
                    getattr(
                        component,
                        "name",
                        "Component"
                    )
                )
            )

            self.details_subtitle.setText(
                (
                    f"{record['type']}  |  "
                    f"{record['project']}"
                )
            )

            self._show_component_details(
                record
            )

            self._show_test_history(
                record
            )

            return

        node = record["node"]

        self.details_title.setText(
            str(
                getattr(
                    node,
                    "name",
                    "Asset"
                )
            )
        )

        self.details_subtitle.setText(
            (
                f"{record['type']}  |  "
                f"{record['project']}"
            )
        )

        self._show_node_details(
            record
        )

        if (
            str(
                getattr(
                    node,
                    "node_type",
                    ""
                )
            ).upper()
            == "PANEL"
        ):

            self._show_panel_components(
                record
            )

            self._show_test_history(
                record
            )

    # =========================================================
    # NODE DETAILS
    # =========================================================

    def _show_node_details(
        self,
        record
    ):

        node = record["node"]

        fields = [

            (
                "Project",
                record.get(
                    "project",
                    ""
                )
            ),

            (
                "Asset ID",
                getattr(
                    node,
                    "asset_id",
                    ""
                )
            ),

            (
                "Asset Tag",
                self._get_asset_tag(
                    record
                )
            ),

            (
                "Manufacturer",
                getattr(
                    node,
                    "manufacturer",
                    ""
                )
            ),

            (
                "Model",
                getattr(
                    node,
                    "model",
                    ""
                )
            ),

            (
                "Serial Number",
                getattr(
                    node,
                    "serial_number",
                    ""
                )
            ),

            (
                "Feed Equipment",
                getattr(
                    node,
                    "equipment_name",
                    ""
                )
            ),

            (
                "Equipment Type",
                getattr(
                    node,
                    "equipment_type",
                    ""
                )
            ),

        ]

        if str(
            getattr(
                node,
                "node_type",
                ""
            )
        ).upper() == "PANEL":

            fields.extend(

                [

                    (
                        "Number of CTs",
                        getattr(
                            node,
                            "ct_count",
                            0
                        )
                    ),

                    (
                        "Numerical Relays",
                        getattr(
                            node,
                            "relay_count",
                            0
                        )
                    ),

                    (
                        "Auxiliary Relays",
                        getattr(
                            node,
                            "aux_count",
                            0
                        )
                    ),

                    (
                        "Meters",
                        getattr(
                            node,
                            "meter_count",
                            0
                        )
                    ),

                ]
            )

        self._add_section(
            "Asset Configuration"
        )

        for label, value in fields:

            self._add_field(
                label,
                value
            )

    # =========================================================
    # COMPONENT DETAILS
    # =========================================================

    def _show_component_details(
        self,
        record
    ):

        component = (
            record["component"]
        )

        fields = [

            (
                "Project",
                record.get(
                    "project",
                    ""
                )
            ),

            (
                "Component ID",
                getattr(
                    component,
                    "component_id",
                    ""
                )
            ),

            (
                "Component Type",
                getattr(
                    component,
                    "component_type",
                    ""
                )
            ),

            (
                "Manufacturer",
                getattr(
                    component,
                    "manufacturer",
                    ""
                )
            ),

            (
                "Model",
                getattr(
                    component,
                    "model",
                    ""
                )
            ),

            (
                "Serial Number",
                getattr(
                    component,
                    "serial_number",
                    ""
                )
            ),

            (
                "Description",
                getattr(
                    component,
                    "description",
                    ""
                )
            ),

            (
                "CT Primary",
                getattr(
                    component,
                    "ct_primary",
                    ""
                )
            ),

            (
                "CT Secondary",
                getattr(
                    component,
                    "ct_secondary",
                    ""
                )
            ),

            (
                "CT Ratio",
                getattr(
                    component,
                    "ct_ratio",
                    ""
                )
            ),

            (
                "CT Class",
                getattr(
                    component,
                    "ct_class",
                    ""
                )
            ),

            (
                "Burden",
                getattr(
                    component,
                    "burden",
                    ""
                )
            ),

            (
                "Core",
                getattr(
                    component,
                    "core",
                    ""
                )
            ),

            (
                "VT Ratio",
                getattr(
                    component,
                    "vt_ratio",
                    ""
                )
            ),

            (
                "Firmware",
                getattr(
                    component,
                    "firmware",
                    ""
                )
            ),

            (
                "Coil Voltage",
                getattr(
                    component,
                    "coil_voltage",
                    ""
                )
            ),

            (
                "Contact Configuration",
                getattr(
                    component,
                    "contact_configuration",
                    ""
                )
            ),

            (
                "Meter Type",
                getattr(
                    component,
                    "meter_type",
                    ""
                )
            ),

            (
                "Meter Functions",
                self._format_value(
                    getattr(
                        component,
                        "meter_functions",
                        ""
                    )
                )
            ),

            (
                "Accuracy Class",
                getattr(
                    component,
                    "accuracy_class",
                    ""
                )
            ),

            (
                "Protection Functions",
                self._format_value(
                    getattr(
                        component,
                        "protection_functions",
                        ""
                    )
                )
            ),

        ]

        self._add_section(
            "Component Configuration"
        )

        for label, value in fields:

            self._add_field(
                label,
                value
            )

    # =========================================================
    # PANEL COMPONENTS
    # =========================================================

    def _show_panel_components(
        self,
        panel_record
    ):

        panel = panel_record["node"]

        panel_id = getattr(
            panel,
            "node_id",
            None
        )

        components = []

        for record in self._all_records:

            if record["record_type"] != "COMPONENT":
                continue

            component_panel = (
                record["node"]
            )

            if getattr(
                component_panel,
                "node_id",
                None
            ) == panel_id:

                components.append(
                    record
                )

        self._add_section(
            "Components"
        )

        if not components:

            self._add_field(
                "Components",
                "No components configured"
            )

            return

        table = QTableWidget()

        table.setColumnCount(
            5
        )

        table.setHorizontalHeaderLabels(
            [
                "Component",
                "Type",
                "Manufacturer",
                "Model",
                "Serial Number",
            ]
        )

        table.setRowCount(
            len(components)
        )

        for row, record in enumerate(
            components
        ):

            component = (
                record["component"]
            )

            values = [

                getattr(
                    component,
                    "name",
                    ""
                ),

                getattr(
                    component,
                    "component_type",
                    ""
                ),

                getattr(
                    component,
                    "manufacturer",
                    ""
                ),

                getattr(
                    component,
                    "model",
                    ""
                ),

                getattr(
                    component,
                    "serial_number",
                    ""
                ),

            ]

            for column, value in enumerate(
                values
            ):

                table.setItem(
                    row,
                    column,
                    QTableWidgetItem(
                        str(
                            value or ""
                        )
                    )
                )

        table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        table.setMaximumHeight(
            250
        )

        self.details_form_layout.addWidget(
            table
        )

    # =========================================================
    # TEST HISTORY
    # =========================================================

    def _show_test_history(
        self,
        record
    ):

        self._add_section(
            "Test History"
        )

        table = QTableWidget()

        table.setColumnCount(
            8
        )

        table.setHorizontalHeaderLabels(
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

        rows = (
            self._get_test_history(
                record
            )
        )

        table.setRowCount(
            len(rows)
        )

        for row_index, row_data in enumerate(
            rows
        ):

            for column_index, value in enumerate(
                row_data
            ):

                table.setItem(
                    row_index,
                    column_index,
                    QTableWidgetItem(
                        str(
                            value or ""
                        )
                    )
                )

        table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

        table.setMinimumHeight(
            180
        )

        self.details_form_layout.addWidget(
            table
        )

        if not rows:

            self._add_field(
                "Tests",
                "No test history found"
            )

    # =========================================================
    # TEST HISTORY DATA
    # =========================================================

    def _get_test_history(
        self,
        record
    ):

        node = record.get(
            "node"
        )

        component = record.get(
            "component"
        )

        if node is None:
            return []

        panel_id = getattr(
            node,
            "node_id",
            None
        )

        component_id = None

        if component is not None:

            component_id = getattr(
                component,
                "component_id",
                None
            )

        results = []

        project_folder = Path(
            record["folder"]
        )

        database_file = (
            project_folder /
            "testing.db"
        )

        if not database_file.exists():

            return []

        component_names = (
            self._load_component_names(
                project_folder
            )
        )

        try:

            connection = sqlite3.connect(
                database_file
            )

            cursor = connection.cursor()

            # -------------------------------------------------
            # Protection tests
            # -------------------------------------------------

            if component_id is None:

                try:

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
                        (
                            panel_id,
                        )
                    )

                    for row in cursor.fetchall():

                        results.append(
                            [
                                row[1],
                                record["project"],
                                getattr(
                                    node,
                                    "name",
                                    ""
                                ),
                                "PROTECTION TEST",
                                (
                                    f"{row[2] or ''} | "
                                    f"{component_names.get(row[3], row[3] or '')}"
                                ),
                                row[4],
                                row[5],
                                row[0],
                            ]
                        )

                except sqlite3.Error:
                    pass

            # -------------------------------------------------
            # Component tests
            # -------------------------------------------------

            try:

                if component_id is not None:

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
                        WHERE component_id = ?
                        ORDER BY test_date DESC
                        """,
                        (
                            component_id,
                        )
                    )

                else:

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
                        (
                            panel_id,
                        )
                    )

                for row in cursor.fetchall():

                    results.append(
                        [
                            row[1],
                            record["project"],
                            getattr(
                                node,
                                "name",
                                ""
                            ),
                            "COMPONENT TEST",
                            component_names.get(
                                row[2],
                                row[2] or ""
                            ),
                            row[4],
                            row[5],
                            row[0],
                        ]
                    )

            except sqlite3.Error:
                pass

            connection.close()

        except sqlite3.Error:

            return []

        return results

    # =========================================================
    # COMPONENT NAMES
    # =========================================================

    @staticmethod
    def _load_component_names(
        project_folder
    ):

        names = {}

        components_file = (
            Path(project_folder) /
            "components.json"
        )

        if not components_file.exists():

            return names

        try:

            import json

            with open(
                components_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            if isinstance(
                data,
                list
            ):

                for item in data:

                    component_id = (
                        item.get(
                            "component_id"
                        )
                    )

                    if component_id:

                        names[
                            component_id
                        ] = item.get(
                            "name",
                            ""
                        )

        except Exception:
            pass

        return names

    # =========================================================
    # DETAILS HELPERS
    # =========================================================

    def _clear_details(self):

        self.details_title.setText(
            "Select an asset"
        )

        self.details_subtitle.setText(
            ""
        )

        self._clear_detail_widgets()

    def _clear_detail_widgets(self):

        while (
            self.details_form_layout.count()
        ):

            item = (
                self.details_form_layout
                .takeAt(0)
            )

            widget = item.widget()

            if widget is not None:

                widget.deleteLater()

    def _add_section(
        self,
        title
    ):

        label = QLabel(
            title
        )

        label.setObjectName(
            "Section"
        )

        self.details_form_layout.addWidget(
            label
        )

    def _add_field(
        self,
        label,
        value
    ):

        row = QHBoxLayout()

        name = QLabel(
            str(label)
        )

        name.setMinimumWidth(
            170
        )

        name.setStyleSheet(
            "font-weight: 600;"
        )

        value_label = QLabel(
            self._format_value(
                value
            )
        )

        value_label.setObjectName(
            "Value"
        )

        value_label.setWordWrap(
            True
        )

        row.addWidget(
            name
        )

        row.addWidget(
            value_label,
            1
        )

        self.details_form_layout.addLayout(
            row
        )

    # =========================================================
    # EXPANSION
    # =========================================================

    def expand_all(self):

        self.tree.expandAll()

    def collapse_all(self):

        self.tree.collapseAll()

    # =========================================================
    # ASSET TAG
    # =========================================================

    @staticmethod
    def _get_asset_tag(
        record
    ):

        node = record.get(
            "node"
        )

        if node is None:

            return ""

        # Direct node field first.

        value = getattr(
            node,
            "asset_tag",
            ""
        )

        if value:

            return str(
                value
            )

        # Asset library.

        manager = record.get(
            "asset_manager"
        )

        asset_id = getattr(
            node,
            "asset_id",
            None
        )

        if (
            manager is not None
            and asset_id
        ):

            try:

                library = getattr(
                    manager,
                    "asset_library",
                    None
                )

                if library is not None:

                    try:
                        library.load()
                    except Exception:
                        pass

                    asset = (
                        library.get_asset(
                            asset_id
                        )
                    )

                    if asset:

                        return str(
                            asset.get(
                                "asset_tag",
                                ""
                            )
                        )

            except Exception:

                pass

        return ""

    # =========================================================
    # FORMAT
    # =========================================================

    @staticmethod
    def _format_value(
        value
    ):

        if value is None:

            return ""

        if isinstance(
            value,
            (list, tuple)
        ):

            return ", ".join(
                str(item)
                for item in value
            )

        if isinstance(
            value,
            dict
        ):

            return ", ".join(
                f"{key}: {value}"
                for key, value in value.items()
            )

        return str(
            value
        )

    # =========================================================
    # NORMALISE TYPE
    # =========================================================

    @staticmethod
    def _normalise_type(
        value
    ):

        value = str(
            value or ""
        ).strip().upper()

        return value.replace(
            " ",
            "_"
        )

    @staticmethod
    def _normalise_component_type(
        value
    ):

        value = str(
            value or ""
        ).strip().upper()

        if value in (
            "CURRENT TRANSFORMER",
            "CURRENT_TRANSFORMER",
        ):

            return "CT"

        if value in (
            "NUMERICAL RELAY",
            "NUMERICAL_RELAY",
            "RELAY",
        ):

            return "NUMERICAL RELAY"

        if value in (
            "AUXILIARY RELAY",
            "AUXILIARY_RELAY",
            "AUX RELAY",
        ):

            return "AUXILIARY RELAY"

        if value in (
            "MULTIFUNCTION METER",
            "MULTIFUNCTION_METER",
            "AMMETER",
            "VOLTMETER",
        ):

            return "METER"

        return value

    # =========================================================
    # EXPORT ASSET REGISTER
    # =========================================================

    def export_asset_register(self):

        default_path = (
            PROJECTS_DIR /
            "Asset_Register.xlsx"
        )

        output_path, _ = (
            QFileDialog.getSaveFileName(
                self,
                "Export Asset Register",
                str(
                    default_path
                ),
                "Excel Workbook (*.xlsx)"
            )
        )

        if not output_path:

            return

        try:

            self._export_excel(
                output_path
            )

            QMessageBox.information(
                self,
                "Asset Register",
                (
                    "Asset Register exported successfully.\n\n"
                    f"{output_path}"
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Asset Register Export Failed",
                (
                    "Unable to export the Asset Register.\n\n"
                    f"{error}"
                )
            )

            raise

    # =========================================================
    # EXCEL EXPORT
    # =========================================================

    def _export_excel(
        self,
        output_path
    ):

        self.global_asset_service.refresh()

        self._load_records()

        workbook = Workbook()

        default_sheet = (
            workbook.active
        )

        workbook.remove(
            default_sheet
        )

        # =====================================================
        # MASTER REGISTER
        # =====================================================

        master_columns = [

            "Project",
            "Substation",
            "Switchboard",
            "Panel",
            "Panel Asset Tag",
            "Feed Equipment",
            "Equipment Type",
            "Component",
            "Component Type",
            "Component ID",

            "Manufacturer",
            "Model",
            "Serial Number",
            "Description",

            "CT Primary",
            "CT Secondary",
            "CT Ratio",
            "CT Class",
            "Burden",
            "Core",

            "VT Ratio",
            "Firmware",

            "Coil Voltage",
            "Contact Configuration",

            "Meter Type",
            "Meter Functions",
            "Accuracy Class",

            "Protection Functions",
        ]

        rows = []

        for record in self._all_records:

            if record["record_type"] != "COMPONENT":
                continue

            component = (
                record["component"]
            )

            panel = (
                record["node"]
            )

            hierarchy = (
                self._get_hierarchy(
                    record
                )
            )

            rows.append(
                {

                    "Project":
                        record["project"],

                    "Substation":
                        hierarchy.get(
                            "SUBSTATION",
                            ""
                        ),

                    "Switchboard":
                        hierarchy.get(
                            "SWITCHBOARD",
                            ""
                        ),

                    "Panel":
                        getattr(
                            panel,
                            "name",
                            ""
                        ),

                    "Panel Asset Tag":
                        self._get_asset_tag(
                            record
                        ),

                    "Feed Equipment":
                        getattr(
                            panel,
                            "equipment_name",
                            ""
                        ),

                    "Equipment Type":
                        getattr(
                            panel,
                            "equipment_type",
                            ""
                        ),

                    "Component":
                        getattr(
                            component,
                            "name",
                            ""
                        ),

                    "Component Type":
                        getattr(
                            component,
                            "component_type",
                            ""
                        ),

                    "Component ID":
                        getattr(
                            component,
                            "component_id",
                            ""
                        ),

                    "Manufacturer":
                        getattr(
                            component,
                            "manufacturer",
                            ""
                        ),

                    "Model":
                        getattr(
                            component,
                            "model",
                            ""
                        ),

                    "Serial Number":
                        getattr(
                            component,
                            "serial_number",
                            ""
                        ),

                    "Description":
                        getattr(
                            component,
                            "description",
                            ""
                        ),

                    "CT Primary":
                        getattr(
                            component,
                            "ct_primary",
                            ""
                        ),

                    "CT Secondary":
                        getattr(
                            component,
                            "ct_secondary",
                            ""
                        ),

                    "CT Ratio":
                        getattr(
                            component,
                            "ct_ratio",
                            ""
                        ),

                    "CT Class":
                        getattr(
                            component,
                            "ct_class",
                            ""
                        ),

                    "Burden":
                        getattr(
                            component,
                            "burden",
                            ""
                        ),

                    "Core":
                        getattr(
                            component,
                            "core",
                            ""
                        ),

                    "VT Ratio":
                        getattr(
                            component,
                            "vt_ratio",
                            ""
                        ),

                    "Firmware":
                        getattr(
                            component,
                            "firmware",
                            ""
                        ),

                    "Coil Voltage":
                        getattr(
                            component,
                            "coil_voltage",
                            ""
                        ),

                    "Contact Configuration":
                        getattr(
                            component,
                            "contact_configuration",
                            ""
                        ),

                    "Meter Type":
                        getattr(
                            component,
                            "meter_type",
                            ""
                        ),

                    "Meter Functions":
                        self._format_value(
                            getattr(
                                component,
                                "meter_functions",
                                ""
                            )
                        ),

                    "Accuracy Class":
                        getattr(
                            component,
                            "accuracy_class",
                            ""
                        ),

                    "Protection Functions":
                        self._format_value(
                            getattr(
                                component,
                                "protection_functions",
                                ""
                            )
                        ),
                }
            )

        self._write_sheet(
            workbook.create_sheet(
                "Asset Register"
            ),
            master_columns,
            rows,
            "AssetRegisterTable"
        )

        # =====================================================
        # PANELS
        # =====================================================

        panel_columns = [

            "Project",
            "Substation",
            "Switchboard",
            "Panel",
            "Panel Asset Tag",
            "Panel ID",
            "Feed Equipment",
            "Equipment Type",
            "CT Count",
            "Numerical Relay Count",
            "Auxiliary Relay Count",
            "Meter Count",
        ]

        panel_rows = []

        for record in self._all_records:

            if record["record_type"] != "NODE":
                continue

            node = record["node"]

            if (
                self._normalise_type(
                    getattr(
                        node,
                        "node_type",
                        ""
                    )
                )
                != "PANEL"
            ):

                continue

            hierarchy = (
                self._get_hierarchy(
                    record
                )
            )

            panel_rows.append(
                {

                    "Project":
                        record["project"],

                    "Substation":
                        hierarchy.get(
                            "SUBSTATION",
                            ""
                        ),

                    "Switchboard":
                        hierarchy.get(
                            "SWITCHBOARD",
                            ""
                        ),

                    "Panel":
                        getattr(
                            node,
                            "name",
                            ""
                        ),

                    "Panel Asset Tag":
                        self._get_asset_tag(
                            record
                        ),

                    "Panel ID":
                        getattr(
                            node,
                            "node_id",
                            ""
                        ),

                    "Feed Equipment":
                        getattr(
                            node,
                            "equipment_name",
                            ""
                        ),

                    "Equipment Type":
                        getattr(
                            node,
                            "equipment_type",
                            ""
                        ),

                    "CT Count":
                        getattr(
                            node,
                            "ct_count",
                            0
                        ),

                    "Numerical Relay Count":
                        getattr(
                            node,
                            "relay_count",
                            0
                        ),

                    "Auxiliary Relay Count":
                        getattr(
                            node,
                            "aux_count",
                            0
                        ),

                    "Meter Count":
                        getattr(
                            node,
                            "meter_count",
                            0
                        ),
                }
            )

        self._write_sheet(
            workbook.create_sheet(
                "Panels"
            ),
            panel_columns,
            panel_rows,
            "PanelsTable"
        )

        # =====================================================
        # COMPONENT SHEETS
        # =====================================================

        component_columns = master_columns

        component_sheet_map = {

            "CT":
                (
                    "CTs",
                    "CTTable"
                ),

            "NUMERICAL RELAY":
                (
                    "Numerical Relays",
                    "NumericalRelayTable"
                ),

            "AUXILIARY RELAY":
                (
                    "Aux Relays",
                    "AuxRelayTable"
                ),

            "METER":
                (
                    "Meters",
                    "MeterTable"
                ),
        }

        for component_type, (
            sheet_name,
            table_name
        ) in component_sheet_map.items():

            component_rows = [

                row

                for row in rows

                if self._normalise_component_type(
                    row.get(
                        "Component Type",
                        ""
                    )
                )
                == component_type
            ]

            self._write_sheet(
                workbook.create_sheet(
                    sheet_name
                ),
                component_columns,
                component_rows,
                table_name
            )

        # =====================================================
        # INFO
        # =====================================================

        info = workbook.create_sheet(
            "Register Info"
        )

        info["A1"] = (
            "Protection Testing Suite"
        )

        info["A1"].font = Font(
            bold=True,
            size=16
        )

        info["A3"] = (
            "Generated"
        )

        from datetime import datetime

        info["B3"] = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        info["A4"] = (
            "Projects"
        )

        info["B4"] = len(
            self.global_asset_service
            .get_projects()
        )

        info["A5"] = (
            "Components"
        )

        info["B5"] = len(
            self.global_asset_service
            .get_all_components()
        )

        info.column_dimensions[
            "A"
        ].width = 25

        info.column_dimensions[
            "B"
        ].width = 30

        workbook.save(
            output_path
        )

    # =========================================================
    # EXCEL SHEET WRITER
    # =========================================================

    @staticmethod
    def _write_sheet(
        worksheet,
        columns,
        rows,
        table_name
    ):

        for column_index, column in enumerate(
            columns,
            start=1
        ):

            cell = worksheet.cell(
                1,
                column_index
            )

            cell.value = column

            cell.font = Font(
                bold=True
            )

            cell.alignment = Alignment(
                horizontal="center",
                vertical="center"
            )

        for row_index, row_data in enumerate(
            rows,
            start=2
        ):

            for column_index, column in enumerate(
                columns,
                start=1
            ):

                value = row_data.get(
                    column,
                    ""
                )

                if value is None:

                    value = ""

                worksheet.cell(
                    row_index,
                    column_index
                ).value = value

        worksheet.freeze_panes = "A2"

        if rows:

            last_column = (
                get_column_letter(
                    len(columns)
                )
            )

            reference = (
                f"A1:"
                f"{last_column}"
                f"{len(rows) + 1}"
            )

            table = Table(
                displayName=table_name,
                ref=reference
            )

            table.tableStyleInfo = (
                TableStyleInfo(
                    name="TableStyleMedium2",
                    showFirstColumn=False,
                    showLastColumn=False,
                    showRowStripes=True,
                    showColumnStripes=False,
                )
            )

            worksheet.add_table(
                table
            )

        for column_index in range(
            1,
            len(columns) + 1
        ):

            letter = get_column_letter(
                column_index
            )

            maximum = len(
                str(
                    worksheet.cell(
                        1,
                        column_index
                    ).value
                    or ""
                )
            )

            for row_index in range(
                2,
                min(
                    worksheet.max_row,
                    1000
                ) + 1
            ):

                value = worksheet.cell(
                    row_index,
                    column_index
                ).value

                if value is not None:

                    maximum = max(
                        maximum,
                        len(
                            str(value)
                        )
                    )

            worksheet.column_dimensions[
                letter
            ].width = min(
                max(
                    maximum + 2,
                    12
                ),
                45
            )

    # =========================================================
    # HIERARCHY
    # =========================================================

    @staticmethod
    def _get_hierarchy(
        record
    ):

        manager = record.get(
            "asset_manager"
        )

        node = record.get(
            "node"
        )

        result = {}

        if (
            manager is None
            or node is None
        ):

            return result

        current = node

        visited = set()

        while current is not None:

            node_id = getattr(
                current,
                "node_id",
                None
            )

            if node_id in visited:

                break

            visited.add(
                node_id
            )

            node_type = (
                AssetExplorerView
                ._normalise_type(
                    getattr(
                        current,
                        "node_type",
                        ""
                    )
                )
            )

            result[
                node_type
            ] = getattr(
                current,
                "name",
                ""
            )

            parent_id = getattr(
                current,
                "parent_id",
                None
            )

            if parent_id is None:

                break

            try:

                current = (
                    manager.get_node(
                        parent_id
                    )
                )

            except Exception:

                break

        return result