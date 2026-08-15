from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QInputDialog,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QDialog,
    QLineEdit,
    QDialogButtonBox,
)

from app.services.asset_manager import AssetManager
from app.services.component_manager import ComponentManager

from app.ui.panel_config_dialog import PanelConfigDialog
from app.ui.component_config_dialog import ComponentConfigDialog
from app.ui.protection_function_dialog import ProtectionFunctionDialog

from app.ui.relay_testing_dialog import RelayTestingDialog
from app.ui.ct_testing_dialog import CTTestingDialog
from app.ui.aux_relay_testing_dialog import AuxRelayTestingDialog

from app.ui.test_history_view import TestHistoryView
from app.ui.asset_link_dialog import AssetLinkDialog


class PanelAssetDialog(QDialog):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(parent)

        self.setWindowTitle(
            "Add Panel"
        )

        self.setModal(True)

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(
            "Example: Panel-1"
        )

        form.addRow(
            "Panel Name:",
            self.name_edit,
        )

        # self.asset_tag_edit = QLineEdit()
        # self.asset_tag_edit.setPlaceholderText(
        #     "Example: 101-P-001A"
        # )

        # form.addRow(
        #     "Asset Tag:",
        #     self.asset_tag_edit,
        # )

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self.name_edit.setFocus()

    def get_values(self):
        return self.name_edit.text().strip()


    def accept(self):

        name = self.name_edit.text().strip()
        #asset_tag = self.asset_tag_edit.text().strip()

        if not name:

            QMessageBox.warning(
                self,
                "Missing Panel Name",
                "Please enter a panel name.",
            )

            self.name_edit.setFocus()
            return

        # if not asset_tag:

        #     QMessageBox.warning(
        #         self,
        #         "Missing Asset Tag",
        #         "Please enter the panel asset tag.",
        #     )

        #     self.asset_tag_edit.setFocus()
        #    return

        super().accept()


class AssetView(QWidget):

    def __init__(
        self,
        project_folder: Path,
        project,
        test_service,
        parent=None,
    ):

        super().__init__(parent)

        # =================================================
        # REFERENCES
        # =================================================

        self.project_folder = project_folder
        self.project = project
        self.test_service = test_service

        self.testing_dialog = None
        self.test_history_view = None

        # Prevent accidental double execution of
        # create_panel().
        self._creating_panel = False

        # =================================================
        # MANAGERS
        # =================================================

        self.asset_manager = AssetManager(
            project_folder
        )

        self.component_manager = ComponentManager(
            project_folder
        )

        # =================================================
        # MAIN LAYOUT
        # =================================================

        layout = QVBoxLayout(self)

        # =================================================
        # ASSET TREE
        # =================================================

        self.tree = QTreeWidget()

        self.tree.setHeaderLabel(
            "Asset Hierarchy"
        )

        self.tree.setMinimumHeight(250)

        layout.addWidget(self.tree)

        # =================================================
        # COMPONENT SECTION
        # =================================================

        self.component_label = QLabel(
            "Test Components"
        )

        layout.addWidget(self.component_label)

        self.component_list = QListWidget()

        layout.addWidget(self.component_list)

        # =================================================
        # COMPONENT CONFIGURATION
        # =================================================

        self.configure_component = QPushButton(
            "Configure Component"
        )

        layout.addWidget(self.configure_component)

        # =================================================
        # PROTECTION FUNCTION CONFIGURATION
        # =================================================

        self.configure_protection = QPushButton(
            "Configure Protection Functions"
        )

        layout.addWidget(self.configure_protection)

        # =================================================
        # BOTTOM BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        self.add_substation = QPushButton(
            "+ Substation"
        )

        self.link_substation = QPushButton(
            "Link Existing Substation"
        )

        self.add_switchboard = QPushButton(
            "+ Switchboard"
        )

        self.link_switchboard = QPushButton(
            "Link Existing Switchboard"
        )

        self.add_panel = QPushButton(
            "+ Panel"
        )

        self.link_panel = QPushButton(
            "Link Existing Panel"
        )

        self.configure_panel = QPushButton(
            "Configure Panel"
        )

        self.open_testing = QPushButton(
            "Open Testing"
        )

        self.test_history_button = QPushButton(
            "Test History"
        )

        # Backward-compatible alias for code that may
        # still refer to self.test_history.
        self.test_history = self.test_history_button

        buttons.addWidget(self.add_substation)
        buttons.addWidget(self.link_substation)
        buttons.addWidget(self.add_switchboard)
        buttons.addWidget(self.link_switchboard)
        buttons.addWidget(self.add_panel)
        buttons.addWidget(self.link_panel)
        buttons.addWidget(self.configure_panel)
        buttons.addWidget(self.open_testing)
        buttons.addWidget(self.test_history_button)

        layout.addLayout(buttons)

        # =================================================
        # SIGNALS
        # =================================================

        self.tree.itemSelectionChanged.connect(
            self.display_selected_components
        )

        self.component_list.itemSelectionChanged.connect(
            self.on_component_selection_changed
        )

        self.configure_component.clicked.connect(
            self.configure_selected_component
        )

        self.configure_protection.clicked.connect(
            self.configure_selected_protection
        )

        self.configure_panel.clicked.connect(
            self.configure_selected_panel
        )

        self.add_substation.clicked.connect(
            self.create_substation
        )

        self.link_substation.clicked.connect(
            self.link_existing_substation
        )

        self.add_switchboard.clicked.connect(
            self.create_switchboard
        )

        self.link_switchboard.clicked.connect(
            self.link_existing_switchboard
        )

        self.add_panel.clicked.connect(
            self.create_panel
        )

        self.link_panel.clicked.connect(
            self.link_existing_panel
        )

        self.open_testing.clicked.connect(
            self.open_component_testing
        )

        self.test_history_button.clicked.connect(
            self.open_test_history
        )

        # =================================================
        # INITIAL STATE
        # =================================================

        self._update_button_states()
        self.refresh_tree()

    # =================================================
    # TREE
    # =================================================

    def refresh_tree(self):

        self.tree.clear()
        self.component_list.clear()

        roots = self.asset_manager.get_children(None)

        for node in roots:

            item = self._create_tree_item(node)

            self.tree.addTopLevelItem(item)

        self.tree.expandAll()

        self._update_button_states()

    def _create_tree_item(
        self,
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
            node.node_id
        )

        children = self.asset_manager.get_children(
            node.node_id
        )

        for child in children:

            child_item = self._create_tree_item(
                child
            )

            item.addChild(child_item)

        return item

    # =================================================
    # SELECTED NODE
    # =================================================

    def get_selected_node(self):

        item = self.tree.currentItem()

        if item is None:
            return None

        node_id = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if node_id is None:
            return None

        return self.asset_manager.get_node(
            node_id
        )

    def get_selected_panel(self):

        node = self.get_selected_node()

        if node is None:
            return None

        if str(
            getattr(
                node,
                "node_type",
                ""
            )
        ).upper() == "PANEL":

            return node

        return None

    # =================================================
    # COMPONENTS
    # =================================================

    def display_selected_components(self):

        self.component_list.clear()

        node = self.get_selected_node()

        if node is None:

            self._update_button_states()
            return

        if str(
            getattr(
                node,
                "node_type",
                ""
            )
        ).upper() != "PANEL":

            self._update_button_states()
            return

        components = (
            self.component_manager.get_panel_components(
                node.node_id
            )
        )

        for component in components:

            item = QListWidgetItem()

            item.setText(
                f"{component.name} | "
                f"{component.component_type}"
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                component.component_id
            )

            self.component_list.addItem(item)

        self._update_button_states()

    def on_component_selection_changed(self):

        self._update_button_states()

    def get_selected_component(self):

        item = self.component_list.currentItem()

        if item is None:
            return None

        component_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if component_id is None:
            return None

        # Current ComponentManager implementations expose
        # either get_component() or the components dict.
        if hasattr(
            self.component_manager,
            "get_component"
        ):

            return self.component_manager.get_component(
                component_id
            )

        return self.component_manager.components.get(
            component_id
        )

    def select_component_by_id(
        self,
        component_id,
    ):

        for index in range(
            self.component_list.count()
        ):

            item = self.component_list.item(index)

            stored_id = item.data(
                Qt.ItemDataRole.UserRole
            )

            if stored_id == component_id:

                self.component_list.setCurrentRow(index)
                return True

        return False

    # =================================================
    # BUTTON STATE
    # =================================================

    def _update_button_states(self):

        node = self.get_selected_node()
        component = self.get_selected_component()

        node_type = (
            str(
                getattr(
                    node,
                    "node_type",
                    ""
                )
            ).upper()
            if node is not None
            else ""
        )

        panel_selected = (
            node_type == "PANEL"
        )

        substation_selected = (
            node_type == "SUBSTATION"
        )

        switchboard_selected = (
            node_type == "SWITCHBOARD"
        )

        component_selected = (
            component is not None
        )

        relay_selected = (
            component_selected
            and str(
                getattr(
                    component,
                    "component_type",
                    ""
                )
            ).strip().upper()
            == "NUMERICAL_RELAY"
        )

        self.link_substation.setEnabled(
            True
        )

        self.add_switchboard.setEnabled(
            substation_selected
        )

        self.link_switchboard.setEnabled(
            substation_selected
        )

        self.add_panel.setEnabled(
            switchboard_selected
        )

        self.link_panel.setEnabled(
            switchboard_selected
        )

        self.configure_panel.setEnabled(
            panel_selected
        )

        self.configure_component.setEnabled(
            component_selected
        )

        self.configure_protection.setEnabled(
            relay_selected
        )

        self.open_testing.setEnabled(
            component_selected
        )

        self.test_history_button.setEnabled(
            panel_selected
        )

    # Compatibility name used by older versions.
    def update_button_state(self):

        self._update_button_states()

    # =================================================
    # INPUT
    # =================================================

    def ask_name(
        self,
        title,
    ):

        text, ok = QInputDialog.getText(
            self,
            title,
            "Name:"
        )

        if not ok:
            return ""

        return text.strip()

    # =================================================
    # CREATE SUBSTATION
    # =================================================

    def create_substation(self):

        name = self.ask_name(
            "Add Substation"
        )

        if not name:
            return

        try:

            self.asset_manager.create_node(
                name=name,
                node_type="SUBSTATION",
            )

            self.refresh_tree()

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Cannot Create Substation",
                str(error),
            )

    # =================================================
    # LINK EXISTING SUBSTATION
    # =================================================

    def link_existing_substation(self):

        try:

            available = (
                self.asset_manager
                .get_available_global_assets(
                    asset_type="SUBSTATION",
                    parent_node=None,
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Asset Database Error",
                str(error),
            )

            return

        if not available:

            QMessageBox.information(
                self,
                "No Substations Available",
                "There are no unlinked substations "
                "available in the global asset database.",
            )

            return

        dialog = AssetLinkDialog(
            available,
            asset_type="SUBSTATION",
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        selected = dialog.get_selected_asset()

        if not selected:
            return

        try:

            linked_node = (
                self.asset_manager.link_asset(
                    asset_id=selected["asset_id"],
                    parent_id=None,
                    name=selected.get("name"),
                )
            )

            self.refresh_tree()

            QMessageBox.information(
                self,
                "Substation Linked",
                f"'{linked_node.name}' "
                "has been linked to this project.",
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Cannot Link Substation",
                str(error),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Link Failed",
                str(error),
            )

    # =================================================
    # CREATE SWITCHBOARD
    # =================================================

    def create_switchboard(self):

        parent = self.get_selected_node()

        if parent is None:

            QMessageBox.warning(
                self,
                "Select Substation",
                "Please select a substation first.",
            )

            return

        if str(
            getattr(
                parent,
                "node_type",
                ""
            )
        ).upper() != "SUBSTATION":

            QMessageBox.warning(
                self,
                "Invalid Selection",
                "A switchboard must belong to a substation.",
            )

            return

        name = self.ask_name(
            "Add Switchboard"
        )

        if not name:
            return

        try:

            self.asset_manager.create_node(
                name=name,
                node_type="SWITCHBOARD",
                parent_id=parent.node_id,
            )

            self.refresh_tree()

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Cannot Create Switchboard",
                str(error),
            )

    # =================================================
    # AVAILABLE SWITCHBOARDS
    # =================================================

    def get_available_master_switchboards(self):

        parent = self.get_selected_node()

        if parent is None:
            return []

        if str(
            getattr(
                parent,
                "node_type",
                ""
            )
        ).upper() != "SUBSTATION":

            return []

        return (
            self.asset_manager
            .get_available_global_assets(
                asset_type="SWITCHBOARD",
                parent_node=parent,
            )
        )

    # =================================================
    # LINK EXISTING SWITCHBOARD
    # =================================================

    def link_existing_switchboard(self):

        parent = self.get_selected_node()

        if parent is None:

            QMessageBox.warning(
                self,
                "Select Substation",
                "Please select a substation first.",
            )

            return

        if str(
            getattr(
                parent,
                "node_type",
                ""
            )
        ).upper() != "SUBSTATION":

            QMessageBox.warning(
                self,
                "Invalid Selection",
                "An existing switchboard must be "
                "linked under a substation.",
            )

            return

        try:

            available = (
                self.get_available_master_switchboards()
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Asset Database Error",
                str(error),
            )

            return

        if not available:

            QMessageBox.information(
                self,
                "No Switchboards Available",
                "There are no unlinked switchboards "
                "available for this substation.",
            )

            return

        dialog = AssetLinkDialog(
            available,
            asset_type="SWITCHBOARD",
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        selected = dialog.get_selected_asset()

        if not selected:
            return

        try:

            linked_node = (
                self.asset_manager.link_asset(
                    asset_id=selected["asset_id"],
                    parent_id=parent.node_id,
                    name=selected.get("name"),
                )
            )

            self.refresh_tree()

            QMessageBox.information(
                self,
                "Switchboard Linked",
                f"Switchboard '{linked_node.name}' "
                "has been linked to this substation.",
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Cannot Link Switchboard",
                str(error),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Link Failed",
                str(error),
            )

    # =================================================
    # CREATE PANEL
    # =================================================

    def create_panel(self):

        if self._creating_panel:
            return

        self._creating_panel = True

        try:

            parent = self.get_selected_node()

            if parent is None:

                QMessageBox.warning(
                    self,
                    "Invalid Selection",
                    "Please select a switchboard first.",
                )

                return

            if str(
                getattr(
                    parent,
                    "node_type",
                    ""
                )
            ).upper() != "SWITCHBOARD":

                QMessageBox.warning(
                    self,
                    "Invalid Selection",
                    "A panel must belong to a switchboard.",
                )

                return

            dialog = PanelAssetDialog(
                parent=self
            )

            if (
                dialog.exec()
                != QDialog.DialogCode.Accepted
            ):

                return

            name = dialog.get_values()

            if not name:
                return

            try:

                self.asset_manager.create_node(
                    name=name,
                    node_type="PANEL",
                    parent_id=parent.node_id,
                    # asset_tag=asset_tag,
                )

            except ValueError as error:

                QMessageBox.warning(
                    self,
                    "Cannot Create Panel",
                    str(error),
                )

                return

            self.refresh_tree()

        finally:

            self._creating_panel = False

    # =================================================
    # AVAILABLE PANELS
    # =================================================

    def get_available_master_panels(self):

        parent = self.get_selected_node()

        if parent is None:
            return []

        if str(
            getattr(
                parent,
                "node_type",
                ""
            )
        ).upper() != "SWITCHBOARD":

            return []

        return (
            self.asset_manager
            .get_available_global_assets(
                asset_type="PANEL",
                parent_node=parent,
            )
        )

    # =================================================
    # LINK EXISTING PANEL + CONFIGURATION
    # =================================================

    def link_existing_panel(self):

        parent = self.get_selected_node()

        if parent is None:

            QMessageBox.warning(
                self,
                "Select Switchboard",
                "Please select a switchboard first.",
            )

            return

        if str(
            getattr(
                parent,
                "node_type",
                ""
            )
        ).upper() != "SWITCHBOARD":

            QMessageBox.warning(
                self,
                "Invalid Selection",
                "A panel must be linked under a switchboard.",
            )

            return

        try:

            available_panels = (
                self.get_available_master_panels()
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Asset Database Error",
                str(error),
            )

            return

        if not available_panels:

            QMessageBox.information(
                self,
                "No Panels Available",
                "There are no unlinked panels "
                "available for this switchboard.",
            )

            return

        dialog = AssetLinkDialog(
            available_panels,
            asset_type="PANEL",
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        selected = dialog.get_selected_asset()

        if not selected:
            return

        try:

            # ---------------------------------------------
            # CREATE PROJECT-LOCAL LINK
            # ---------------------------------------------

            linked_node = (
                self.asset_manager.link_asset(
                    asset_id=selected["asset_id"],
                    parent_id=parent.node_id,
                    name=selected.get("name"),
                )
            )

            # ---------------------------------------------
            # RESTORE PANEL CONFIGURATION
            # ---------------------------------------------

            metadata = (
                selected.get("metadata")
                or {}
            )

            panel_configuration = (
                metadata.get(
                    "panel_configuration",
                    {},
                )
            )

            if panel_configuration:

                try:

                    self.asset_manager.update_panel_configuration(
                        linked_node.node_id,
                        panel_configuration,
                    )

                except Exception:
                    # Do not fail the link if only the optional
                    # panel metadata is malformed.
                    pass

            # ---------------------------------------------
            # RESTORE COMPONENTS
            # ---------------------------------------------

            component_data = (
                metadata.get(
                    "components",
                    [],
                )
            )

            if component_data:

                if hasattr(
                    self.component_manager,
                    "clone_panel_components",
                ):

                    self.component_manager.clone_panel_components(
                        linked_node.node_id,
                        component_data,
                    )

                elif hasattr(
                    self.component_manager,
                    "restore_global_panel_components",
                ):

                    self.component_manager.restore_global_panel_components(
                        linked_node.node_id,
                        selected,
                    )

            self.refresh_tree()

            QMessageBox.information(
                self,
                "Panel Linked",
                f"Panel '{linked_node.name}' "
                "and its configuration have been "
                "imported successfully.",
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Cannot Link Panel",
                str(error),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Panel Import Failed",
                str(error),
            )

    # =================================================
    # PANEL CONFIGURATION
    # =================================================

    def configure_selected_panel(self):

        panel = self.get_selected_panel()

        if panel is None:

            QMessageBox.warning(
                self,
                "No Panel Selected",
                "Please select a panel first.",
            )

            return

        dialog = PanelConfigDialog(
            node=panel,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        configuration = dialog.get_configuration()

        try:

            self.asset_manager.update_panel_configuration(
                panel.node_id,
                configuration,
            )

            self.component_manager.generate_panel_components(
                panel_id=panel.node_id,
                ct_count=int(
                    configuration.get(
                        "ct_count",
                        0,
                    ) or 0
                ),
                relay_count=int(
                    configuration.get(
                        "relay_count",
                        0,
                    ) or 0
                ),
                aux_count=int(
                    configuration.get(
                        "aux_count",
                        0,
                    ) or 0
                ),
            )

            self.display_selected_components()

            QMessageBox.information(
                self,
                "Panel Saved",
                "Panel configuration and test components "
                "saved successfully.",
            )

        except (
            ValueError,
            TypeError,
        ) as error:

            QMessageBox.warning(
                self,
                "Cannot Save",
                str(error),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error),
            )

    # =================================================
    # COMPONENT CONFIGURATION
    # =================================================

    def configure_selected_component(self):

        component = self.get_selected_component()

        if component is None:

            QMessageBox.warning(
                self,
                "No Component Selected",
                "Please select a component first.",
            )

            return

        dialog = ComponentConfigDialog(
            component,
            self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        configuration = dialog.get_configuration()

        try:

            self.component_manager.update_component_configuration(
                component.component_id,
                configuration,
            )

            self.display_selected_components()

            self.select_component_by_id(
                component.component_id
            )

            QMessageBox.information(
                self,
                "Saved",
                f"{component.name} configuration saved.",
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Cannot Save",
                str(error),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error),
            )

    # =================================================
    # PROTECTION FUNCTION CONFIGURATION
    # =================================================

    def configure_selected_protection(self):

        component = self.get_selected_component()

        if component is None:

            QMessageBox.warning(
                self,
                "No Component Selected",
                "Please select a numerical relay first.",
            )

            return

        component_type = str(
            getattr(
                component,
                "component_type",
                "",
            )
        ).upper()

        if component_type != "NUMERICAL_RELAY":

            QMessageBox.warning(
                self,
                "Invalid Component",
                "Protection functions can only be configured "
                "for a numerical relay.",
            )

            return

        dialog = ProtectionFunctionDialog(
            component,
            self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        try:

            self.component_manager.update_protection_functions(
                component.component_id,
                getattr(
                    component,
                    "protection_functions",
                    [],
                ),
            )

            self.display_selected_components()

            self.select_component_by_id(
                component.component_id
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Cannot Save",
                str(error),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error),
            )

    # =================================================
    # SAVE COMPONENT CONFIGURATION
    # =================================================

    def save_component_configuration(
        self,
        component,
    ):

        if component is None:
            return False

        try:

            self.component_manager.update_component_configuration(
                component.component_id,
                {
                    "manufacturer": getattr(
                        component,
                        "manufacturer",
                        "",
                    ),
                    "model": getattr(
                        component,
                        "model",
                        "",
                    ),
                    "serial_number": getattr(
                        component,
                        "serial_number",
                        "",
                    ),
                    "ct_ratio": getattr(
                        component,
                        "ct_ratio",
                        "",
                    ),
                    "ct_class": getattr(
                        component,
                        "ct_class",
                        "",
                    ),
                    "burden": getattr(
                        component,
                        "burden",
                        "",
                    ),
                    "core": getattr(
                        component,
                        "core",
                        "",
                    ),
                    "vt_ratio": getattr(
                        component,
                        "vt_ratio",
                        "",
                    ),
                    "firmware": getattr(
                        component,
                        "firmware",
                        "",
                    ),
                    "coil_voltage": getattr(
                        component,
                        "coil_voltage",
                        "",
                    ),
                    "contact_configuration": getattr(
                        component,
                        "contact_configuration",
                        "",
                    ),
                    "protection_functions": getattr(
                        component,
                        "protection_functions",
                        [],
                    ),
                },
            )

            return True

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                f"Unable to save component configuration:\n\n"
                f"{error}",
            )

            return False

    # =================================================
    # OPEN TESTING
    # =================================================

    def open_component_testing(self):

        self.open_testing_view()

    def open_testing_view(self):

        component = self.get_selected_component()

        if component is None:

            QMessageBox.warning(
                self,
                "No Component Selected",
                "Please select a component first.",
            )

            return

        # Prevent duplicate testing windows.

        if self.testing_dialog is not None:

            try:

                if self.testing_dialog.isVisible():

                    self.testing_dialog.raise_()
                    self.testing_dialog.activateWindow()

                    return

            except RuntimeError:

                self.testing_dialog = None

        project_id = getattr(
            self.project,
            "project_id",
            None,
        )

        if not project_id:

            QMessageBox.warning(
                self,
                "Project Error",
                "Unable to determine project ID.",
            )

            return

        panel = self.get_selected_panel()

        panel_id = None

        if panel is not None:

            panel_id = getattr(
                panel,
                "node_id",
                None,
            )

        if not panel_id:

            panel_id = getattr(
                component,
                "panel_id",
                None,
            )

        if not panel_id:

            QMessageBox.warning(
                self,
                "Panel Not Found",
                "Unable to determine the panel associated "
                "with this component.",
            )

            return

        component_type = str(
            getattr(
                component,
                "component_type",
                "",
            )
        ).strip().upper()

        if component_type == "NUMERICAL_RELAY":

            self.testing_dialog = RelayTestingDialog(
                project_id=project_id,
                panel_id=panel_id,
                relay_id=component.component_id,
                component=component,
                test_service=self.test_service,
                parent=self,
            )

        elif component_type in (
            "CT",
            "CURRENT TRANSFORMER",
        ):

            self.testing_dialog = CTTestingDialog(
                project_id=project_id,
                panel_id=panel_id,
                component=component,
                test_service=self.test_service,
                parent=self,
            )

        elif component_type in (
            "AUXILIARY_RELAY",
            "AUX RELAY",
        ):

            self.testing_dialog = AuxRelayTestingDialog(
                project_id=project_id,
                panel_id=panel_id,
                component=component,
                test_service=self.test_service,
                parent=self,
            )

        else:

            QMessageBox.information(
                self,
                "Testing Not Available",
                (
                    "Testing template is not yet available "
                    "for component type:\n\n"
                    f"{component.component_type}"
                ),
            )

            return

        self.testing_dialog.setAttribute(
            Qt.WidgetAttribute.WA_DeleteOnClose
        )

        self.testing_dialog.finished.connect(
            self.on_testing_dialog_closed
        )

        self.testing_dialog.show()
        self.testing_dialog.raise_()
        self.testing_dialog.activateWindow()

    # =================================================
    # TESTING DIALOG LIFETIME
    # =================================================

    def close_testing_dialog(self):

        if self.testing_dialog is None:
            return

        try:
            self.testing_dialog.close()
        except RuntimeError:
            pass

        self.testing_dialog = None

    def on_testing_dialog_closed(
        self,
        *args,
    ):

        self.testing_dialog = None

    # =================================================
    # TEST HISTORY
    # =================================================

    def open_test_history(self):

        panel = self.get_selected_panel()

        if panel is None:

            QMessageBox.warning(
                self,
                "No Panel Selected",
                "Please select a panel first.",
            )

            return

        project_id = getattr(
            self.project,
            "project_id",
            None,
        )

        if project_id is None:

            QMessageBox.warning(
                self,
                "Project Error",
                "Unable to determine project ID.",
            )

            return

        panel_id = getattr(
            panel,
            "node_id",
            None,
        )

        if panel_id is None:

            QMessageBox.warning(
                self,
                "Panel Error",
                "Unable to determine panel ID.",
            )

            return

        self.test_history_view = TestHistoryView(
            test_service=self.test_service,
            project_id=project_id,
            panel_id=panel_id,
            parent=self,
        )

        self.test_history_view.exec()

    # =================================================
    # REFRESH
    # =================================================

    def refresh_component_view(self):

        self.display_selected_components()
