import json
from pathlib import Path

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
    QScrollArea,
    QWidget,
    QSizePolicy,
    QAbstractScrollArea,
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

        self.target_panel_id = target_panel_id

        self.selected_panel = None

        self.source_components = []

        self.checkboxes = {}

        self._configuration = {}

        # =====================================================
        # WINDOW
        # =====================================================

        self.setWindowTitle(
            "Import Panel Configuration"
        )

        self.setModal(True)

        # Keep the dialog within a normal laptop screen.
        self.resize(
            1100,
            720
        )

        self.setMinimumSize(
            850,
            550
        )

        self._apply_style()

        self._build_ui()

        self.load_projects()

    # =========================================================
    # STYLE
    # =========================================================

    def _apply_style(self):

        self.setStyleSheet(
            """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #3a3f46;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 14px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }

            QTreeWidget {
                border: 1px solid #3f444c;
                border-radius: 6px;
            }

            QTreeWidget::item {
                padding: 5px;
            }

            QTreeWidget::item:selected {
                background: #3f444c;
            }

            QCheckBox {
                min-height: 26px;
                padding: 2px;
            }

            QPushButton {
                min-height: 40px;
                padding-left: 14px;
                padding-right: 14px;
                border-radius: 6px;
            }

            QPushButton:hover {
                border: 1px solid #60a5fa;
            }

            QScrollArea {
                border: 1px solid #3f444c;
                border-radius: 6px;
            }

            QScrollBar:vertical {
                width: 14px;
                margin: 1px;
            }

            QScrollBar::handle:vertical {
                min-height: 30px;
                border-radius: 5px;
            }

            QScrollBar:horizontal {
                height: 12px;
            }
            """
        )

    # =========================================================
    # BUILD UI
    # =========================================================

    def _build_ui(self):

        layout = QVBoxLayout(
            self
        )

        layout.setContentsMargins(
            18,
            16,
            18,
            16
        )

        layout.setSpacing(
            10
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

        description.setWordWrap(
            True
        )

        description.setStyleSheet(
            """
            QLabel {
                color: #9ca3af;
                font-size: 13px;
            }
            """
        )

        layout.addWidget(
            description
        )

        # =====================================================
        # MAIN CONTENT
        # =====================================================

        main_layout = QHBoxLayout()

        main_layout.setSpacing(
            10
        )

        # =====================================================
        # LEFT: PANEL TREE
        # =====================================================

        tree_group = QGroupBox(
            "Available Panels"
        )

        tree_group.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        tree_layout = QVBoxLayout(
            tree_group
        )

        tree_layout.setContentsMargins(
            10,
            15,
            10,
            10
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
            280
        )

        self.panel_tree.setUniformRowHeights(
            True
        )

        self.panel_tree.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        self.panel_tree.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.panel_tree.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
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
        # RIGHT: PARAMETERS
        # =====================================================

        parameter_group = QGroupBox(
            "Parameters to Import"
        )

        parameter_group.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        parameter_layout = QVBoxLayout(
            parameter_group
        )

        parameter_layout.setContentsMargins(
            10,
            15,
            10,
            10
        )

        parameter_layout.setSpacing(
            8
        )

        # =====================================================
        # SELECT / DESELECT
        # =====================================================

        selection_buttons = QHBoxLayout()

        select_all = QPushButton(
            "Select All"
        )

        deselect_all = QPushButton(
            "Deselect All"
        )

        select_all.setMinimumHeight(
            38
        )

        deselect_all.setMinimumHeight(
            38
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

        # =====================================================
        # IMPORTANT:
        #
        # The scroll area gets the remaining height.
        # The contents are allowed to become taller than it.
        # =====================================================

        self.parameter_scroll = QScrollArea()

        self.parameter_scroll.setWidgetResizable(
            True
        )

        self.parameter_scroll.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustIgnored
        )

        self.parameter_scroll.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        self.parameter_scroll.setMinimumHeight(
            200
        )

        self.parameter_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.parameter_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.parameter_scroll.setFrameShape(
            QScrollArea.Shape.NoFrame
        )

        # =====================================================
        # SCROLL CONTENT
        # =====================================================

        self.parameter_container = QWidget()

        self.parameter_container.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred
        )

        self.parameter_container.setMinimumWidth(
            0
        )

        self.parameter_container.setMinimumHeight(
            0
        )

        self.parameter_layout = QVBoxLayout(
            self.parameter_container
        )

        self.parameter_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        self.parameter_layout.setSpacing(
            4
        )

        # IMPORTANT:
        # No stretch here.
        #
        # The widget must be allowed to become taller
        # than the viewport so QScrollArea can scroll it.
        # =====================================================

        self.parameter_scroll.setWidget(
            self.parameter_container
        )

        parameter_layout.addWidget(
            self.parameter_scroll,
            1
        )

        main_layout.addWidget(
            parameter_group,
            1
        )

        # =====================================================
        # MAIN LAYOUT
        # =====================================================

        layout.addLayout(
            main_layout,
            1
        )

        # =====================================================
        # BOTTOM BUTTONS
        # =====================================================

        buttons = QHBoxLayout()

        buttons.addStretch()

        cancel_button = QPushButton(
            "Cancel"
        )

        import_button = QPushButton(
            "Import Configuration"
        )

        cancel_button.setMinimumHeight(
            42
        )

        import_button.setMinimumHeight(
            42
        )

        cancel_button.clicked.connect(
            self.reject
        )

        import_button.clicked.connect(
            self.accept_selection
        )

        buttons.addWidget(
            cancel_button
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

        try:

            project_folders = sorted(
                [
                    p
                    for p in self.projects_dir.iterdir()
                    if p.is_dir()
                ],
                key=lambda p:
                    p.name.lower()
            )

        except Exception:

            return

        for project_folder in project_folders:

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
                    "folder": str(
                        project_folder
                    )
                }
            )

            self.panel_tree.addTopLevelItem(
                project_item
            )

            self.load_project_assets(
                project_item,
                project_folder
            )

        # =====================================================
        # IMPORTANT:
        # START COLLAPSED
        # =====================================================

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

                data = json.load(
                    file
                )

        except Exception:

            return

        if isinstance(
            data,
            list
        ):

            assets = data

        elif isinstance(
            data,
            dict
        ):

            assets = data.get(
                "assets",
                []
            )

        else:

            assets = []

        if not isinstance(
            assets,
            list
        ):

            return

        items = {}

        # =====================================================
        # CREATE ALL ITEMS
        # =====================================================

        for asset in assets:

            if not isinstance(
                asset,
                dict
            ):

                continue

            node_id = (
                asset.get(
                    "node_id"
                )
                or
                asset.get(
                    "id"
                )
            )

            if not node_id:

                continue

            name = str(
                asset.get(
                    "name",
                    ""
                )
                or
                ""
            )

            node_type = str(
                asset.get(
                    "node_type",
                    asset.get(
                        "type",
                        ""
                    )
                )
                or
                ""
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

            items[
                str(node_id)
            ] = item

        # =====================================================
        # BUILD TREE
        # =====================================================

        for asset in assets:

            if not isinstance(
                asset,
                dict
            ):

                continue

            node_id = (
                asset.get(
                    "node_id"
                )
                or
                asset.get(
                    "id"
                )
            )

            item = items.get(
                str(node_id)
            )

            if item is None:

                continue

            parent_id = (
                asset.get(
                    "parent_id"
                )
            )

            if parent_id is not None:

                parent_item = items.get(
                    str(parent_id)
                )

            else:

                parent_item = None

            if parent_item is not None:

                parent_item.addChild(
                    item
                )

            else:

                project_item.addChild(
                    item
                )

    # =========================================================
    # PANEL SELECTED
    # =========================================================

    def on_panel_selected(self):

        selected_items = (
            self.panel_tree.selectedItems()
        )

        if not selected_items:

            self.selected_panel = None

            self.clear_parameter_checkboxes()

            return

        item = selected_items[0]

        asset = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            asset,
            dict
        ):

            self.selected_panel = None

            self.clear_parameter_checkboxes()

            return

        node_type = str(
            asset.get(
                "node_type",
                asset.get(
                    "type",
                    ""
                )
            )
            or
            ""
        ).strip().upper()

        # =====================================================
        # ONLY PANELS
        # =====================================================

        if node_type != "PANEL":

            self.selected_panel = None

            self.clear_parameter_checkboxes()

            return

        source_panel_id = (
            asset.get(
                "node_id",
                asset.get(
                    "id"
                )
            )
        )

        # =====================================================
        # DON'T ALLOW SAME PANEL
        # =====================================================

        if (
            self.target_panel_id is not None
            and
            str(source_panel_id)
            ==
            str(self.target_panel_id)
        ):

            self.selected_panel = None

            self.clear_parameter_checkboxes()

            QMessageBox.information(
                self,
                "Invalid Source Panel",
                "The current panel cannot be used "
                "as its own configuration source."
            )

            return

        self.selected_panel = asset

        self.load_parameter_checkboxes(
            asset
        )

    # =========================================================
    # LOAD PARAMETERS
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
            panel.get(
                "equipment_name",
                ""
            ),
            True
        )

        self.add_checkbox(
            "panel_equipment_type",
            "Equipment Type",
            panel.get(
                "equipment_type",
                ""
            ),
            True
        )

        self.add_checkbox(
            "panel_ct_count",
            "Number of CTs",
            panel.get(
                "ct_count",
                0
            ),
            True
        )

        self.add_checkbox(
            "panel_relay_count",
            "Number of Numerical Relays",
            panel.get(
                "relay_count",
                0
            ),
            True
        )

        self.add_checkbox(
            "panel_aux_count",
            "Number of Auxiliary Relays",
            panel.get(
                "aux_count",
                0
            ),
            True
        )

        self.add_checkbox(
            "panel_meter_count",
            "Number of Meters",
            panel.get(
                "meter_count",
                0
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

        # =====================================================
        # RESET SCROLL
        # =====================================================

        self.parameter_scroll.verticalScrollBar().setValue(
            0
        )

        self.parameter_scroll.horizontalScrollBar().setValue(
            0
        )

        # Force geometry update.
        self.parameter_container.adjustSize()

    # =========================================================
    # COMPONENT CHECKBOXES
    # =========================================================

    def add_component_checkboxes(
        self,
        index,
        component
    ):

        component_type = (
            self.normalise_component_type(
                component.get(
                    "component_type",
                    ""
                )
            )
        )

        name = str(
            component.get(
                "name",
                f"Component {index + 1}"
            )
            or
            ""
        )

        prefix = (
            f"component_{index}_"
        )

        # =====================================================
        # HEADER
        # =====================================================

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
                margin-bottom: 3px;
            }
            """
        )

        self.parameter_layout.addWidget(
            header
        )

        self.checkboxes[
            prefix + "ALL"
        ] = header

        # =====================================================
        # COMMON
        # =====================================================

        self.add_checkbox(
            prefix + "serial_number",
            f"{name}: Serial Number",
            component.get(
                "serial_number",
                ""
            ),
            False
        )

        self.add_checkbox(
            prefix + "manufacturer",
            f"{name}: Manufacturer",
            component.get(
                "manufacturer",
                ""
            ),
            True
        )

        self.add_checkbox(
            prefix + "model",
            f"{name}: Model",
            component.get(
                "model",
                ""
            ),
            True
        )

        self.add_checkbox(
            prefix + "description",
            f"{name}: Description",
            component.get(
                "description",
                ""
            ),
            True
        )

        # =====================================================
        # CT
        # =====================================================

        if component_type == "CT":

            fields = [

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

            for field, label in fields:

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

        elif component_type == "NUMERICAL RELAY":

            fields = [

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

            for field, label in fields:

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

        elif component_type == "AUXILIARY RELAY":

            fields = [

                (
                    "coil_voltage",
                    "Coil Voltage"
                ),

                (
                    "contact_configuration",
                    "Contact Configuration"
                ),
            ]

            for field, label in fields:

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

        elif component_type == "METER":

            fields = [

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

            for field, label in fields:

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
        # HEADER CONTROLS COMPONENT
        # =====================================================

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

        checkbox.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed
        )

        checkbox.setToolTip(
            f"Current value: "
            f"{self.format_value(value)}"
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
            list(
                self.checkboxes.items()
            )
        ):

            if (
                key.startswith(prefix)
                and
                key != prefix + "ALL"
            ):

                checkbox.blockSignals(
                    True
                )

                checkbox.setChecked(
                    checked
                )

                checkbox.blockSignals(
                    False
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

            checkbox.blockSignals(
                True
            )

            checkbox.setChecked(
                checked
            )

            checkbox.blockSignals(
                False
            )

    # =========================================================
    # CLEAR PARAMETERS
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

            if widget is not None:

                widget.deleteLater()

        self.parameter_container.adjustSize()

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

        if isinstance(
            data,
            list
        ):

            components = data

        elif isinstance(
            data,
            dict
        ):

            components = data.get(
                "components",
                []
            )

        else:

            components = []

        if not isinstance(
            components,
            list
        ):

            return []

        panel_id = (
            panel.get(
                "node_id",
                panel.get(
                    "id"
                )
            )
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
                ==
                str(panel_id)
            ):

                result.append(
                    component
                )

        return result

    # =========================================================
    # FIND PROJECT FOLDER
    # =========================================================

    def find_project_folder(
        self,
        panel
    ):

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

        panel_id = (
            panel.get(
                "node_id",
                panel.get(
                    "id"
                )
            )
        )

        try:

            folders = (
                self.projects_dir.iterdir()
            )

        except Exception:

            return None

        for folder in folders:

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

            if isinstance(
                data,
                list
            ):

                assets = data

            elif isinstance(
                data,
                dict
            ):

                assets = data.get(
                    "assets",
                    []
                )

            else:

                assets = []

            for asset in assets:

                if not isinstance(
                    asset,
                    dict
                ):

                    continue

                asset_id = (
                    asset.get(
                        "node_id",
                        asset.get(
                            "id"
                        )
                    )
                )

                if (
                    str(asset_id)
                    ==
                    str(panel_id)
                ):

                    return folder

        return None

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

        if not configuration:

            return

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

        panel_configuration = {}

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

        # =====================================================
        # PANEL PARAMETERS
        # =====================================================

        for checkbox_key, field in (
            panel_mapping.items()
        ):

            checkbox = (
                self.checkboxes.get(
                    checkbox_key
                )
            )

            if (
                checkbox is not None
                and
                checkbox.isChecked()
            ):

                panel_configuration[
                    field
                ] = panel.get(
                    field,
                    ""
                )

        # =====================================================
        # COMPONENT PARAMETERS
        # =====================================================

        imported_components = []

        for index, source in enumerate(
            self.source_components
        ):

            prefix = (
                f"component_{index}_"
            )

            imported = {

                "component_type":
                    source.get(
                        "component_type",
                        ""
                    ),

                "name":
                    source.get(
                        "name",
                        ""
                    ),
            }

            fields = [

                "manufacturer",
                "model",
                "description",

                # Unique, unchecked by default.
                "serial_number",

                # CT
                "ct_primary",
                "ct_secondary",
                "ct_ratio",
                "ct_class",
                "burden",
                "core",

                # Relay
                "vt_ratio",
                "firmware",
                "protection_functions",

                # Aux relay
                "coil_voltage",
                "contact_configuration",

                # Meter
                "meter_type",
                "meter_functions",
                "accuracy_class",
            ]

            for field in fields:

                checkbox = (
                    self.checkboxes.get(
                        prefix + field
                    )
                )

                if (
                    checkbox is not None
                    and
                    checkbox.isChecked()
                ):

                    imported[
                        field
                    ] = source.get(
                        field,
                        ""
                    )

            imported_components.append(
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
                panel_configuration,

            "components":
                imported_components,
        }

    # =========================================================
    # GET CONFIGURATION
    # =========================================================

    def get_configuration(self):

        return self._configuration

    # =========================================================
    # NORMALISE COMPONENT TYPE
    # =========================================================

    @staticmethod
    def normalise_component_type(
        value
    ):

        value = str(
            value or ""
        ).strip().upper()

        aliases = {

            "CT":
                "CT",

            "CURRENT TRANSFORMER":
                "CT",

            "NUMERICAL RELAY":
                "NUMERICAL RELAY",

            "NUMERICAL_RELAY":
                "NUMERICAL RELAY",

            "RELAY":
                "NUMERICAL RELAY",

            "AUX":
                "AUXILIARY RELAY",

            "AUX RELAY":
                "AUXILIARY RELAY",

            "AUXILIARY RELAY":
                "AUXILIARY RELAY",

            "AUXILIARY_RELAY":
                "AUXILIARY RELAY",

            "METER":
                "METER",

            "METERING":
                "METER",
        }

        return aliases.get(
            value,
            value
        )

    # =========================================================
    # FORMAT VALUE
    # =========================================================

    @staticmethod
    def format_value(
        value
    ):

        if value is None:

            return ""

        if isinstance(
            value,
            list
        ):

            return ", ".join(
                str(item)
                for item in value
            )

        if isinstance(
            value,
            dict
        ):

            return json.dumps(
                value,
                ensure_ascii=False
            )

        return str(
            value
        )