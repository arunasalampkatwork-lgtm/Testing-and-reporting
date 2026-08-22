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
    QCheckBox,
    QPushButton,
    QMessageBox,
    QGroupBox,
)


class PanelConfigurationCopyDialog(QDialog):

    def __init__(
        self,
        projects_dir,
        target_project_folder=None,
        target_panel_id=None,
        parent=None
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

        self.source_components = []

        self.checkboxes = {}

        self.setWindowTitle(
            "Import Panel Configuration"
        )

        self.resize(
            1000,
            700
        )

        self.build_ui()

        self.load_projects()

    # =========================================================
    # UI
    # =========================================================

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )

        # =====================================================
        # TITLE
        # =====================================================

        title = QLabel(
            "IMPORT CONFIGURATION FROM EXISTING PANEL"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 22px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            title
        )

        description = QLabel(
            "Select a panel and choose which configuration "
            "parameters should be copied."
        )

        description.setStyleSheet(
            """
            QLabel {
                color: #9ca3af;
            }
            """
        )

        layout.addWidget(
            description
        )

        # =====================================================
        # MAIN SPLIT
        # =====================================================

        main_layout = QHBoxLayout()

        # =====================================================
        # PANEL TREE
        # =====================================================

        tree_group = QGroupBox(
            "Available Panels"
        )

        tree_layout = QVBoxLayout(
            tree_group
        )

        self.panel_tree = QTreeWidget()

        self.panel_tree.setHeaderLabels(
            [
                "Asset",
                "Type"
            ]
        )

        self.panel_tree.setColumnWidth(
            0,
            300
        )

        self.panel_tree.itemSelectionChanged.connect(
            self.on_panel_selected
        )

        tree_layout.addWidget(
            self.panel_tree
        )

        main_layout.addWidget(
            tree_group,
            1
        )

        # =====================================================
        # PARAMETERS
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

        select_all = QPushButton(
            "Select All"
        )

        deselect_all = QPushButton(
            "Deselect All"
        )

        select_all.clicked.connect(
            lambda:
            self.set_all_checked(True)
        )

        deselect_all.clicked.connect(
            lambda:
            self.set_all_checked(False)
        )

        selection_buttons.addWidget(
            select_all
        )

        selection_buttons.addWidget(
            deselect_all
        )

        parameter_layout.addLayout(
            selection_buttons
        )

        # -----------------------------------------------------
        # CHECKBOX AREA
        # -----------------------------------------------------

        self.parameter_layout = QVBoxLayout()

        parameter_layout.addLayout(
            self.parameter_layout
        )

        parameter_layout.addStretch()

        main_layout.addWidget(
            parameter_group,
            1
        )

        layout.addLayout(
            main_layout
        )

        # =====================================================
        # BUTTONS
        # =====================================================

        buttons = QHBoxLayout()

        cancel = QPushButton(
            "Cancel"
        )

        import_button = QPushButton(
            "Import Configuration"
        )

        cancel.clicked.connect(
            self.reject
        )

        import_button.clicked.connect(
            self.accept_selection
        )

        buttons.addStretch()

        buttons.addWidget(
            cancel
        )

        buttons.addWidget(
            import_button
        )

        layout.addLayout(
            buttons
        )

    # =========================================================
    # LOAD PROJECTS
    # =========================================================

    def load_projects(self):

        self.panel_tree.clear()

        if not self.projects_dir.exists():

            return

        for project_folder in sorted(
            self.projects_dir.iterdir()
        ):

            if not project_folder.is_dir():

                continue

            project_item = QTreeWidgetItem(
                [
                    project_folder.name,
                    "Project"
                ]
            )

            project_item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                {
                    "type": "project",
                    "folder": project_folder
                }
            )

            self.panel_tree.addTopLevelItem(
                project_item
            )

            self.load_project_assets(
                project_item,
                project_folder
            )

        # -----------------------------------------------------
        # EVERYTHING COLLAPSED BY DEFAULT
        # -----------------------------------------------------

        self.panel_tree.collapseAll()

    # =========================================================
    # LOAD PROJECT ASSETS
    # =========================================================

    def load_project_assets(
        self,
        project_item,
        project_folder
    ):

        assets_file = (
            project_folder /
            "assets.json"
        )

        if not assets_file.exists():

            return

        try:

            with open(
                assets_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

        except Exception:

            return

        assets = (
            data
            if isinstance(data, list)
            else data.get(
                "assets",
                []
            )
        )

        items = {}

        # -----------------------------------------------------
        # CREATE ITEMS
        # -----------------------------------------------------

        for asset in assets:

            if not isinstance(
                asset,
                dict
            ):

                continue

            node_id = (
                asset.get("node_id")
                or asset.get("id")
            )

            parent_id = (
                asset.get("parent_id")
            )

            name = str(
                asset.get(
                    "name",
                    ""
                )
            )

            node_type = str(
                asset.get(
                    "node_type",
                    asset.get(
                        "type",
                        ""
                    )
                )
            )

            item = QTreeWidgetItem(
                [
                    name,
                    node_type
                ]
            )

            item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                asset
            )

            items[node_id] = item

        # -----------------------------------------------------
        # BUILD TREE
        # -----------------------------------------------------

        for asset in assets:

            node_id = (
                asset.get("node_id")
                or asset.get("id")
            )

            parent_id = (
                asset.get("parent_id")
            )

            item = items.get(
                node_id
            )

            if item is None:

                continue

            if parent_id in items:

                items[
                    parent_id
                ].addChild(
                    item
                )

            else:

                project_item.addChild(
                    item
                )

    # =========================================================
    # PANEL SELECTION
    # =========================================================

    def on_panel_selected(self):

        items = (
            self.panel_tree.selectedItems()
        )

        if not items:

            return

        asset = items[0].data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            asset,
            dict
        ):

            return

        node_type = str(
            asset.get(
                "node_type",
                asset.get(
                    "type",
                    ""
                )
            )
        ).upper()

        if node_type != "PANEL":

            self.selected_panel = None

            return

        self.selected_panel = asset

        self.load_parameter_checkboxes(
            asset
        )

    # =========================================================
    # PARAMETERS
    # =========================================================

    def load_parameter_checkboxes(
        self,
        panel
    ):

        self.clear_parameter_checkboxes()

        # =====================================================
        # PANEL PARAMETERS
        # =====================================================

        self.add_checkbox(
            "panel_equipment_name",
            "Equipment Name",
            self.get_value(
                panel,
                "equipment_name"
            ),
            True
        )

        self.add_checkbox(
            "panel_equipment_type",
            "Equipment Type",
            self.get_value(
                panel,
                "equipment_type"
            ),
            True
        )

        self.add_checkbox(
            "panel_ct_count",
            "Number of CTs",
            self.get_value(
                panel,
                "ct_count"
            ),
            True
        )

        self.add_checkbox(
            "panel_relay_count",
            "Number of Numerical Relays",
            self.get_value(
                panel,
                "relay_count"
            ),
            True
        )

        self.add_checkbox(
            "panel_aux_count",
            "Number of Auxiliary Relays",
            self.get_value(
                panel,
                "aux_count"
            ),
            True
        )

        self.add_checkbox(
            "panel_meter_count",
            "Number of Meters",
            self.get_value(
                panel,
                "meter_count"
            ),
            True
        )

        # =====================================================
        # COMPONENTS
        # =====================================================

        self.source_components = (
            self.load_components_for_panel(
                panel
            )
        )

        for index, component in enumerate(
            self.source_components
        ):

            self.add_component_checkboxes(
                index,
                component
            )

    # =========================================================
    # COMPONENT CHECKBOXES
    # =========================================================

    def add_component_checkboxes(
        self,
        index,
        component
    ):

        component_type = str(
            component.get(
                "component_type",
                ""
            )
        ).upper()

        name = str(
            component.get(
                "name",
                f"Component {index + 1}"
            )
        )

        prefix = (
            f"component_{index}_"
        )

        # -----------------------------------------------------
        # COMPONENT HEADER
        # -----------------------------------------------------

        header = QCheckBox(
            f"{name} ({component_type}) - ALL"
        )

        header.setChecked(
            True
        )

        header.setStyleSheet(
            """
            QCheckBox {
                font-weight: bold;
                margin-top: 8px;
            }
            """
        )

        self.parameter_layout.addWidget(
            header
        )

        self.checkboxes[
            prefix + "ALL"
        ] = header

        # -----------------------------------------------------
        # COMMON
        # -----------------------------------------------------

        common_fields = [
            (
                "manufacturer",
                "Manufacturer"
            ),
            (
                "model",
                "Model"
            ),
            (
                "description",
                "Description"
            ),
        ]

        # -----------------------------------------------------
        # UNIQUE FIELD
        # -----------------------------------------------------

        self.add_checkbox(
            prefix + "serial_number",
            f"{name}: Serial Number",
            component.get(
                "serial_number",
                ""
            ),
            False
        )

        # -----------------------------------------------------
        # COMMON FIELDS
        # -----------------------------------------------------

        for field, label in common_fields:

            self.add_checkbox(
                prefix + field,
                f"{name}: {label}",
                component.get(
                    field,
                    ""
                ),
                True
            )

        # =====================================================
        # CT
        # =====================================================

        if component_type == "CT":

            ct_fields = [

                (
                    "ct_primary",
                    "CT Primary"
                ),

                (
                    "ct_secondary",
                    "CT Secondary"
                ),

                (
                    "ct_ratio",
                    "CT Ratio"
                ),

                (
                    "ct_class",
                    "CT Class"
                ),

                (
                    "burden",
                    "Burden"
                ),

                (
                    "core",
                    "Core"
                ),
            ]

            for field, label in ct_fields:

                self.add_checkbox(
                    prefix + field,
                    f"{name}: {label}",
                    component.get(
                        field,
                        ""
                    ),
                    True
                )

        # =====================================================
        # NUMERICAL RELAY
        # =====================================================

        elif component_type in (
            "NUMERICAL RELAY",
            "RELAY",
            "NUMERICAL_RELAY"
        ):

            relay_fields = [

                (
                    "vt_ratio",
                    "VT Ratio"
                ),

                (
                    "firmware",
                    "Firmware"
                ),

                (
                    "protection_functions",
                    "Protection Functions"
                ),
            ]

            for field, label in relay_fields:

                self.add_checkbox(
                    prefix + field,
                    f"{name}: {label}",
                    component.get(
                        field,
                        ""
                    ),
                    True
                )

        # =====================================================
        # AUXILIARY RELAY
        # =====================================================

        elif component_type in (
            "AUX",
            "AUX RELAY",
            "AUXILIARY RELAY",
            "AUXILIARY_RELAY"
        ):

            aux_fields = [

                (
                    "coil_voltage",
                    "Coil Voltage"
                ),

                (
                    "contact_configuration",
                    "Contact Configuration"
                ),
            ]

            for field, label in aux_fields:

                self.add_checkbox(
                    prefix + field,
                    f"{name}: {label}",
                    component.get(
                        field,
                        ""
                    ),
                    True
                )

        # =====================================================
        # METER
        # =====================================================

        elif component_type in (
            "METER",
            "METERING"
        ):

            meter_fields = [

                (
                    "meter_type",
                    "Meter Type"
                ),

                (
                    "meter_functions",
                    "Meter Functions"
                ),

                (
                    "accuracy_class",
                    "Accuracy Class"
                ),
            ]

            for field, label in meter_fields:

                self.add_checkbox(
                    prefix + field,
                    f"{name}: {label}",
                    component.get(
                        field,
                        ""
                    ),
                    True
                )

        # -----------------------------------------------------
        # COMPONENT SELECT-ALL CONNECTION
        # -----------------------------------------------------

        header.toggled.connect(
            lambda checked,
            p=prefix:
            self.toggle_component(
                p,
                checked
            )
        )

    # =========================================================
    # ADD CHECKBOX
    # =========================================================

    def add_checkbox(
        self,
        key,
        label,
        value,
        checked=True
    ):

        checkbox = QCheckBox(
            label
        )

        checkbox.setChecked(
            checked
        )

        checkbox.setToolTip(
            f"Current value: {value}"
        )

        self.parameter_layout.addWidget(
            checkbox
        )

        self.checkboxes[
            key
        ] = checkbox

    # =========================================================
    # TOGGLE COMPONENT
    # =========================================================

    def toggle_component(
        self,
        prefix,
        checked
    ):

        for key, checkbox in (
            self.checkboxes.items()
        ):

            if (
                key.startswith(prefix)
                and key != prefix + "ALL"
            ):

                checkbox.setChecked(
                    checked
                )

    # =========================================================
    # SELECT ALL
    # =========================================================

    def set_all_checked(
        self,
        checked
    ):

        for checkbox in (
            self.checkboxes.values()
        ):

            checkbox.setChecked(
                checked
            )

    # =========================================================
    # CLEAR CHECKBOXES
    # =========================================================

    def clear_parameter_checkboxes(
        self
    ):

        self.checkboxes.clear()

        while (
            self.parameter_layout.count()
        ):

            item = (
                self.parameter_layout.takeAt(
                    0
                )
            )

            widget = item.widget()

            if widget:

                widget.deleteLater()

    # =========================================================
    # LOAD COMPONENTS
    # =========================================================

    def load_components_for_panel(
        self,
        panel
    ):

        project_folder = (
            self.find_project_folder(
                panel
            )
        )

        if project_folder is None:

            return []

        components_file = (
            project_folder /
            "components.json"
        )

        if not components_file.exists():

            return []

        try:

            with open(
                components_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

        except Exception:

            return []

        components = (
            data
            if isinstance(
                data,
                list
            )
            else data.get(
                "components",
                []
            )
        )

        panel_id = (
            panel.get("node_id")
            or panel.get("id")
        )

        result = []

        for component in components:

            if not isinstance(
                component,
                dict
            ):

                continue

            component_panel_id = (
                component.get(
                    "panel_id"
                )
            )

            if (
                str(component_panel_id)
                == str(panel_id)
            ):

                result.append(
                    component
                )

        return result

    # =========================================================
    # FIND PROJECT
    # =========================================================

    def find_project_folder(
        self,
        panel
    ):

        current = (
            self.projects_dir
        )

        project_id = (
            panel.get(
                "project_id"
            )
        )

        if project_id:

            candidate = (
                self.projects_dir /
                str(project_id)
            )

            if candidate.exists():

                return candidate

        # -----------------------------------------------------
        # Fallback: search projects
        # -----------------------------------------------------

        for folder in (
            self.projects_dir.iterdir()
        ):

            if not folder.is_dir():

                continue

            assets_file = (
                folder /
                "assets.json"
            )

            if not assets_file.exists():

                continue

            try:

                with open(
                    assets_file,
                    "r",
                    encoding="utf-8"
                ) as file:

                    data = json.load(
                        file
                    )

            except Exception:

                continue

            assets = (
                data
                if isinstance(
                    data,
                    list
                )
                else data.get(
                    "assets",
                    []
                )
            )

            panel_id = (
                panel.get("node_id")
                or panel.get("id")
            )

            for asset in assets:

                if not isinstance(
                    asset,
                    dict
                ):

                    continue

                asset_id = (
                    asset.get("node_id")
                    or asset.get("id")
                )

                if str(asset_id) == str(
                    panel_id
                ):

                    return folder

        return None

    # =========================================================
    # VALUE
    # =========================================================

    @staticmethod
    def get_value(
        data,
        key
    ):

        value = data.get(
            key,
            ""
        )

        if isinstance(
            value,
            list
        ):

            return ", ".join(
                str(x)
                for x in value
            )

        return str(
            value or ""
        )

    # =========================================================
    # ACCEPT
    # =========================================================

    def accept_selection(self):

        if self.selected_panel is None:

            QMessageBox.warning(
                self,
                "No Panel Selected",
                "Please select a panel from the tree."
            )

            return

        configuration = (
            self.build_configuration()
        )

        self._configuration = (
            configuration
        )

        self.accept()

    # =========================================================
    # BUILD CONFIGURATION
    # =========================================================

    def build_configuration(
        self
    ):

        panel = (
            self.selected_panel
        )

        panel_config = {}

        # -----------------------------------------------------
        # PANEL FIELDS
        # -----------------------------------------------------

        panel_mapping = {

            "panel_equipment_name":
                "equipment_name",

            "panel_equipment_type":
                "equipment_type",

            "panel_ct_count":
                "ct_count",

            "panel_relay_count":
                "relay_count",

            "panel_aux_count":
                "aux_count",

            "panel_meter_count":
                "meter_count",
        }

        for checkbox_key, field in (
            panel_mapping.items()
        ):

            checkbox = (
                self.checkboxes.get(
                    checkbox_key
                )
            )

            if checkbox and checkbox.isChecked():

                panel_config[
                    field
                ] = panel.get(
                    field,
                    ""
                )

        # -----------------------------------------------------
        # COMPONENTS
        # -----------------------------------------------------

        components = []

        for index, component in enumerate(
            self.source_components
        ):

            prefix = (
                f"component_{index}_"
            )

            imported = {}

            # -------------------------------------------------
            # ALWAYS KEEP COMPONENT TYPE
            # -------------------------------------------------

            imported[
                "component_type"
            ] = component.get(
                "component_type",
                ""
            )

            # -------------------------------------------------
            # COMPONENT NAME
            # -------------------------------------------------

            imported[
                "name"
            ] = component.get(
                "name",
                ""
            )

            # -------------------------------------------------
            # COMPONENT FIELDS
            # -------------------------------------------------

            for field in (
                "manufacturer",
                "model",
                "description",
                "serial_number",
                "ct_primary",
                "ct_secondary",
                "ct_ratio",
                "ct_class",
                "burden",
                "core",
                "vt_ratio",
                "firmware",
                "coil_voltage",
                "contact_configuration",
                "meter_type",
                "meter_functions",
                "accuracy_class",
                "protection_functions",
            ):

                checkbox = self.checkboxes.get(
                    prefix + field
                )

                if (
                    checkbox
                    and checkbox.isChecked()
                ):

                    imported[
                        field
                    ] = component.get(
                        field,
                        ""
                    )

            components.append(
                imported
            )

        return {

            "source_panel_name":
                panel.get(
                    "name",
                    ""
                ),

            "source_panel_id":
                panel.get(
                    "node_id",
                    panel.get(
                        "id"
                    )
                ),

            "panel_configuration":
                panel_config,

            "components":
                components,
        }

    # =========================================================
    # GET CONFIGURATION
    # =========================================================

    def get_configuration(self):

        return getattr(
            self,
            "_configuration",
            {}
        )