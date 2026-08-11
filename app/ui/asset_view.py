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

        # -------------------------------------------------
        # PANEL NAME
        # -------------------------------------------------

        self.name_edit = QLineEdit()

        self.name_edit.setPlaceholderText(
            "Example: Panel-1"
        )

        form.addRow(
            "Panel Name:",
            self.name_edit,
        )

        # -------------------------------------------------
        # ASSET TAG
        # -------------------------------------------------

        self.asset_tag_edit = QLineEdit()

        self.asset_tag_edit.setPlaceholderText(
            "Example: 101-P-001A"
        )

        form.addRow(
            "Asset Tag:",
            self.asset_tag_edit,
        )

        layout.addLayout(
            form
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self.accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(
            buttons
        )

        self.name_edit.setFocus()

    # =====================================================
    # GET VALUES
    # =====================================================

    def get_values(self):

        return (
            self.name_edit.text().strip(),
            self.asset_tag_edit.text().strip(),
        )

    # =====================================================
    # VALIDATE
    # =====================================================

    def accept(self):

        name = self.name_edit.text().strip()

        asset_tag = (
            self.asset_tag_edit.text().strip()
        )

        if not name:

            QMessageBox.warning(
                self,
                "Missing Panel Name",
                "Please enter a panel name.",
            )

            self.name_edit.setFocus()

            return

        if not asset_tag:

            QMessageBox.warning(
                self,
                "Missing Asset Tag",
                "Please enter the panel asset tag.",
            )

            self.asset_tag_edit.setFocus()

            return

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

        layout = QVBoxLayout(
            self
        )

        # =================================================
        # ASSET TREE
        # =================================================

        self.tree = QTreeWidget()

        self.tree.setHeaderLabel(
            "Asset Hierarchy"
        )

        self.tree.setMinimumHeight(
            250
        )

        layout.addWidget(
            self.tree
        )

        # =================================================
        # COMPONENT SECTION
        # =================================================

        self.component_label = QLabel(
            "Test Components"
        )

        layout.addWidget(
            self.component_label
        )

        self.component_list = QListWidget()

        layout.addWidget(
            self.component_list
        )

        # =================================================
        # COMPONENT CONFIGURATION
        # =================================================

        self.configure_component = QPushButton(
            "Configure Component"
        )

        layout.addWidget(
            self.configure_component
        )

        # =================================================
        # PROTECTION FUNCTION CONFIGURATION
        # =================================================

        self.configure_protection = QPushButton(
            "Configure Protection Functions"
        )

        layout.addWidget(
            self.configure_protection
        )

        # =================================================
        # BOTTOM BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        self.add_substation = QPushButton(
            "+ Substation"
        )

        self.add_switchboard = QPushButton(
            "+ Switchboard"
        )

        self.add_panel = QPushButton(
            "+ Panel"
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

        buttons.addWidget(
            self.add_substation
        )

        buttons.addWidget(
            self.add_switchboard
        )

        buttons.addWidget(
            self.add_panel
        )

        buttons.addWidget(
            self.configure_panel
        )

        buttons.addWidget(
            self.open_testing
        )

        buttons.addWidget(
            self.test_history_button
        )

        layout.addLayout(
            buttons
        )

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

        self.add_switchboard.clicked.connect(
            self.create_switchboard
        )

        self.add_panel.clicked.connect(
            self.create_panel
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

    # =====================================================
    # TREE
    # =====================================================

    def refresh_tree(self):

        self.tree.clear()

        self.component_list.clear()

        roots = self.asset_manager.get_children(
            None
        )

        for node in roots:

            item = self._create_tree_item(
                node
            )

            self.tree.addTopLevelItem(
                item
            )

        self.tree.expandAll()

        self._update_button_states()

    # =====================================================
    # CREATE TREE ITEM
    # =====================================================

    def _create_tree_item(
        self,
        node,
    ):

        item = QTreeWidgetItem()

        item.setText(
            0,
            node.name
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

            item.addChild(
                child_item
            )

        return item

    # =====================================================
    # SELECTED NODE
    # =====================================================

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

    # =====================================================
    # SELECTED PANEL
    # =====================================================

    def get_selected_panel(self):

        node = self.get_selected_node()

        if node is None:
            return None

        node_type = str(
            getattr(
                node,
                "node_type",
                ""
            )
        ).upper()

        if node_type == "PANEL":
            return node

        return None

    # =====================================================
    # SELECTED COMPONENT
    # =====================================================

    def get_selected_component(self):

        item = self.component_list.currentItem()

        if item is None:
            return None

        component_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if component_id is None:
            return None

        return self.component_manager.components.get(
            component_id
        )

    # =====================================================
    # SELECT COMPONENT BY ID
    # =====================================================

    def select_component_by_id(
        self,
        component_id,
    ):

        for index in range(
            self.component_list.count()
        ):

            item = self.component_list.item(
                index
            )

            stored_id = item.data(
                Qt.ItemDataRole.UserRole
            )

            if stored_id == component_id:

                self.component_list.setCurrentRow(
                    index
                )

                return True

        return False

    # =====================================================
    # INPUT DIALOG
    # =====================================================

    def ask_name(
        self,
        title,
    ):

        text, ok = QInputDialog.getText(
            self,
            title,
            title,
        )

        if not ok:
            return ""

        return text.strip()

    # =====================================================
    # CREATE SUBSTATION
    # =====================================================

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
                "Cannot Create",
                str(error),
            )

    # =====================================================
    # CREATE SWITCHBOARD
    # =====================================================

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
                "",
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
                "Cannot Create",
                str(error),
            )

    # =====================================================
    # CREATE PANEL
    # =====================================================

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
                    "",
                )
            ).upper() != "SWITCHBOARD":

                QMessageBox.warning(
                    self,
                    "Invalid Selection",
                    "A panel must belong to a switchboard.",
                )

                return

            # -------------------------------------------------
            # ONE DIALOG FOR BOTH VALUES
            # -------------------------------------------------

            dialog = PanelAssetDialog(
                parent=self
            )

            if (
                dialog.exec()
                != QDialog.DialogCode.Accepted
            ):
                return

            name, asset_tag = (
                dialog.get_values()
            )

            if not name or not asset_tag:
                return

            # -------------------------------------------------
            # CREATE PANEL
            # -------------------------------------------------

            try:

                self.asset_manager.create_node(
                    name=name,
                    node_type="PANEL",
                    parent_id=parent.node_id,
                    asset_tag=asset_tag,
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

    # =====================================================
    # DISPLAY COMPONENTS
    # =====================================================

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
                "",
            )
        ).upper() != "PANEL":

            self._update_button_states()

            return

        components = (
            self.component_manager
            .get_panel_components(
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
                component.component_id,
            )

            self.component_list.addItem(
                item
            )

        self._update_button_states()

    # =====================================================
    # COMPONENT SELECTION
    # =====================================================

    def on_component_selection_changed(self):

        self._update_button_states()

    # =====================================================
    # BUTTON STATE
    # =====================================================

    def _update_button_states(self):

        node = self.get_selected_node()

        component = self.get_selected_component()

        panel_selected = (
            node is not None
            and str(
                getattr(
                    node,
                    "node_type",
                    "",
                )
            ).upper() == "PANEL"
        )

        relay_selected = (
            component is not None
            and str(
                getattr(
                    component,
                    "component_type",
                    "",
                )
            ).upper() == "NUMERICAL_RELAY"
        )

        component_selected = (
            component is not None
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

    # =====================================================
    # PANEL CONFIGURATION
    # =====================================================

    def configure_selected_panel(self):

        node = self.get_selected_panel()

        if node is None:

            QMessageBox.warning(
                self,
                "No Panel Selected",
                "Please select a panel first.",
            )

            return

        dialog = PanelConfigDialog(
            node=node,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        configuration = (
            dialog.get_configuration()
        )

        try:

            self.asset_manager.update_panel_configuration(
                node.node_id,
                configuration,
            )

            self.component_manager.generate_panel_components(
                panel_id=node.node_id,
                ct_count=int(
                    configuration.get(
                        "ct_count",
                        0,
                    )
                ),
                relay_count=int(
                    configuration.get(
                        "relay_count",
                        0,
                    )
                ),
                aux_count=int(
                    configuration.get(
                        "aux_count",
                        0,
                    )
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

    # =====================================================
    # COMPONENT CONFIGURATION
    # =====================================================

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

        configuration = (
            dialog.get_configuration()
        )

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

    # =====================================================
    # PROTECTION FUNCTION CONFIGURATION
    # =====================================================

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

    # =====================================================
    # SAVE COMPONENT CONFIGURATION
    # =====================================================

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

    # =====================================================
    # OPEN COMPONENT TESTING
    # =====================================================

    def open_component_testing(self):

        component = self.get_selected_component()

        if component is None:

            QMessageBox.warning(
                self,
                "No Component Selected",
                "Please select a component first.",
            )

            return

        component_type = str(
            getattr(
                component,
                "component_type",
                "",
            )
        ).strip().upper()

        # -------------------------------------------------
        # Prevent duplicate window
        # -------------------------------------------------

        if self.testing_dialog is not None:

            try:

                if self.testing_dialog.isVisible():

                    self.testing_dialog.raise_()

                    self.testing_dialog.activateWindow()

                    return

            except RuntimeError:

                self.testing_dialog = None

        # -------------------------------------------------
        # Determine panel
        # -------------------------------------------------

        panel = self.get_selected_panel()

        panel_id = None

        if panel is not None:

            panel_id = getattr(
                panel,
                "node_id",
                None,
            )

        if panel_id is None:

            panel_id = getattr(
                component,
                "panel_id",
                None,
            )

        if panel_id is None:

            QMessageBox.warning(
                self,
                "Panel Not Found",
                "Unable to determine the panel associated "
                "with this component.",
            )

            return

        # -------------------------------------------------
        # Project ID
        # -------------------------------------------------

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

        # =================================================
        # NUMERICAL RELAY
        # =================================================

        if component_type == "NUMERICAL_RELAY":

            self.testing_dialog = RelayTestingDialog(
                project_id=project_id,
                panel_id=panel_id,
                relay_id=component.component_id,
                component=component,
                test_service=self.test_service,
                parent=self,
            )

        # =================================================
        # CT
        # =================================================

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

        # =================================================
        # AUXILIARY RELAY
        # =================================================

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

        # =================================================
        # UNKNOWN
        # =================================================

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

        # =================================================
        # DIALOG LIFETIME
        # =================================================

        self.testing_dialog.setAttribute(
            Qt.WidgetAttribute.WA_DeleteOnClose
        )

        self.testing_dialog.finished.connect(
            self.on_testing_dialog_closed
        )

        self.testing_dialog.show()

        self.testing_dialog.raise_()

        self.testing_dialog.activateWindow()

    # =====================================================
    # CLOSE TESTING DIALOG
    # =====================================================

    def close_testing_dialog(self):

        if self.testing_dialog is None:
            return

        try:

            self.testing_dialog.close()

        except RuntimeError:

            pass

        self.testing_dialog = None

    # =====================================================
    # TESTING DIALOG CLOSED
    # =====================================================

    def on_testing_dialog_closed(self):

        self.testing_dialog = None

    # =====================================================
    # TEST HISTORY
    # =====================================================

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

    # =====================================================
    # REFRESH COMPONENT VIEW
    # =====================================================

    def refresh_component_view(self):

        self.display_selected_components()