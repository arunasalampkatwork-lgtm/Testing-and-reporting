from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtCore import (
    QDate
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QFrame,
    QSizePolicy,
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
    QDateEdit,
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
from app.ui.asset_edit_dialog import AssetEditDialog
from app.services.panel_report_service import (
    PanelReportService
)
from app.ui.meter_testing_dialog import (
    MeterTestingDialog
)



class PanelAssetDialog(QDialog):

    def __init__(
        self,
        parent=None,
    ):

        super().__init__(
            parent
        )

        self.setWindowTitle(
            "Add Panel"
        )

        self.setModal(
            True
        )

        self.resize(
            450,
            140
        )

        layout = QVBoxLayout(
            self
        )

        form = QFormLayout()

        self.name_edit = QLineEdit()

        self.name_edit.setPlaceholderText(
            "Example: P-03"
        )

        form.addRow(
            "Panel Name:",
            self.name_edit
        )

        layout.addLayout(
            form
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            |
            QDialogButtonBox.StandardButton.Cancel
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

    def get_values(self):

        return (
            self.name_edit
            .text()
            .strip()
        )

    def accept(self):

        name = (
            self.name_edit
            .text()
            .strip()
        )

        if not name:

            QMessageBox.warning(
                self,
                "Missing Panel Name",
                "Please enter a panel name."
            )

            self.name_edit.setFocus()

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
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # =================================================
        # WORKSPACE
        #
        # Left  : asset hierarchy + components
        # Right : context/action panel
        # =================================================

        workspace = QHBoxLayout()
        workspace.setSpacing(12)

        # =================================================
        # LEFT WORKSPACE
        # =================================================

        left_layout = QVBoxLayout()
        left_layout.setSpacing(8)

        # -------------------------------------------------
        # ASSET TREE HEADER
        # -------------------------------------------------

        asset_header = QLabel(
            "Asset Hierarchy"
        )

        asset_header.setObjectName(
            "SectionHeader"
        )

        left_layout.addWidget(
            asset_header
        )

        # -------------------------------------------------
        # ASSET TREE
        # -------------------------------------------------

        self.tree = QTreeWidget()

        self.tree.setHeaderLabel(
            "Project Assets"
        )

        self.tree.setMinimumHeight(280)

        self.tree.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.tree.setIndentation(24)
        self.tree.setAnimated(True)
        self.tree.setUniformRowHeights(True)

        left_layout.addWidget(
            self.tree,
            5,
        )

        # -------------------------------------------------
        # COMPONENT HEADER
        # -------------------------------------------------

        self.component_label = QLabel(
            "Test Components"
        )

        self.component_label.setObjectName(
            "SectionHeader"
        )

        left_layout.addWidget(
            self.component_label
        )

        # -------------------------------------------------
        # COMPONENT LIST
        # -------------------------------------------------

        self.component_list = QListWidget()

        self.component_list.setMinimumHeight(220)

        self.component_list.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.component_list.setSpacing(2)
        self.component_list.setUniformItemSizes(True)

        left_layout.addWidget(
            self.component_list,
            4,
        )

        # =================================================
        # RIGHT ACTION PANEL
        # =================================================

        action_panel = QFrame()

        action_panel.setObjectName(
            "ActionPanel"
        )

        action_panel.setFixedWidth(
            245
        )

        action_layout = QVBoxLayout(
            action_panel
        )

        action_layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        action_layout.setSpacing(7)

        # -------------------------------------------------
        # ACTION HEADER
        # -------------------------------------------------

        action_title = QLabel(
            "Actions"
        )

        action_title.setObjectName(
            "ActionTitle"
        )

        action_layout.addWidget(
            action_title
        )

        action_subtitle = QLabel(
            "Select an asset or component, then choose an action."
        )

        action_subtitle.setObjectName(
            "ActionSubtitle"
        )

        action_subtitle.setWordWrap(True)

        action_layout.addWidget(
            action_subtitle
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        self.add_substation = QPushButton(
            "+  Substation"
        )

        self.link_substation = QPushButton(
            "Link Existing Substation"
        )

        self.add_switchboard = QPushButton(
            "+  Switchboard"
        )

        self.link_switchboard = QPushButton(
            "Link Existing Switchboard"
        )

        self.add_panel = QPushButton(
            "+  Panel"
        )

        self.link_panel = QPushButton(
            "Link Existing Panel"
        )

        self.configure_component = QPushButton(
            "Edit Component"
        )

        self.configure_protection = QPushButton(
            "Edit Protection Functions"
        )

        self.configure_panel = QPushButton(
            "Edit Panel Configuration"
        )

        self.open_testing = QPushButton(
            "Open Testing"
        )

        self.test_history_button = QPushButton(
            "Test History"
        )

        self.panel_report_button = QPushButton(
            "Panel Report"
        )

        self.edit_asset_button = QPushButton(
            "Edit Asset"
        )

        # Backward-compatible alias for code that may
        # still refer to self.test_history.
        self.test_history = self.test_history_button

        # -------------------------------------------------
        # GROUP LABEL HELPER
        # -------------------------------------------------

        def add_action_group(
            title,
            buttons,
        ):

            group_label = QLabel(
                title.upper()
            )

            group_label.setObjectName(
                "ActionGroup"
            )

            action_layout.addWidget(
                group_label
            )

            for button in buttons:

                button.setMinimumHeight(
                    38
                )

                button.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Fixed,
                )

                action_layout.addWidget(
                    button
                )

        # -------------------------------------------------
        # ASSET STRUCTURE
        # -------------------------------------------------

        add_action_group(
            "Asset Structure",
            [
                self.add_substation,
                self.link_substation,
                self.add_switchboard,
                self.link_switchboard,
                self.add_panel,
                self.link_panel,
            ],
        )

        # -------------------------------------------------
        # EDITING
        # -------------------------------------------------

        add_action_group(
            "Editing",
            [
                self.edit_asset_button,
                self.configure_panel,
                self.configure_component,
                self.configure_protection,
            ],
        )

        # -------------------------------------------------
        # TESTING & REPORTING
        # -------------------------------------------------

        add_action_group(
            "Testing & Reporting",
            [
                self.open_testing,
                self.test_history_button,
                self.panel_report_button,
            ],
        )

        action_layout.addStretch()

        # =================================================
        # ADD WORKSPACE
        # =================================================

        workspace.addLayout(
            left_layout,
            1,
        )

        workspace.addWidget(
            action_panel
        )

        layout.addLayout(
            workspace,
            1,
        )

        # =================================================
        # LOCAL UI STYLING
        # =================================================

        self.setStyleSheet(
            """
            /* ------------------------------------------
               SECTION HEADERS
               ------------------------------------------ */

            QLabel#SectionHeader {
                font-size: 15px;
                font-weight: 600;
                padding: 8px 11px;
                color: #f2f2f2;
                background-color: #353535;
                border: 1px solid #454545;
                border-radius: 6px;
            }

            /* ------------------------------------------
               ACTION PANEL
               ------------------------------------------ */

            QFrame#ActionPanel {
                background-color: #242424;
                border: 1px solid #414141;
                border-radius: 8px;
            }

            QLabel#ActionTitle {
                font-size: 19px;
                font-weight: 700;
                padding: 2px 2px 0px 2px;
                color: #f4f4f4;
                background: transparent;
                border: none;
            }

            QLabel#ActionSubtitle {
                font-size: 11px;
                color: #999999;
                padding: 0px 2px 6px 2px;
                background: transparent;
                border: none;
            }

            QLabel#ActionGroup {
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
                color: #a9a9a9;
                padding: 7px 3px 2px 3px;
                background: transparent;
                border: none;
            }

            /* ------------------------------------------
               ACTION BUTTONS
               ------------------------------------------ */

            QPushButton {
                min-height: 36px;
                padding: 6px 11px;
                text-align: left;
                border-radius: 6px;
                border: 1px solid #444444;
                background-color: #303030;
                color: #eeeeee;
            }

            QPushButton:hover {
                background-color: #383838;
                border: 1px solid #666666;
            }

            QPushButton:pressed {
                background-color: #222222;
                border: 1px solid #777777;
            }

            QPushButton:disabled {
                color: #666666;
                background-color: #272727;
                border: 1px solid #333333;
            }

            /* Primary workflow */
            QPushButton#OpenTestingButton {
                min-height: 44px;
                font-size: 13px;
                font-weight: 700;
                border: 1px solid #e58a18;
                background-color: #343434;
            }

            QPushButton#OpenTestingButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #f09a27;
            }

            QPushButton#OpenTestingButton:pressed {
                background-color: #292929;
            }

            /* Report action */
            QPushButton#PanelReportButton {
                min-height: 42px;
                font-weight: 600;
            }

            /* ------------------------------------------
               TREE
               ------------------------------------------ */

            QTreeWidget {
                background-color: #292929;
                alternate-background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 6px;
                outline: none;
                padding: 4px;
            }

            QTreeWidget::item {
                height: 30px;
                padding: 3px 6px;
                border-radius: 4px;
            }

            QTreeWidget::item:hover {
                background-color: #353535;
            }

            QTreeWidget::item:selected {
                background-color: #3b3b3b;
                border-left: 2px solid #e58a18;
            }

            QHeaderView::section {
                background-color: #333333;
                color: #dddddd;
                padding: 7px;
                border: none;
                border-bottom: 1px solid #444444;
                font-weight: 600;
            }

            /* ------------------------------------------
               COMPONENT LIST
               ------------------------------------------ */

            QListWidget {
                background-color: #292929;
                alternate-background-color: #2d2d2d;
                border: 1px solid #3e3e3e;
                border-radius: 6px;
                outline: none;
                padding: 4px;
            }

            QListWidget::item {
                min-height: 34px;
                padding: 4px 9px;
                border-radius: 5px;
            }

            QListWidget::item:hover {
                background-color: #353535;
            }

            QListWidget::item:selected {
                background-color: #3b3b3b;
                border-left: 2px solid #e58a18;
            }
            """
        )

        # Make the primary actions visually distinct.
        self.open_testing.setObjectName(
            "OpenTestingButton"
        )

        self.panel_report_button.setObjectName(
            "PanelReportButton"
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
        self.edit_asset_button.clicked.connect(
            self.edit_selected_asset
        )
        self.panel_report_button.clicked.connect(
            self.generate_panel_report
        )

        # =================================================
        # INITIAL STATE
        # =================================================

        self._update_button_states()
        self._tree_initialized = False
        self.refresh_tree()

    # =================================================
    # TREE
    # =================================================


    def refresh_tree(self):

        expanded_node_ids = set()

        def collect_expanded(item):

            node_id = item.data(
                0,
                Qt.ItemDataRole.UserRole
            )

            if node_id and item.isExpanded():
                expanded_node_ids.add(node_id)

            for index in range(item.childCount()):

                collect_expanded(
                    item.child(index)
                )

        for index in range(
            self.tree.topLevelItemCount()
        ):

            collect_expanded(
                self.tree.topLevelItem(index)
            )

        # =================================================
        # REMEMBER CURRENT SELECTION
        # =================================================

        selected_node_id = None

        current_item = self.tree.currentItem()

        if current_item is not None:

            selected_node_id = current_item.data(
                0,
                Qt.ItemDataRole.UserRole
            )

        # =================================================
        # REBUILD TREE
        # =================================================

        self.tree.blockSignals(True)

        try:

            self.tree.clear()

            self.component_list.clear()

            roots = self.asset_manager.get_children(None)

            for node in roots:

                item = self._create_tree_item(
                    node
                )

                self.tree.addTopLevelItem(
                    item
                )

            # =================================================
            # INITIAL LOAD
            #
            # First load is collapsed.
            # Later refreshes preserve the user's state.
            # =================================================

            if not self._tree_initialized:

                self.tree.collapseAll()

            else:

                def restore_expansion(item):

                    node_id = item.data(
                        0,
                        Qt.ItemDataRole.UserRole
                    )

                    if node_id in expanded_node_ids:

                        item.setExpanded(
                            True
                        )

                    for index in range(
                        item.childCount()
                    ):

                        restore_expansion(
                            item.child(index)
                        )

                for index in range(
                    self.tree.topLevelItemCount()
                ):

                    restore_expansion(
                        self.tree.topLevelItem(index)
                    )

        finally:

            self.tree.blockSignals(False)

        # =================================================
        # RESTORE SELECTION
        # =================================================

        if selected_node_id:

            self.select_tree_node(
                selected_node_id
            )

        # =================================================
        # UPDATE STATE
        # =================================================

        self._tree_initialized = True

        self._update_button_states()

        self.display_selected_components()
    # =================================================
    # SELECT TREE NODE
    # =================================================

    def select_tree_node(
        self,
        node_id,
    ):

        def find_item(
            parent_item,
        ):

            for index in range(
                parent_item.childCount()
            ):

                child = (
                    parent_item.child(index)
                )

                child_id = child.data(
                    0,
                    Qt.ItemDataRole.UserRole,
                )

                if child_id == node_id:

                    return child

                result = find_item(
                    child
                )

                if result is not None:

                    return result

            return None

        for index in range(
            self.tree.topLevelItemCount()
        ):

            item = (
                self.tree.topLevelItem(
                    index
                )
            )

            item_id = item.data(
                0,
                Qt.ItemDataRole.UserRole,
            )

            if item_id == node_id:

                self.tree.setCurrentItem(
                    item
                )

                return True

            result = find_item(
                item
            )

            if result is not None:

                self.tree.setCurrentItem(
                    result
                )

                return True

        return False

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
        self.panel_report_button.setEnabled(
            panel_selected
        )
        physical_asset_selected = (
            node_type in (
                "SUBSTATION",
                "SWITCHBOARD",
                "PANEL",
            )
        )

        self.edit_asset_button.setEnabled(
            physical_asset_selected
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
                    "Please select a switchboard first."
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
                    "A panel must belong to a switchboard."
                )

                return

            parent_id = parent.node_id

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

            # =================================================
            # AUTO-GENERATE PHYSICAL ASSET TAG
            #
            # Hierarchy:
            #     REF-III SS-2
            #         HV-203A
            #
            # Panel:
            #     P-03
            #
            # Result:
            #     REF-III-SS-2-HV-203A-P-03
            # =================================================

            hierarchy_names = []

            current = parent

            while current is not None:

                current_name = str(
                    getattr(
                        current,
                        "name",
                        ""
                    )
                ).strip()

                if current_name:

                    hierarchy_names.append(
                        current_name
                    )

                current_parent_id = getattr(
                    current,
                    "parent_id",
                    None
                )

                if current_parent_id is None:
                    break

                current = (
                    self.asset_manager.get_node(
                        current_parent_id
                    )
                )

            hierarchy_names.reverse()

            tag_parts = []

            for value in hierarchy_names:

                cleaned = (
                    str(value)
                    .strip()
                    .replace(" ", "-")
                )

                if cleaned:
                    tag_parts.append(cleaned)

            panel_tag_name = (
                str(name)
                .strip()
                .replace(" ", "-")
            )

            if panel_tag_name:
                tag_parts.append(
                    panel_tag_name
                )

            asset_tag = "-".join(
                tag_parts
            )

            # =================================================
            # CREATE
            # =================================================

            try:

                new_panel = (
                    self.asset_manager.create_node(
                        name=name,
                        node_type="PANEL",
                        parent_id=parent_id,
                        asset_tag=asset_tag
                    )
                )

            except ValueError as error:

                QMessageBox.warning(
                    self,
                    "Cannot Create Panel",
                    str(error)
                )

                return

            # =================================================
            # REFRESH WHILE PRESERVING TREE STATE
            # =================================================

            self.refresh_tree()

            if new_panel is not None:

                self.select_tree_node(
                    new_panel.node_id
                )

                self.display_selected_components()

            self._update_button_states()

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
                ct_count=int(configuration.get("ct_count", 0) or 0),
                relay_count=int(configuration.get("relay_count", 0) or 0),
                aux_count=int(configuration.get("aux_count", 0) or 0),
                meter_count=int(configuration.get("meter_count", 0) or 0),
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

            # =================================================
            # GET CTs BELONGING TO THIS PANEL
            # =================================================

            try:

                available_cts = (
                    self.component_manager
                    .get_panel_cts(
                        panel_id
                    )
                )

            except AttributeError:

                # Compatibility fallback for an older
                # ComponentManager.

                available_cts = [

                    item

                    for item
                    in self.component_manager
                    .get_panel_components(
                        panel_id
                    )

                    if str(
                        getattr(
                            item,
                            "component_type",
                            ""
                        )
                    ).strip().upper()
                    in (
                        "CT",
                        "CURRENT TRANSFORMER",
                    )
                ]

            # =================================================
            # OPEN RELAY TESTING
            # =================================================

            self.testing_dialog = RelayTestingDialog(

                project_id=project_id,

                panel_id=panel_id,

                relay_id=component.component_id,

                # Numerical relay
                component=component,

                # CTs mapped to this panel
                available_cts=available_cts,

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
        elif component_type in (
            "METER",
            "AMMETER",
            "VOLTMETER",
            "MULTIFUNCTION_METER",
        ):

            self.testing_dialog = MeterTestingDialog(

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
            project_folder=self.project_folder,
            parent=self,
        )

        self.test_history_view.exec()

    # =================================================
    # REFRESH
    # =================================================

    def refresh_component_view(self):

        self.display_selected_components()

    # =================================================
    # EDIT PHYSICAL ASSET
    # =================================================

    def edit_selected_asset(self):

        node = self.get_selected_node()

        if node is None:

            QMessageBox.warning(
                self,
                "No Asset Selected",
                "Please select a substation, "
                "switchboard or panel first.",
            )

            return

        node_type = str(
            getattr(
                node,
                "node_type",
                "",
            )
        ).upper()

        if node_type not in (
            "SUBSTATION",
            "SWITCHBOARD",
            "PANEL",
        ):

            QMessageBox.warning(
                self,
                "Invalid Selection",
                "This asset cannot be edited here.",
            )

            return

        # =================================================
        # LOAD GLOBAL ASSET
        # =================================================

        global_asset = None

        asset_id = getattr(
            node,
            "asset_id",
            None,
        )

        if asset_id:

            try:

                self.asset_manager.asset_library.load()

                global_asset = (
                    self.asset_manager
                    .asset_library
                    .get_asset(
                        asset_id
                    )
                )

            except Exception:

                global_asset = None
        # =================================================
        # OPEN EDIT DIALOG
        # =================================================

        dialog = AssetEditDialog(
            node=node,
            global_asset=global_asset,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        values = (
            dialog.get_values()
        )

        # =================================================
        # SAVE
        # =================================================

        try:

            updated_node = (
                self.asset_manager
                .update_asset_details(
                    node_id=node.node_id,
                    name=values["name"],
                    asset_tag=values["asset_tag"],
                    manufacturer=values["manufacturer"],
                    model=values["model"],
                    serial_number=values["serial_number"],
                )
            )

            self.refresh_tree()

            # Try to restore the selection after refresh.
            self.select_tree_node(
                updated_node.node_id
            )

            QMessageBox.information(
                self,
                "Asset Updated",
                f"{updated_node.name} "
                "has been updated successfully.",
            )

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Cannot Update Asset",
                str(error),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Update Failed",
                str(error),
            )

    # =====================================================
    # PANEL REPORT
    # =====================================================

# =====================================================
# PANEL REPORT
# =====================================================

    def generate_panel_report(
        self
    ):

        panel = self.get_selected_panel()

        if panel is None:

            QMessageBox.warning(
                self,
                "No Panel Selected",
                "Please select a panel first."
            )

            return

        project_id = getattr(
            self.project,
            "project_id",
            None
        )

        if project_id is None:

            QMessageBox.warning(
                self,
                "Project Error",
                "Unable to determine project ID."
            )

            return

        panel_id = getattr(
            panel,
            "node_id",
            None
        )

        if panel_id is None:

            QMessageBox.warning(
                self,
                "Panel Error",
                "Unable to determine panel ID."
            )

            return

        # =================================================
        # SELECT REPORT DATE
        # =================================================

        report_date = (
            self.select_panel_report_date()
        )

        if not report_date:

            return

        try:

            # =================================================
            # COMPONENTS
            # =================================================

            components = (
                self.component_manager
                .get_panel_components(
                    panel_id
                )
            )

            # =================================================
            # PROTECTION TESTS
            # =================================================

            protection_rows = (
                self.test_service
                .get_all_tests()
            )

            protection_tests = []

            for row in protection_rows:

                # ---------------------------------------------
                # Expected:
                #
                # 0 test_id
                # 1 project_id
                # 2 panel_id
                # 3 relay_id
                # 4 protection_code
                # 5 test_date
                # 6 result
                # 7 remarks
                # ---------------------------------------------

                if row[1] != project_id:
                    continue

                if row[2] != panel_id:
                    continue

                test = (
                    self.test_service
                    .get_test(
                        row[0]
                    )
                )

                if test is None:
                    continue

                if not self.test_matches_date(
                    test.get(
                        "test_date"
                    ),
                    report_date
                ):
                    continue

                protection_tests.append(
                    test
                )

            # =================================================
            # COMPONENT TESTS
            # =================================================

            component_rows = (
                self.test_service
                .get_all_component_tests()
            )

            component_tests = []

            for row in component_rows:

                # ---------------------------------------------
                # Expected:
                #
                # 0 test_id
                # 1 project_id
                # 2 panel_id
                # 3 component_id
                # 4 test_type
                # 5 test_date
                # 6 result
                # 7 remarks
                # ---------------------------------------------

                if row[1] != project_id:
                    continue

                if row[2] != panel_id:
                    continue

                test = (
                    self.test_service
                    .get_component_test(
                        row[0]
                    )
                )

                if test is None:
                    continue

                if not self.test_matches_date(
                    test.get(
                        "test_date"
                    ),
                    report_date
                ):
                    continue

                component_tests.append(
                    test
                )

            # =================================================
            # NOTHING TESTED ON SELECTED DATE
            # =================================================

            if not protection_tests and not component_tests:

                QMessageBox.information(
                    self,
                    "No Tests Found",
                    (
                        "No tests were conducted on "
                        f"{report_date} for panel "
                        f"{getattr(panel, 'name', panel_id)}."
                    )
                )

                return

            # =================================================
            # RESOLVE ELECTRICAL HIERARCHY
            #
            # Panel
            #   -> Switchboard
            #       -> Substation
            #
            # These names are passed to the report service so
            # the generated document is self-identifying.
            # =================================================

            substation_name = ""
            switchboard_name = ""

            current_node = panel

            while current_node is not None:

                node_type = str(
                    getattr(
                        current_node,
                        "node_type",
                        ""
                    )
                ).upper()

                node_name = str(
                    getattr(
                        current_node,
                        "name",
                        ""
                    )
                ).strip()

                if node_type == "SWITCHBOARD":

                    switchboard_name = node_name

                elif node_type == "SUBSTATION":

                    substation_name = node_name

                parent_node_id = getattr(
                    current_node,
                    "parent_id",
                    None
                )

                if parent_node_id is None:

                    break

                current_node = (
                    self.asset_manager.get_node(
                        parent_node_id
                    )
                )

            # =================================================
            # GENERATE REPORT
            # =================================================

            service = PanelReportService(
                self.project_folder
            )

            service.generate_report(

                panel=panel,

                components=components,

                protection_tests=(
                    protection_tests
                ),

                component_tests=(
                    component_tests
                ),

                report_date=report_date,

                substation_name=(
                    substation_name
                ),

                switchboard_name=(
                    switchboard_name
                ),

                parent=self
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Panel Report Failed",
                str(error)
            )


    # =====================================================
    # SELECT REPORT DATE
    # =====================================================

    def select_panel_report_date(
        self
    ):

        dialog = QDialog(
            self
        )

        dialog.setWindowTitle(
            "Panel Report Date"
        )

        dialog.resize(
            350,
            150
        )

        layout = QVBoxLayout(
            dialog
        )

        label = QLabel(
            "Select the date for which the panel report "
            "shall be generated:"
        )

        label.setWordWrap(
            True
        )

        layout.addWidget(
            label
        )

        date_edit = QDateEdit()

        date_edit.setCalendarPopup(
            True
        )

        date_edit.setDisplayFormat(
            "dd-MM-yyyy"
        )

        date_edit.setDate(
            QDate.currentDate()
        )

        layout.addWidget(
            date_edit
        )

        buttons = QHBoxLayout()

        cancel_button = QPushButton(
            "Cancel"
        )

        generate_button = QPushButton(
            "Generate"
        )

        buttons.addStretch()

        buttons.addWidget(
            cancel_button
        )

        buttons.addWidget(
            generate_button
        )

        layout.addLayout(
            buttons
        )

        cancel_button.clicked.connect(
            dialog.reject
        )

        generate_button.clicked.connect(
            dialog.accept
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return None

        return (
            date_edit
            .date()
            .toString(
                "yyyy-MM-dd"
            )
        )


    # =====================================================
    # TEST DATE MATCH
    # =====================================================

    @staticmethod
    def test_matches_date(
        test_date,
        report_date
    ):

        if not test_date:
            return False

        test_date = str(
            test_date
        ).strip()

        report_date = str(
            report_date
        ).strip()

        # -------------------------------------------------
        # ISO datetime
        #
        # 2026-08-15T16:42:32
        #
        # becomes
        #
        # 2026-08-15
        # -------------------------------------------------

        if "T" in test_date:

            test_date = (
                test_date
                .split("T")[0]
            )

        # -------------------------------------------------
        # ISO datetime with space
        #
        # 2026-08-15 16:42:32
        # -------------------------------------------------

        elif " " in test_date:

            test_date = (
                test_date
                .split(" ")[0]
            )

        # -------------------------------------------------
        # Already YYYY-MM-DD
        # -------------------------------------------------

        return (
            test_date
            ==
            report_date
        )