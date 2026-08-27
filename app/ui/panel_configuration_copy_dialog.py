
import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTreeWidget,
    QTreeWidgetItem, QCheckBox, QPushButton, QMessageBox,
    QGroupBox, QScrollArea, QWidget, QSizePolicy
)

from app.services.asset_manager import AssetManager
from app.services.component_manager import ComponentManager


class PanelConfigurationCopyDialog(QDialog):

    PANEL_PARAMETERS = {
        "equipment_name": "Equipment Name",
        "equipment_type": "Equipment Type",
        "ct_count": "Number of CTs",
        "relay_count": "Number of Numerical Relays",
        "aux_count": "Number of Auxiliary Relays",
        "meter_count": "Number of Meters",
    }

    COMPONENT_PARAMETERS = {
        "manufacturer": "Manufacturer",
        "model": "Model",
        "description": "Description",
        "ct_primary": "CT Primary",
        "ct_secondary": "CT Secondary",
        "ct_ratio": "CT Ratio",
        "ct_class": "CT Class",
        "burden": "Burden",
        "core": "Core",
        "vt_ratio": "VT Ratio",
        "firmware": "Firmware",
        "coil_voltage": "Coil Voltage",
        "contact_configuration": "Contact Configuration",
        "meter_type": "Meter Type",
        "meter_functions": "Meter Functions",
        "accuracy_class": "Accuracy Class",
        "protection_functions": "Protection Functions",
    }

    UNIQUE_PARAMETERS = {
        "component_id",
        "panel_id",
        "name",
        "component_name",
        "serial_number",
    }

    def __init__(
        self,
        projects_dir,
        target_project_folder=None,
        target_panel_id=None,
        parent=None,
        **kwargs
    ):
        super().__init__(parent)

        # Backward compatibility with older callers.
        if projects_dir is None:
            projects_dir = kwargs.get("project_folder")

        self.projects_dir = Path(projects_dir)
        self.target_project_folder = (
            Path(target_project_folder)
            if target_project_folder else None
        )
        self.target_panel_id = target_panel_id

        self.selected_panel = None
        self.source_components = []
        self.panel_checkboxes = {}
        self.component_checkboxes = {}
        self._component_checkbox_field = {}

        self.setWindowTitle("Import Panel Configuration")
        self.resize(1150, 760)
        self.setMinimumSize(900, 600)

        self._build_ui()
        self.load_projects()

    def _build_ui(self):
        root = QVBoxLayout(self)

        title = QLabel("IMPORT CONFIGURATION FROM EXISTING PANEL")
        title.setStyleSheet("font-size:22px;font-weight:bold;")
        root.addWidget(title)

        subtitle = QLabel(
            "Select a source panel and choose every configuration "
            "parameter you want copied. Unique identifiers are excluded."
        )
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        content = QHBoxLayout()
        root.addLayout(content, 1)

        left = QGroupBox("Available Panels")
        left_layout = QVBoxLayout(left)

        self.panel_tree = QTreeWidget()
        self.panel_tree.setHeaderLabels(["Asset", "Type"])
        self.panel_tree.setColumnWidth(0, 300)
        self.panel_tree.itemSelectionChanged.connect(
            self.on_panel_selected
        )
        left_layout.addWidget(self.panel_tree)
        content.addWidget(left, 1)

        right = QGroupBox("Parameters to Import")
        right_layout = QVBoxLayout(right)

        buttons = QHBoxLayout()
        select_all = QPushButton("Select All")
        deselect_all = QPushButton("Deselect All")
        select_all.clicked.connect(lambda: self.set_all_checked(True))
        deselect_all.clicked.connect(lambda: self.set_all_checked(False))
        buttons.addWidget(select_all)
        buttons.addWidget(deselect_all)
        right_layout.addLayout(buttons)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.parameter_container = QWidget()
        self.parameter_layout = QVBoxLayout(
            self.parameter_container
        )
        self.parameter_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop
        )
        self.scroll.setWidget(self.parameter_container)
        right_layout.addWidget(self.scroll, 1)

        content.addWidget(right, 1)

        bottom = QHBoxLayout()
        bottom.addStretch()

        cancel = QPushButton("Cancel")
        import_button = QPushButton("Import Configuration")

        cancel.clicked.connect(self.reject)
        import_button.clicked.connect(self.accept_selection)

        bottom.addWidget(cancel)
        bottom.addWidget(import_button)
        root.addLayout(bottom)

    def load_projects(self):
        self.panel_tree.clear()

        if not self.projects_dir.exists():
            return

        for folder in sorted(
            [p for p in self.projects_dir.iterdir() if p.is_dir()],
            key=lambda p: p.name.lower()
        ):
            project_item = QTreeWidgetItem(
                [folder.name, "Project"]
            )
            project_item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                {"kind": "PROJECT", "folder": str(folder)}
            )
            self.panel_tree.addTopLevelItem(project_item)
            self._load_project_tree(
                project_item,
                folder
            )

        self.panel_tree.collapseAll()

    def _load_project_tree(self, project_item, folder):
        path = folder / "assets.json"
        if not path.exists():
            return

        try:
            data = json.loads(
                path.read_text(encoding="utf-8")
            )
        except Exception:
            return

        assets = (
            data if isinstance(data, list)
            else data.get("assets", [])
            if isinstance(data, dict)
            else []
        )

        by_id = {}

        for asset in assets:
            if not isinstance(asset, dict):
                continue

            node_id = asset.get("node_id") or asset.get("id")
            if not node_id:
                continue

            node_type = str(
                asset.get(
                    "node_type",
                    asset.get("type", "")
                ) or ""
            ).upper()

            item = QTreeWidgetItem([
                str(asset.get("name", "") or ""),
                node_type
            ])

            item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                {
                    "kind": "NODE",
                    "folder": str(folder),
                    "asset": asset,
                }
            )

            by_id[str(node_id)] = item

        for asset in assets:
            if not isinstance(asset, dict):
                continue

            node_id = asset.get("node_id") or asset.get("id")
            item = by_id.get(str(node_id))
            if item is None:
                continue

            parent_id = asset.get("parent_id")
            parent_item = by_id.get(str(parent_id)) if parent_id else None

            if parent_item is not None:
                parent_item.addChild(item)
            else:
                project_item.addChild(item)

    def on_panel_selected(self):
        selected = self.panel_tree.selectedItems()

        self.selected_panel = None
        self.source_components = []
        self._clear_parameters()

        if not selected:
            return

        data = selected[0].data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(data, dict):
            return

        asset = data.get("asset")
        if not isinstance(asset, dict):
            return

        node_type = str(
            asset.get(
                "node_type",
                asset.get("type", "")
            ) or ""
        ).upper()

        if node_type != "PANEL":
            return

        source_id = asset.get("node_id") or asset.get("id")

        if (
            self.target_panel_id is not None
            and str(source_id) == str(self.target_panel_id)
        ):
            QMessageBox.warning(
                self,
                "Invalid Source",
                "The target panel cannot be its own source."
            )
            return

        self.selected_panel = {
            "panel": asset,
            "folder": Path(data["folder"]),
        }

        self._load_source_components(
            Path(data["folder"]),
            source_id
        )
        self._build_parameters()

    def _load_source_components(self, folder, panel_id):
        try:
            manager = ComponentManager(folder)
            self.source_components = (
                manager.get_panel_components(panel_id)
                or []
            )
        except Exception:
            self.source_components = []

    def _clear_parameters(self):
        while self.parameter_layout.count():
            item = self.parameter_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.panel_checkboxes.clear()
        self.component_checkboxes.clear()
        self._component_checkbox_field.clear()

    def _build_parameters(self):
        self._clear_parameters()

        panel_group = QGroupBox("Panel Configuration")
        panel_layout = QVBoxLayout(panel_group)

        for field, label in self.PANEL_PARAMETERS.items():
            cb = QCheckBox(label)
            cb.setChecked(True)
            self.panel_checkboxes[field] = cb
            panel_layout.addWidget(cb)

        self.parameter_layout.addWidget(panel_group)

        for component in self.source_components:
            name = str(
                getattr(component, "name", "")
                or "Unnamed Component"
            )
            ctype = str(
                getattr(component, "component_type", "")
                or "COMPONENT"
            )

            group = QGroupBox(
                f"{name} ({ctype}) - ALL"
            )
            group_layout = QVBoxLayout(group)

            all_key = f"__ALL__::{id(component)}"
            all_cb = QCheckBox(
                f"{name} ({ctype}) - ALL"
            )
            all_cb.setChecked(True)

            group_layout.addWidget(all_cb)

            for field, label in self.COMPONENT_PARAMETERS.items():

                if field in self.UNIQUE_PARAMETERS:
                    continue

                cb = QCheckBox(
                    f"{name}: {label}"
                )
                cb.setChecked(True)

                key = (
                    f"{id(component)}::{field}"
                )

                self.component_checkboxes[key] = cb
                self._component_checkbox_field[key] = (
                    component,
                    field
                )

                group_layout.addWidget(cb)

                all_cb.toggled.connect(
                    lambda checked, c=cb: c.setChecked(checked)
                )

            self.parameter_layout.addWidget(group)

        self.parameter_layout.addStretch(1)

    def set_all_checked(self, checked):
        for cb in self.panel_checkboxes.values():
            cb.setChecked(checked)

        for cb in self.component_checkboxes.values():
            cb.setChecked(checked)

    def accept_selection(self):
        if self.selected_panel is None:
            QMessageBox.warning(
                self,
                "No Source Panel",
                "Please select a source panel."
            )
            return

        source_panel = self.selected_panel["panel"]

        panel_configuration = {}
        for field, cb in self.panel_checkboxes.items():
            if cb.isChecked():
                panel_configuration[field] = source_panel.get(
                    field,
                    ""
                )

        selected_component_fields = {}

        for key, cb in self.component_checkboxes.items():
            if not cb.isChecked():
                continue

            component, field = self._component_checkbox_field[key]
            selected_component_fields.setdefault(
                id(component),
                []
            ).append(field)

        component_configuration = []

        for component in self.source_components:
            fields = selected_component_fields.get(
                id(component),
                []
            )

            # Structural identity is retained only for matching.
            data = {
                "_source_component_type":
                    getattr(component, "component_type", ""),
                "_source_component_name":
                    getattr(component, "name", ""),
            }

            for field in fields:
                value = getattr(component, field, "")

                if isinstance(value, list):
                    value = list(value)

                elif isinstance(value, dict):
                    value = dict(value)

                data[field] = value

            component_configuration.append(data)

        self._configuration = {
            "source_panel_name":
                source_panel.get("name", ""),
            "source_panel_id":
                source_panel.get("node_id"),
            "source_project_folder":
                str(self.selected_panel["folder"]),
            "panel_configuration":
                panel_configuration,

            # Canonical key
            "component_configuration":
                component_configuration,

            # Compatibility key used by older code
            "components":
                component_configuration,
        }

        self.accept()

    def get_configuration(self):
        return self._configuration

    # Compatibility with the older AssetView workflow.
    @property
    def source_panel(self):
        if not self.selected_panel:
            return None
        return self.selected_panel["panel"]

    def get_selected_attributes(self):
        result = set(self.panel_checkboxes.keys())

        for key, cb in self.component_checkboxes.items():
            if cb.isChecked():
                result.add(
                    self._component_checkbox_field[key][1]
                )

        return result
