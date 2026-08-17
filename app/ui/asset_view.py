from pathlib import Path

from PySide6.QtCore import (
    Qt,
    QDate,
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

from app.services.asset_manager import (
    AssetManager
)

from app.services.component_manager import (
    ComponentManager
)

from app.ui.panel_config_dialog import (
    PanelConfigDialog
)

from app.ui.component_config_dialog import (
    ComponentConfigDialog
)

from app.ui.protection_function_dialog import (
    ProtectionFunctionDialog
)

from app.ui.relay_testing_dialog import (
    RelayTestingDialog
)

from app.ui.ct_testing_dialog import (
    CTTestingDialog
)

from app.ui.aux_relay_testing_dialog import (
    AuxRelayTestingDialog
)

from app.ui.meter_testing_dialog import (
    MeterTestingDialog
)

from app.ui.test_history_view import (
    TestHistoryView
)

from app.ui.asset_link_dialog import (
    AssetLinkDialog
)

from app.ui.asset_edit_dialog import (
    AssetEditDialog
)

from app.services.panel_report_service import (
    PanelReportService
)

from app.ui.panel_configuration_copy_dialog import (
    PanelConfigurationCopyDialog
)


# =========================================================
# PANEL CREATION DIALOG
# =========================================================


class PanelAssetDialog(QDialog):

    def __init__(
        self,
        suggested_asset_tag="",
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
            180
        )

        layout = QVBoxLayout(
            self
        )

        form = QFormLayout()

        # -------------------------------------------------
        # PANEL NAME
        # -------------------------------------------------

        self.name_edit = QLineEdit()

        self.name_edit.setPlaceholderText(
            "Example: P-03"
        )

        form.addRow(
            "Panel Name:",
            self.name_edit
        )

        # -------------------------------------------------
        # ASSET TAG
        # -------------------------------------------------

        self.asset_tag_edit = QLineEdit()

        self.asset_tag_edit.setPlaceholderText(
            "Example: REF3-HV201A-P03"
        )

        if suggested_asset_tag:

            self.asset_tag_edit.setText(
                suggested_asset_tag
            )

        form.addRow(
            "Asset Tag:",
            self.asset_tag_edit
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

    # =====================================================
    # VALUES
    # =====================================================

    def get_values(self):

        return (
            self.name_edit.text().strip(),
            self.asset_tag_edit.text().strip(),
        )

    # =====================================================
    # VALIDATION
    # =====================================================

    def accept(self):

        name = (
            self.name_edit
            .text()
            .strip()
        )

        asset_tag = (
            self.asset_tag_edit
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

        if not asset_tag:

            QMessageBox.warning(
                self,
                "Missing Asset Tag",
                "Please enter the physical asset tag."
            )

            self.asset_tag_edit.setFocus()

            return

        super().accept()


# =========================================================
# ASSET VIEW
# =========================================================


class AssetView(QWidget):

    def __init__(
        self,
        project_folder: Path,
        project,
        test_service,
        parent=None,
    ):

        super().__init__(
            parent
        )

        # =================================================
        # REFERENCES
        # =================================================

        self.project_folder = (
            project_folder
        )

        self.project = project

        self.test_service = (
            test_service
        )

        self.testing_dialog = None

        self.test_history_view = None

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

        layout.setContentsMargins(
            12,
            12,
            12,
            12,
        )

        layout.setSpacing(
            10
        )

        workspace = QHBoxLayout()

        workspace.setSpacing(
            12
        )

        # =================================================
        # LEFT
        # =================================================

        left_layout = QVBoxLayout()

        left_layout.setSpacing(
            8
        )

        asset_header = QLabel(
            "Asset Hierarchy"
        )

        asset_header.setObjectName(
            "SectionHeader"
        )

        left_layout.addWidget(
            asset_header
        )

        # =================================================
        # TREE
        # =================================================

        self.tree = QTreeWidget()

        self.tree.setHeaderLabel(
            "Project Assets"
        )

        self.tree.setMinimumHeight(
            280
        )

        self.tree.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.tree.setIndentation(
            24
        )

        self.tree.setAnimated(
            True
        )

        self.tree.setUniformRowHeights(
            True
        )

        left_layout.addWidget(
            self.tree,
            5
        )

        # =================================================
        # COMPONENTS
        # =================================================

        self.component_label = QLabel(
            "Test Components"
        )

        self.component_label.setObjectName(
            "SectionHeader"
        )

        left_layout.addWidget(
            self.component_label
        )

        self.component_list = QListWidget()

        self.component_list.setMinimumHeight(
            220
        )

        self.component_list.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.component_list.setSpacing(
            2
        )

        self.component_list.setUniformItemSizes(
            True
        )

        left_layout.addWidget(
            self.component_list,
            4
        )

        # =================================================
        # RIGHT ACTION PANEL
        # =================================================

        action_panel = QFrame()

        action_panel.setObjectName(
            "ActionPanel"
        )

        action_panel.setFixedWidth(
            270
        )

        action_layout = QVBoxLayout(
            action_panel
        )

        action_layout.setContentsMargins(
            12,
            12,
            12,
            12
        )

        action_layout.setSpacing(
            7
        )

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
            "Select an asset or component, "
            "then choose an action."
        )

        action_subtitle.setObjectName(
            "ActionSubtitle"
        )

        action_subtitle.setWordWrap(
            True
        )

        action_layout.addWidget(
            action_subtitle
        )

        # =================================================
        # BUTTONS
        # =================================================

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

        self.edit_asset_button = QPushButton(
            "Edit Asset"
        )

        self.configure_panel = QPushButton(
            "Edit Panel Configuration"
        )

        # =================================================
        # NEW
        # =================================================

        self.copy_panel_configuration = QPushButton(
            "Copy Configuration From Existing Panel"
        )

        self.configure_component = QPushButton(
            "Edit Component"
        )

        self.configure_protection = QPushButton(
            "Edit Protection Functions"
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

        self.test_history = (
            self.test_history_button
        )

        # =================================================
        # GROUP HELPER
        # =================================================

        def add_action_group(
            title,
            buttons,
        ):

            label = QLabel(
                title.upper()
            )

            label.setObjectName(
                "ActionGroup"
            )

            action_layout.addWidget(
                label
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

        # =================================================
        # ASSET STRUCTURE
        # =================================================

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

        # =================================================
        # EDITING
        # =================================================

        add_action_group(
            "Editing",
            [
                self.edit_asset_button,
                self.configure_panel,
                self.copy_panel_configuration,
                self.configure_component,
                self.configure_protection,
            ],
        )

        # =================================================
        # TESTING
        # =================================================

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
        # WORKSPACE
        # =================================================

        workspace.addLayout(
            left_layout,
            1
        )

        workspace.addWidget(
            action_panel
        )

        layout.addLayout(
            workspace,
            1
        )

        # =================================================
        # STYLE
        # =================================================

        self.setStyleSheet(
            """
            QLabel#SectionHeader {
                font-size: 15px;
                font-weight: 700;
                padding: 4px;
            }

            QLabel#ActionTitle {
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#ActionSubtitle {
                color: #999999;
                padding-bottom: 4px;
            }

            QLabel#ActionGroup {
                color: #999999;
                font-size: 11px;
                font-weight: 700;
                padding-top: 8px;
            }

            QFrame#ActionPanel {
                background-color: #252525;
                border: 1px solid #3e3e3e;
                border-radius: 7px;
            }

            QPushButton {
                min-height: 36px;
            }

            QPushButton#OpenTestingButton {
                min-height: 42px;
                font-weight: 600;
            }

            QPushButton#PanelReportButton {
                min-height: 42px;
                font-weight: 600;
            }

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

        self.copy_panel_configuration.clicked.connect(
            self.copy_configuration_from_existing_panel
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

        self.refresh_tree()

    # =====================================================
    # TREE
    # =====================================================

    def refresh_tree(
        self,
    ):

        selected_node_id = None

        current_item = (
            self.tree.currentItem()
        )

        if current_item is not None:

            selected_node_id = (
                current_item.data(
                    Qt.ItemDataRole.UserRole
                )
            )

        self.tree.blockSignals(
            True
        )

        self.component_list.clear()

        self.tree.clear()

        roots = (
            self.asset_manager
            .get_children(None)
        )

        for node in roots:

            item = (
                self._create_tree_item(
                    node
                )
            )

            self.tree.addTopLevelItem(
                item
            )

        # =================================================
        # IMPORTANT
        #
        # Project opens COLLAPSED.
        # =================================================

        self.tree.collapseAll()

        self.tree.blockSignals(
            False
        )

        # Restore selection only if possible.

        if selected_node_id:

            self.select_tree_node(
                selected_node_id
            )

        self._update_button_states()

        self.display_selected_components()

    # =====================================================
    # TREE ITEM
    # =====================================================

    def _create_tree_item(
        self,
        node,
    ):

        item = QTreeWidgetItem()

        item.setText(
            0,
            str(
                getattr(
                    node,
                    "name",
                    ""
                )
            )
        )

        item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            getattr(
                node,
                "node_id",
                None
            )
        )

        children = (
            self.asset_manager
            .get_children(
                node.node_id
            )
        )

        for child in children:

            item.addChild(
                self._create_tree_item(
                    child
                )
            )

        return item

    # =====================================================
    # SELECT TREE NODE
    # =====================================================

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
                    Qt.ItemDataRole.UserRole
                )

                if child_id == node_id:

                    return child

                result = (
                    find_item(
                        child
                    )
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
                Qt.ItemDataRole.UserRole
            )

            if item_id == node_id:

                self.tree.setCurrentItem(
                    item
                )

                return True

            result = (
                find_item(
                    item
                )
            )

            if result is not None:

                # Expand ancestors so that the
                # selected item can actually be seen.

                parent = result.parent()

                while parent is not None:

                    parent.setExpanded(
                        True
                    )

                    parent = parent.parent()

                self.tree.setCurrentItem(
                    result
                )

                return True

        return False

    # =====================================================
    # SELECTED NODE
    # =====================================================

    def get_selected_node(
        self,
    ):

        item = (
            self.tree.currentItem()
        )

        if item is None:

            return None

        node_id = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if node_id is None:

            return None

        return (
            self.asset_manager
            .get_node(
                node_id
            )
        )

    # =====================================================
    # SELECTED PANEL
    # =====================================================

    def get_selected_panel(
        self,
    ):

        node = (
            self.get_selected_node()
        )

        if node is None:

            return None

        if str(
            getattr(
                node,
                "node_type",
                ""
            )
        ).strip().upper() == "PANEL":

            return node

        return None

    # =====================================================
    # COMPONENTS
    # =====================================================

    def display_selected_components(
        self,
    ):

        self.component_list.clear()

        node = (
            self.get_selected_node()
        )

        if node is None:

            self._update_button_states()

            return

        if str(
            getattr(
                node,
                "node_type",
                ""
            )
        ).strip().upper() != "PANEL":

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
                component.component_id
            )

            self.component_list.addItem(
                item
            )

        self._update_button_states()

    # =====================================================
    # COMPONENT SELECTION
    # =====================================================

    def on_component_selection_changed(
        self,
    ):

        self._update_button_states()

    # =====================================================
    # SELECTED COMPONENT
    # =====================================================

    def get_selected_component(
        self,
    ):

        item = self.component_list.currentItem()

        if item is None:
            return None

        # QListWidgetItem.data() takes ONLY the role.
        component_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        if component_id is None:
            return None

        if hasattr(
            self.component_manager,
            "get_component"
        ):

            return self.component_manager.get_component(
                component_id
            )

        return (
            self.component_manager
            .components
            .get(
                component_id
            )
        )
    # =====================================================
    # SELECT COMPONENT
    # =====================================================

    def select_component_by_id(
        self,
        component_id,
    ):

        for index in range(
            self.component_list.count()
        ):

            item = (
                self.component_list.item(
                    index
                )
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
    # BUTTON STATE
    # =====================================================

    def _update_button_states(
        self,
    ):

        node = (
            self.get_selected_node()
        )

        component = (
            self.get_selected_component()
        )

        node_type = (
            str(
                getattr(
                    node,
                    "node_type",
                    ""
                )
            ).strip().upper()
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

        self.edit_asset_button.setEnabled(
            node_type in (
                "SUBSTATION",
                "SWITCHBOARD",
                "PANEL",
            )
        )

        self.configure_panel.setEnabled(
            panel_selected
        )

        self.copy_panel_configuration.setEnabled(
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

    # =====================================================
    # COMPATIBILITY
    # =====================================================

    def update_button_state(
        self,
    ):

        self._update_button_states()

    # =====================================================
    # INPUT
    # =====================================================

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

    # =====================================================
    # CREATE SUBSTATION
    # =====================================================

    def create_substation(
        self,
    ):

        name = (
            self.ask_name(
                "Add Substation"
            )
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

    # =====================================================
    # LINK SUBSTATION
    # =====================================================

    def link_existing_substation(
        self,
    ):

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

        selected = (
            dialog.get_selected_asset()
        )

        if not selected:

            return

        try:

            linked_node = (
                self.asset_manager.link_asset(
                    asset_id=selected[
                        "asset_id"
                    ],
                    parent_id=None,
                    name=selected.get(
                        "name"
                    ),
                )
            )

            self.refresh_tree()

            QMessageBox.information(
                self,
                "Substation Linked",
                f"'{linked_node.name}' "
                "has been linked to this project.",
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Link Failed",
                str(error),
            )

    # =====================================================
    # CREATE SWITCHBOARD
    # =====================================================

    def create_switchboard(
        self,
    ):

        parent = (
            self.get_selected_node()
        )

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
        ).strip().upper() != "SUBSTATION":

            QMessageBox.warning(
                self,
                "Invalid Selection",
                "A switchboard must belong to a substation.",
            )

            return

        name = (
            self.ask_name(
                "Add Switchboard"
            )
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

    # =====================================================
    # AVAILABLE SWITCHBOARDS
    # =====================================================

    def get_available_master_switchboards(
        self,
    ):

        parent = (
            self.get_selected_node()
        )

        if parent is None:

            return []

        if str(
            getattr(
                parent,
                "node_type",
                ""
            )
        ).strip().upper() != "SUBSTATION":

            return []

        return (
            self.asset_manager
            .get_available_global_assets(
                asset_type="SWITCHBOARD",
                parent_node=parent,
            )
        )

    # =====================================================
    # LINK SWITCHBOARD
    # =====================================================

    def link_existing_switchboard(
        self,
    ):

        parent = (
            self.get_selected_node()
        )

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
        ).strip().upper() != "SUBSTATION":

            QMessageBox.warning(
                self,
                "Invalid Selection",
                "An existing switchboard must be "
                "linked under a substation.",
            )

            return

        available = (
            self.get_available_master_switchboards()
        )

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

        selected = (
            dialog.get_selected_asset()
        )

        if not selected:

            return

        try:

            linked_node = (
                self.asset_manager.link_asset(
                    asset_id=selected[
                        "asset_id"
                    ],
                    parent_id=parent.node_id,
                    name=selected.get(
                        "name"
                    ),
                )
            )

            self.refresh_tree()

            QMessageBox.information(
                self,
                "Switchboard Linked",
                f"Switchboard '{linked_node.name}' "
                "has been linked to this substation.",
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Link Failed",
                str(error),
            )

    # =====================================================
    # CREATE PANEL
    # =====================================================

    def create_panel(
        self,
    ):

        if self._creating_panel:

            return

        self._creating_panel = True

        try:

            parent = (
                self.get_selected_node()
            )

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
            ).strip().upper() != "SWITCHBOARD":

                QMessageBox.warning(
                    self,
                    "Invalid Selection",
                    "A panel must belong to a switchboard."
                )

                return

            # =================================================
            # SUGGEST ASSET TAG
            # =================================================

            hierarchy = []

            current = parent

            while current is not None:

                name = str(
                    getattr(
                        current,
                        "name",
                        ""
                    )
                ).strip()

                if name:

                    hierarchy.insert(
                        0,
                        name
                    )

                parent_id = getattr(
                    current,
                    "parent_id",
                    None
                )

                if parent_id is None:

                    break

                current = (
                    self.asset_manager
                    .get_node(
                        parent_id
                    )
                )

            prefix = "-".join(
                value.replace(
                    " ",
                    "-"
                )
                for value in hierarchy
            )

            suggested_tag = (
                f"{prefix}-PANEL"
                if prefix
                else ""
            )

            dialog = PanelAssetDialog(
                suggested_asset_tag=suggested_tag,
                parent=self,
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

            new_panel = (
                self.asset_manager.create_node(
                    name=name,
                    node_type="PANEL",
                    parent_id=parent.node_id,
                    asset_tag=asset_tag,
                )
            )

            self.refresh_tree()

            if new_panel is not None:

                self.select_tree_node(
                    new_panel.node_id
                )

                self.display_selected_components()

        except ValueError as error:

            QMessageBox.warning(
                self,
                "Cannot Create Panel",
                str(error),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Panel Creation Failed",
                str(error),
            )

        finally:

            self._creating_panel = False

    # =====================================================
    # AVAILABLE PANELS
    # =====================================================

    def get_available_master_panels(
        self,
    ):

        parent = (
            self.get_selected_node()
        )

        if parent is None:

            return []

        if str(
            getattr(
                parent,
                "node_type",
                ""
            )
        ).strip().upper() != "SWITCHBOARD":

            return []

        return (
            self.asset_manager
            .get_available_global_assets(
                asset_type="PANEL",
                parent_node=parent,
            )
        )

    # =====================================================
    # LINK PANEL
    # =====================================================

    def link_existing_panel(
        self,
    ):

        parent = (
            self.get_selected_node()
        )

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
        ).strip().upper() != "SWITCHBOARD":

            QMessageBox.warning(
                self,
                "Invalid Selection",
                "A panel must be linked under a switchboard.",
            )

            return

        available = (
            self.get_available_master_panels()
        )

        if not available:

            QMessageBox.information(
                self,
                "No Panels Available",
                "There are no unlinked panels "
                "available for this switchboard.",
            )

            return

        dialog = AssetLinkDialog(
            available,
            asset_type="PANEL",
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        selected = (
            dialog.get_selected_asset()
        )

        if not selected:

            return

        try:

            linked_node = (
                self.asset_manager.link_asset(
                    asset_id=selected[
                        "asset_id"
                    ],
                    parent_id=parent.node_id,
                    name=selected.get(
                        "name"
                    ),
                )
            )

            metadata = (
                selected.get(
                    "metadata"
                )
                or {}
            )

            panel_configuration = (
                metadata.get(
                    "panel_configuration",
                    {}
                )
            )

            if panel_configuration:

                try:

                    self.asset_manager.update_panel_configuration(
                        linked_node.node_id,
                        panel_configuration,
                    )

                except Exception:

                    pass

            component_data = (
                metadata.get(
                    "components",
                    []
                )
            )

            if component_data:

                if hasattr(
                    self.component_manager,
                    "clone_panel_components"
                ):

                    self.component_manager.clone_panel_components(
                        linked_node.node_id,
                        component_data,
                    )

                elif hasattr(
                    self.component_manager,
                    "restore_global_panel_components"
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

        except Exception as error:

            QMessageBox.critical(
                self,
                "Panel Import Failed",
                str(error),
            )

    # =====================================================
    # PANEL CONFIGURATION
    # =====================================================

    def configure_selected_panel(
        self,
    ):

        panel = (
            self.get_selected_panel()
        )

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

        configuration = (
            dialog.get_configuration()
        )

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
                        0
                    )
                    or 0
                ),
                relay_count=int(
                    configuration.get(
                        "relay_count",
                        0
                    )
                    or 0
                ),
                aux_count=int(
                    configuration.get(
                        "aux_count",
                        0
                    )
                    or 0
                ),
                meter_count=int(
                    configuration.get(
                        "meter_count",
                        0
                    )
                    or 0
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

    # =====================================================
    # COPY CONFIGURATION FROM EXISTING PANEL
    # =====================================================

    def copy_configuration_from_existing_panel(
        self,
    ):

        target_panel = (
            self.get_selected_panel()
        )

        if target_panel is None:

            QMessageBox.warning(
                self,
                "No Target Panel",
                "Please select the panel into which "
                "the configuration should be copied."
            )

            return

        dialog = PanelConfigurationCopyDialog(
            asset_manager=self.asset_manager,
            target_panel_id=target_panel.node_id,
            parent=self,
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        source_panel = (
            dialog.source_panel
        )

        selected_attributes = (
            dialog.get_selected_attributes()
        )

        if source_panel is None:

            return

        try:

            # =================================================
            # CONFIRM
            # =================================================

            hierarchy = (
                self.get_panel_hierarchy_names(
                    source_panel
                )
            )

            source_description = (
                " / ".join(
                    hierarchy
                )
            )

            target_hierarchy = (
                self.get_panel_hierarchy_names(
                    target_panel
                )
            )

            target_description = (
                " / ".join(
                    target_hierarchy
                )
            )

            answer = QMessageBox.question(
                self,
                "Confirm Configuration Copy",
                (
                    "Copy selected configuration from:\n\n"
                    f"{source_description}\n\n"
                    "to:\n\n"
                    f"{target_description}\n\n"
                    "Panel name, asset tag and unchecked "
                    "panel-specific values will remain unchanged."
                ),
                QMessageBox.StandardButton.Yes
                |
                QMessageBox.StandardButton.No,
            )

            if answer != QMessageBox.StandardButton.Yes:

                return

            # =================================================
            # PANEL CONFIGURATION
            # =================================================

            panel_fields = (
                "equipment_name",
                "equipment_type",
                "ct_count",
                "relay_count",
                "aux_count",
                "meter_count",
            )

            panel_configuration = {}

            for field in panel_fields:

                if field not in selected_attributes:

                    continue

                if not hasattr(
                    source_panel,
                    field
                ):

                    continue

                panel_configuration[
                    field
                ] = getattr(
                    source_panel,
                    field
                )

            if panel_configuration:

                self.asset_manager.update_panel_configuration(
                    target_panel.node_id,
                    panel_configuration,
                )

            # =================================================
            # COMPONENT COUNTS
            # =================================================

            target_ct_count = self.safe_int(
                getattr(
                    target_panel,
                    "ct_count",
                    0
                )
            )

            target_relay_count = self.safe_int(
                getattr(
                    target_panel,
                    "relay_count",
                    0
                )
            )

            target_aux_count = self.safe_int(
                getattr(
                    target_panel,
                    "aux_count",
                    0
                )
            )

            target_meter_count = self.safe_int(
                getattr(
                    target_panel,
                    "meter_count",
                    0
                )
            )

            if "ct_count" in selected_attributes:

                target_ct_count = self.safe_int(
                    getattr(
                        source_panel,
                        "ct_count",
                        0
                    )
                )

            if "relay_count" in selected_attributes:

                target_relay_count = self.safe_int(
                    getattr(
                        source_panel,
                        "relay_count",
                        0
                    )
                )

            if "aux_count" in selected_attributes:

                target_aux_count = self.safe_int(
                    getattr(
                        source_panel,
                        "aux_count",
                        0
                    )
                )

            if "meter_count" in selected_attributes:

                target_meter_count = self.safe_int(
                    getattr(
                        source_panel,
                        "meter_count",
                        0
                    )
                )

            # =================================================
            # REGENERATE COMPONENT STRUCTURE
            # =================================================

            if any(
                field in selected_attributes

                for field in (
                    "ct_count",
                    "relay_count",
                    "aux_count",
                    "meter_count",
                )
            ):

                self.component_manager.generate_panel_components(
                    panel_id=target_panel.node_id,
                    ct_count=target_ct_count,
                    relay_count=target_relay_count,
                    aux_count=target_aux_count,
                    meter_count=target_meter_count,
                )

            # =================================================
            # SOURCE COMPONENTS
            # =================================================

            source_components = (
                self.component_manager
                .get_panel_components(
                    source_panel.node_id
                )
            )

            target_components = (
                self.component_manager
                .get_panel_components(
                    target_panel.node_id
                )
            )

            # =================================================
            # INDEX COMPONENTS
            #
            # CT-01 -> CT-01
            # CT-02 -> CT-02
            # REL-01 -> REL-01
            # AUX-01 -> AUX-01
            # M-01 -> M-01
            # =================================================

            source_by_key = {}

            for component in source_components:

                key = (
                    self.component_identity_key(
                        component
                    )
                )

                source_by_key[
                    key
                ] = component

            target_by_key = {}

            for component in target_components:

                key = (
                    self.component_identity_key(
                        component
                    )
                )

                target_by_key[
                    key
                ] = component

            # =================================================
            # COMPONENT FIELDS
            # =================================================

            component_fields = [

                "manufacturer",

                "model",

                "serial_number",

                "description",

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
            ]

            copied_components = 0

            skipped_components = 0

            for key, source_component in (
                source_by_key.items()
            ):

                target_component = (
                    target_by_key.get(
                        key
                    )
                )

                if target_component is None:

                    skipped_components += 1

                    continue

                configuration = {}

                for field in component_fields:

                    if field not in selected_attributes:

                        continue

                    if not hasattr(
                        source_component,
                        field
                    ):

                        continue

                    value = getattr(
                        source_component,
                        field
                    )

                    if isinstance(
                        value,
                        list
                    ):

                        value = list(
                            value
                        )

                    configuration[
                        field
                    ] = value

                if not configuration:

                    continue

                self.component_manager.update_component_configuration(
                    target_component.component_id,
                    configuration,
                )

                copied_components += 1

            # =================================================
            # REFRESH
            # =================================================

            self.refresh_tree()

            self.select_tree_node(
                target_panel.node_id
            )

            self.display_selected_components()

            # =================================================
            # SUCCESS
            # =================================================

            QMessageBox.information(
                self,
                "Configuration Copied",
                (
                    "Panel configuration copied successfully.\n\n"
                    f"Source: {source_panel.name}\n"
                    f"Target: {target_panel.name}\n\n"
                    f"Components updated: "
                    f"{copied_components}\n"
                    f"Components skipped: "
                    f"{skipped_components}"
                )
            )

        except (
            ValueError,
            TypeError,
        ) as error:

            QMessageBox.warning(
                self,
                "Cannot Copy Configuration",
                str(error),
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Copy Failed",
                str(error),
            )

    # =====================================================
    # HELPERS FOR COPY
    # =====================================================

    @staticmethod
    def safe_int(
        value,
    ):

        try:

            return int(
                value or 0
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0

    @staticmethod
    def component_identity_key(
        component,
    ):

        component_type = str(
            getattr(
                component,
                "component_type",
                ""
            )
        ).strip().upper()

        name = str(
            getattr(
                component,
                "name",
                ""
            )
        ).strip().upper()

        return (
            component_type,
            name,
        )

    def get_panel_hierarchy_names(
        self,
        panel,
    ):

        result = []

        current = panel

        while current is not None:

            name = str(
                getattr(
                    current,
                    "name",
                    ""
                )
            ).strip()

            if name:

                result.insert(
                    0,
                    name
                )

            parent_id = getattr(
                current,
                "parent_id",
                None
            )

            if parent_id is None:

                break

            current = (
                self.asset_manager
                .get_node(
                    parent_id
                )
            )

        return result

    # =====================================================
    # COMPONENT CONFIGURATION
    # =====================================================

    def configure_selected_component(
        self,
    ):

        component = (
            self.get_selected_component()
        )

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

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error),
            )

    # =====================================================
    # PROTECTION FUNCTIONS
    # =====================================================

    def configure_selected_protection(
        self,
    ):

        component = (
            self.get_selected_component()
        )

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
                ""
            )
        ).strip().upper()

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
                    []
                ),
            )

            self.display_selected_components()

            self.select_component_by_id(
                component.component_id
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error),
            )

    # =====================================================
    # EDIT ASSET
    # =====================================================

    def edit_selected_asset(
        self,
    ):

        node = (
            self.get_selected_node()
        )

        if node is None:

            QMessageBox.warning(
                self,
                "No Asset Selected",
                "Please select an asset first.",
            )

            return

        node_type = str(
            getattr(
                node,
                "node_type",
                ""
            )
        ).strip().upper()

        if node_type not in (
            "SUBSTATION",
            "SWITCHBOARD",
            "PANEL",
        ):

            return

        global_asset = None

        asset_id = getattr(
            node,
            "asset_id",
            None
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

        try:

            updated_node = (
                self.asset_manager
                .update_asset_details(
                    node_id=node.node_id,
                    name=values["name"],
                    asset_tag=values["asset_tag"],
                    manufacturer=values[
                        "manufacturer"
                    ],
                    model=values[
                        "model"
                    ],
                    serial_number=values[
                        "serial_number"
                    ],
                )
            )

            self.refresh_tree()

            self.select_tree_node(
                updated_node.node_id
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Update Failed",
                str(error),
            )

    # =====================================================
    # TESTING
    # =====================================================

    def open_component_testing(
        self,
    ):

        self.open_testing_view()

    def open_testing_view(
        self,
    ):

        component = (
            self.get_selected_component()
        )

        if component is None:

            QMessageBox.warning(
                self,
                "No Component Selected",
                "Please select a component first.",
            )

            return

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
            None
        )

        if not project_id:

            QMessageBox.warning(
                self,
                "Project Error",
                "Unable to determine project ID.",
            )

            return

        panel = (
            self.get_selected_panel()
        )

        panel_id = (
            getattr(
                panel,
                "node_id",
                None
            )
            if panel is not None
            else getattr(
                component,
                "panel_id",
                None
            )
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
                ""
            )
        ).strip().upper()

        if component_type == "NUMERICAL_RELAY":

            try:

                available_cts = (
                    self.component_manager
                    .get_panel_cts(
                        panel_id
                    )
                )

            except AttributeError:

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

            self.testing_dialog = RelayTestingDialog(
                project_id=project_id,
                panel_id=panel_id,
                relay_id=component.component_id,
                component=component,
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

    # =====================================================
    # TESTING LIFETIME
    # =====================================================

    def close_testing_dialog(
        self,
    ):

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

    # =====================================================
    # TEST HISTORY
    # =====================================================

    def open_test_history(
        self,
    ):

        panel = (
            self.get_selected_panel()
        )

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
            None
        )

        panel_id = getattr(
            panel,
            "node_id",
            None
        )

        if not project_id or not panel_id:

            return

        self.test_history_view = TestHistoryView(
            test_service=self.test_service,
            project_id=project_id,
            panel_id=panel_id,
            project_folder=self.project_folder,
            parent=self,
        )

        self.test_history_view.exec()

    # =====================================================
    # PANEL REPORT
    # =====================================================

    def generate_panel_report(
        self,
    ):

        panel = (
            self.get_selected_panel()
        )

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

        panel_id = getattr(
            panel,
            "node_id",
            None
        )

        if project_id is None or panel_id is None:

            return

        report_date = (
            self.select_panel_report_date()
        )

        if not report_date:

            return

        try:

            components = (
                self.component_manager
                .get_panel_components(
                    panel_id
                )
            )

            protection_tests = []

            for row in (
                self.test_service
                .get_all_tests()
                or []
            ):

                if len(row) < 6:

                    continue

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

                if self.test_matches_date(
                    test.get(
                        "test_date"
                    ),
                    report_date
                ):

                    protection_tests.append(
                        test
                    )

            component_tests = []

            for row in (
                self.test_service
                .get_all_component_tests()
                or []
            ):

                if len(row) < 6:

                    continue

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

                if self.test_matches_date(
                    test.get(
                        "test_date"
                    ),
                    report_date
                ):

                    component_tests.append(
                        test
                    )

            if not protection_tests and not component_tests:

                QMessageBox.information(
                    self,
                    "No Tests Found",
                    (
                        "No tests were conducted on "
                        f"{report_date} for "
                        f"{panel.name}."
                    )
                )

                return

            hierarchy = (
                self.get_panel_hierarchy_names(
                    panel
                )
            )

            substation_name = ""

            switchboard_name = ""

            for node in hierarchy:

                current = str(
                    node
                )

                node_obj = (
                    self.asset_manager
                    .find_node(
                        current
                    )
                )

                if node_obj is None:

                    continue

                node_type = str(
                    getattr(
                        node_obj,
                        "node_type",
                        ""
                    )
                ).upper()

                if node_type == "SUBSTATION":

                    substation_name = current

                elif node_type == "SWITCHBOARD":

                    switchboard_name = current

            service = PanelReportService(
                self.project_folder
            )

            service.generate_report(
                panel=panel,
                components=components,
                protection_tests=protection_tests,
                component_tests=component_tests,
                report_date=report_date,
                substation_name=substation_name,
                switchboard_name=switchboard_name,
                parent=self,
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Panel Report Failed",
                str(error)
            )

    # =====================================================
    # REPORT DATE
    # =====================================================

    def select_panel_report_date(
        self,
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
    # DATE MATCH
    # =====================================================

    @staticmethod
    def test_matches_date(
        test_date,
        report_date,
    ):

        if not test_date:

            return False

        value = str(
            test_date
        ).strip()

        if "T" in value:

            value = (
                value.split(
                    "T"
                )[0]
            )

        elif " " in value:

            value = (
                value.split(
                    " "
                )[0]
            )

        return (
            value
            ==
            str(
                report_date
            ).strip()
        )

    # =====================================================
    # REFRESH COMPONENT VIEW
    # =====================================================

    def refresh_component_view(
        self,
    ):

        self.display_selected_components()

    # =====================================================
    # CLOSE EVENT
    # =====================================================

    def closeEvent(
        self,
        event,
    ):

        self.close_testing_dialog()

        event.accept()