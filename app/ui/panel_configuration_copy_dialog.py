from pathlib import Path
import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QCheckBox,
    QGroupBox,
    QScrollArea,
    QWidget,
    QMessageBox,
)

from app.services.asset_manager import AssetManager
from app.services.component_manager import ComponentManager


class PanelConfigurationCopyDialog(QDialog):

    # =========================================================
    # PANEL PARAMETERS
    # =========================================================

    PANEL_PARAMETERS = {

        "equipment_name":
            "Feed Equipment",

        "equipment_type":
            "Equipment Type",

        "ct_count":
            "Number of CTs",

        "relay_count":
            "Numerical Relays",

        "aux_count":
            "Auxiliary Relays",

        "meter_count":
            "Meters",
    }

    # =========================================================
    # COMPONENT PARAMETERS
    # =========================================================

    COMPONENT_PARAMETERS = {

        "manufacturer":
            "Manufacturer",

        "model":
            "Model",

        "description":
            "Description",

        # -------------------------
        # CT
        # -------------------------

        "ct_primary":
            "CT Primary",

        "ct_secondary":
            "CT Secondary",

        "ct_ratio":
            "CT Ratio",

        "ct_class":
            "CT Class",

        "burden":
            "Burden",

        "core":
            "Core",

        # -------------------------
        # RELAY
        # -------------------------

        "vt_ratio":
            "VT Ratio",

        "firmware":
            "Firmware",

        # -------------------------
        # AUX RELAY
        # -------------------------

        "coil_voltage":
            "Coil Voltage",

        "contact_configuration":
            "Contact Configuration",

        # -------------------------
        # METER
        # -------------------------

        "meter_type":
            "Meter Type",

        "meter_functions":
            "Meter Functions",

        "accuracy_class":
            "Accuracy Class",

        # -------------------------
        # PROTECTION
        # -------------------------

        "protection_functions":
            "Protection Functions",
    }

    # =========================================================
    # UNIQUE PARAMETERS
    #
    # These are intentionally NOT offered for import.
    # =========================================================

    UNIQUE_PARAMETERS = {

        "panel_name",
        "asset_tag",

        "component_id",
        "panel_id",
        "component_name",

        "serial_number",
    }

    # =========================================================
    # INIT
    # =========================================================

    def __init__(
        self,
        projects_dir,
        target_project_folder=None,
        target_panel_id=None,
        parent=None,
    ):

        super().__init__(parent)

        self.projects_dir = Path(
            projects_dir
        )

        self.target_project_folder = (
            Path(target_project_folder)
            if target_project_folder
            else None
        )

        self.target_panel_id = (
            target_panel_id
        )

        self.selected_panel = None

        self.selected_panel_configuration = {}

        self.selected_component_configuration = []

        self.panel_checkboxes = {}

        self.component_checkboxes = {}

        self.project_managers = {}

        self.setWindowTitle(
            "Copy Configuration from Existing Panel"
        )

        self.resize(
            1100,
            700
        )

        self.build_ui()

        self.load_projects()

    # =========================================================
    # UI
    # =========================================================

    def build_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        # =====================================================
        # TITLE
        # =====================================================

        title = QLabel(
            "Copy Configuration from Existing Panel"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
            }
            """
        )

        main_layout.addWidget(
            title
        )

        description = QLabel(
            "Select a panel from any project. "
            "Its configuration can then be copied "
            "to the current panel."
        )

        description.setWordWrap(
            True
        )

        main_layout.addWidget(
            description
        )

        # =====================================================
        # MAIN AREA
        # =====================================================

        content_layout = QHBoxLayout()

        # =====================================================
        # LEFT: PANEL TREE
        # =====================================================

        tree_group = QGroupBox(
            "Select Source Panel"
        )

        tree_layout = QVBoxLayout(
            tree_group
        )

        self.panel_tree = QTreeWidget()

        self.panel_tree.setHeaderLabels(
            [
                "Project / Asset"
            ]
        )

        self.panel_tree.setSelectionMode(
            QTreeWidget.SelectionMode.SingleSelection
        )

        self.panel_tree.itemSelectionChanged.connect(
            self.on_panel_selected
        )

        tree_layout.addWidget(
            self.panel_tree
        )

        content_layout.addWidget(
            tree_group,
            1
        )

        # =====================================================
        # RIGHT: PARAMETERS
        # =====================================================

        parameter_group = QGroupBox(
            "Parameters to Import"
        )

        parameter_layout = QVBoxLayout(
            parameter_group
        )

        # -----------------------------------------------------
        # SELECT ALL / DESELECT ALL
        # -----------------------------------------------------

        selection_buttons = QHBoxLayout()

        self.select_all_button = QPushButton(
            "Select All"
        )

        self.deselect_all_button = QPushButton(
            "Deselect All"
        )

        self.select_all_button.clicked.connect(
            self.select_all_parameters
        )

        self.deselect_all_button.clicked.connect(
            self.deselect_all_parameters
        )

        selection_buttons.addWidget(
            self.select_all_button
        )

        selection_buttons.addWidget(
            self.deselect_all_button
        )

        selection_buttons.addStretch()

        parameter_layout.addLayout(
            selection_buttons
        )

        # -----------------------------------------------------
        # SCROLL AREA
        # -----------------------------------------------------

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll_widget = QWidget()

        self.parameter_scroll_layout = (
            QVBoxLayout(
                scroll_widget
            )
        )

        # =====================================================
        # PANEL PARAMETERS
        # =====================================================

        panel_group = QGroupBox(
            "Panel Configuration"
        )

        panel_layout = QVBoxLayout(
            panel_group
        )

        for key, label in (
            self.PANEL_PARAMETERS.items()
        ):

            checkbox = QCheckBox(
                label
            )

            checkbox.setChecked(
                True
            )

            self.panel_checkboxes[
                key
            ] = checkbox

            panel_layout.addWidget(
                checkbox
            )

        self.parameter_scroll_layout.addWidget(
            panel_group
        )

        # =====================================================
        # COMPONENT PARAMETERS
        # =====================================================

        component_group = QGroupBox(
            "Component Configuration"
        )

        component_layout = QVBoxLayout(
            component_group
        )

        for key, label in (
            self.COMPONENT_PARAMETERS.items()
        ):

            checkbox = QCheckBox(
                label
            )

            checkbox.setChecked(
                True
            )

            self.component_checkboxes[
                key
            ] = checkbox

            component_layout.addWidget(
                checkbox
            )

        self.parameter_scroll_layout.addWidget(
            component_group
        )

        self.parameter_scroll_layout.addStretch()

        scroll.setWidget(
            scroll_widget
        )

        parameter_layout.addWidget(
            scroll
        )

        content_layout.addWidget(
            parameter_group,
            1
        )

        main_layout.addLayout(
            content_layout
        )

        # =====================================================
        # BOTTOM BUTTONS
        # =====================================================

        buttons = QHBoxLayout()

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.import_button = QPushButton(
            "Import Configuration"
        )

        self.import_button.setEnabled(
            False
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        self.import_button.clicked.connect(
            self.accept_import
        )

        buttons.addStretch()

        buttons.addWidget(
            self.cancel_button
        )

        buttons.addWidget(
            self.import_button
        )

        main_layout.addLayout(
            buttons
        )

    # =========================================================
    # LOAD PROJECTS
    # =========================================================

    def load_projects(self):

        self.panel_tree.clear()

        if not self.projects_dir.exists():

            return

        project_folders = sorted(
            [
                folder
                for folder in self.projects_dir.iterdir()
                if folder.is_dir()
            ],
            key=lambda path:
                path.name.lower()
        )

        for project_folder in project_folders:

            assets_file = (
                project_folder /
                "assets.json"
            )

            if not assets_file.exists():
                continue

            try:

                asset_manager = AssetManager(
                    project_folder
                )

                self.project_managers[
                    project_folder.name
                ] = asset_manager

            except Exception:

                continue

            project_item = (
                QTreeWidgetItem()
            )

            project_item.setText(
                0,
                project_folder.name
            )

            project_item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                {
                    "type": "PROJECT",
                    "project_folder":
                        str(project_folder),
                }
            )

            self.panel_tree.addTopLevelItem(
                project_item
            )

            roots = (
                asset_manager.get_children(
                    None
                )
            )

            for root in roots:

                self.add_node_recursive(
                    project_item,
                    asset_manager,
                    root
                )

        self.panel_tree.collapseAll()

    # =========================================================
    # ADD NODE
    # =========================================================

    def add_node_recursive(
        self,
        parent_item,
        asset_manager,
        node,
    ):

        item = QTreeWidgetItem()

        item.setText(
            0,
            str(node.name)
        )

        item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            {
                "type":
                    str(
                        getattr(
                            node,
                            "node_type",
                            ""
                        )
                    ).upper(),

                "node_id":
                    node.node_id,

                "project_folder":
                    str(
                        asset_manager.project_folder
                    ),
            }
        )

        parent_item.addChild(
            item
        )

        children = (
            asset_manager.get_children(
                node.node_id
            )
        )

        for child in children:

            self.add_node_recursive(
                item,
                asset_manager,
                child
            )

    # =========================================================
    # PANEL SELECTED
    # =========================================================

    def on_panel_selected(self):

        item = (
            self.panel_tree.currentItem()
        )

        self.selected_panel = None

        self.import_button.setEnabled(
            False
        )

        if item is None:
            return

        data = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            data,
            dict
        ):
            return

        if data.get(
            "type"
        ) != "PANEL":

            return

        source_project_folder = Path(
            data[
                "project_folder"
            ]
        )

        source_manager = (
            self.project_managers.get(
                source_project_folder.name
            )
        )

        if source_manager is None:
            return

        source_panel = (
            source_manager.get_node(
                data["node_id"]
            )
        )

        if source_panel is None:
            return

        # Prevent copying a panel onto itself.

        if (
            self.target_project_folder
            and
            source_project_folder.resolve()
            == self.target_project_folder.resolve()
            and
            source_panel.node_id
            == self.target_panel_id
        ):

            self.import_button.setEnabled(
                False
            )

            return

        self.selected_panel = {
            "project_folder":
                source_project_folder,

            "asset_manager":
                source_manager,

            "panel":
                source_panel,
        }

        self.import_button.setEnabled(
            True
        )

    # =========================================================
    # SELECT ALL
    # =========================================================

    def select_all_parameters(self):

        for checkbox in (
            self.panel_checkboxes.values()
        ):

            checkbox.setChecked(
                True
            )

        for checkbox in (
            self.component_checkboxes.values()
        ):

            checkbox.setChecked(
                True
            )

    # =========================================================
    # DESELECT ALL
    # =========================================================

    def deselect_all_parameters(self):

        for checkbox in (
            self.panel_checkboxes.values()
        ):

            checkbox.setChecked(
                False
            )

        for checkbox in (
            self.component_checkboxes.values()
        ):

            checkbox.setChecked(
                False
            )

    # =========================================================
    # ACCEPT IMPORT
    # =========================================================

    def accept_import(self):

        if self.selected_panel is None:

            QMessageBox.warning(
                self,
                "No Source Panel",
                "Please select a source panel."
            )

            return

        # =====================================================
        # PANEL CONFIGURATION
        # =====================================================

        source_panel = (
            self.selected_panel[
                "panel"
            ]
        )

        panel_configuration = {}

        for key, checkbox in (
            self.panel_checkboxes.items()
        ):

            if not checkbox.isChecked():
                continue

            panel_configuration[
                key
            ] = getattr(
                source_panel,
                key,
                ""
            )

        # =====================================================
        # COMPONENT CONFIGURATION
        # =====================================================

        component_configuration = []

        source_manager = (
            self.selected_panel[
                "asset_manager"
            ]
        )

        source_component_manager = (
            ComponentManager(
                source_manager.project_folder
            )
        )

        source_components = (
            source_component_manager
            .get_panel_components(
                source_panel.node_id
            )
        )

        selected_component_keys = [

            key

            for key, checkbox in (
                self.component_checkboxes.items()
            )

            if checkbox.isChecked()
        ]

        for component in source_components:

            data = {

                # -----------------------------------------
                # STRUCTURAL
                #
                # These are copied internally so that
                # components can be matched by type/order.
                # They are NOT exposed as selectable unique
                # attributes.
                # -----------------------------------------

                "_source_component_type":
                    getattr(
                        component,
                        "component_type",
                        ""
                    ),

                "_source_component_name":
                    getattr(
                        component,
                        "name",
                        ""
                    ),

            }

            for key in selected_component_keys:

                data[key] = getattr(
                    component,
                    key,
                    ""
                )

            component_configuration.append(
                data
            )

        # =====================================================
        # RESULT
        # =====================================================

        self.selected_panel_configuration = (
            panel_configuration
        )

        self.selected_component_configuration = (
            component_configuration
        )

        self.accept()

    # =========================================================
    # RESULT
    # =========================================================

    def get_configuration(self):

        return {

            "panel_configuration":
                self.selected_panel_configuration,

            "component_configuration":
                self.selected_component_configuration,

        }