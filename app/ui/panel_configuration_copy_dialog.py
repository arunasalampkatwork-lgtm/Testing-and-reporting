from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QLabel,
    QCheckBox,
    QPushButton,
    QScrollArea,
    QWidget,
    QMessageBox,
    QFrame,
)


class PanelConfigurationCopyDialog(QDialog):
    """
    Dialog used to select an existing panel and choose which
    configuration attributes should be copied into the target panel.

    The source panel is selected using the same hierarchy:

        Substation
            └── Switchboard
                    └── Panel

    Panel identity fields are deliberately NOT selected by default.
    """

    def __init__(
        self,
        asset_manager,
        target_panel_id,
        parent=None,
    ):

        super().__init__(parent)

        self.asset_manager = asset_manager
        self.target_panel_id = target_panel_id

        self.source_panel = None

        self.checkboxes = {}

        self.setWindowTitle(
            "Copy Panel Configuration"
        )

        self.resize(
            950,
            720
        )

        self.build_ui()

        self.populate_tree()

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            14,
            14,
            14,
            14
        )

        main_layout.setSpacing(
            10
        )

        # =================================================
        # TITLE
        # =================================================

        title = QLabel(
            "Copy Configuration From Existing Panel"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: 700;
            }
            """
        )

        main_layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Select the source panel from the hierarchy, "
            "then choose which configuration attributes "
            "should be copied."
        )

        subtitle.setWordWrap(
            True
        )

        subtitle.setStyleSheet(
            "color: #999999;"
        )

        main_layout.addWidget(
            subtitle
        )

        # =================================================
        # SOURCE / OPTIONS
        # =================================================

        workspace = QHBoxLayout()

        workspace.setSpacing(
            12
        )

        # =================================================
        # SOURCE TREE
        # =================================================

        source_frame = QFrame()

        source_frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        source_layout = QVBoxLayout(
            source_frame
        )

        source_label = QLabel(
            "Source Panel"
        )

        source_label.setStyleSheet(
            "font-size: 15px; font-weight: 700;"
        )

        source_layout.addWidget(
            source_label
        )

        self.tree = QTreeWidget()

        self.tree.setHeaderLabel(
            "Project Assets"
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

        self.tree.itemSelectionChanged.connect(
            self.on_source_selection_changed
        )

        source_layout.addWidget(
            self.tree
        )

        self.selected_source_label = QLabel(
            "No panel selected"
        )

        self.selected_source_label.setWordWrap(
            True
        )

        self.selected_source_label.setStyleSheet(
            """
            QLabel {
                padding: 8px;
                background: #303030;
                border-radius: 5px;
                font-weight: 600;
            }
            """
        )

        source_layout.addWidget(
            self.selected_source_label
        )

        workspace.addWidget(
            source_frame,
            1
        )

        # =================================================
        # CONFIGURATION OPTIONS
        # =================================================

        options_frame = QFrame()

        options_frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        options_layout = QVBoxLayout(
            options_frame
        )

        options_title = QLabel(
            "Configuration to Copy"
        )

        options_title.setStyleSheet(
            "font-size: 15px; font-weight: 700;"
        )

        options_layout.addWidget(
            options_title
        )

        # -------------------------------------------------
        # SELECT ALL
        # -------------------------------------------------

        select_row = QHBoxLayout()

        self.select_all_checkbox = QCheckBox(
            "Select All"
        )

        self.select_all_checkbox.setChecked(
            True
        )

        self.select_all_checkbox.stateChanged.connect(
            self.select_all_changed
        )

        select_row.addWidget(
            self.select_all_checkbox
        )

        select_row.addStretch()

        options_layout.addLayout(
            select_row
        )

        # -------------------------------------------------
        # SCROLL AREA
        # -------------------------------------------------

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        container = QWidget()

        container_layout = QVBoxLayout(
            container
        )

        container_layout.setSpacing(
            5
        )

        # =================================================
        # PANEL CONFIGURATION
        # =================================================

        self.add_section(
            container_layout,
            "Panel Configuration"
        )

        self.add_checkbox(
            container_layout,
            "equipment_name",
            "Feed / Equipment Name",
            True
        )

        self.add_checkbox(
            container_layout,
            "equipment_type",
            "Equipment Type",
            True
        )

        self.add_checkbox(
            container_layout,
            "ct_count",
            "Number of CTs",
            True
        )

        self.add_checkbox(
            container_layout,
            "relay_count",
            "Numerical Relays",
            True
        )

        self.add_checkbox(
            container_layout,
            "aux_count",
            "Auxiliary Relays",
            True
        )

        self.add_checkbox(
            container_layout,
            "meter_count",
            "Meters",
            True
        )

        # =================================================
        # COMMON COMPONENT CONFIGURATION
        # =================================================

        self.add_section(
            container_layout,
            "Common Component Configuration"
        )

        self.add_checkbox(
            container_layout,
            "manufacturer",
            "Manufacturer",
            True
        )

        self.add_checkbox(
            container_layout,
            "model",
            "Model",
            True
        )

        self.add_checkbox(
            container_layout,
            "description",
            "Description",
            True
        )

        # =================================================
        # CT CONFIGURATION
        # =================================================

        self.add_section(
            container_layout,
            "CT Configuration"
        )

        self.add_checkbox(
            container_layout,
            "ct_class",
            "CT Class",
            True
        )

        self.add_checkbox(
            container_layout,
            "burden",
            "Burden",
            True
        )

        self.add_checkbox(
            container_layout,
            "core",
            "Core",
            True
        )

        # =================================================
        # NUMERICAL RELAY
        # =================================================

        self.add_section(
            container_layout,
            "Numerical Relay Configuration"
        )

        self.add_checkbox(
            container_layout,
            "vt_ratio",
            "VT Ratio",
            True
        )

        self.add_checkbox(
            container_layout,
            "firmware",
            "Firmware",
            True
        )

        self.add_checkbox(
            container_layout,
            "protection_functions",
            "Protection Functions",
            True
        )

        # =================================================
        # AUX RELAY
        # =================================================

        self.add_section(
            container_layout,
            "Auxiliary Relay Configuration"
        )

        self.add_checkbox(
            container_layout,
            "coil_voltage",
            "Coil Voltage",
            True
        )

        self.add_checkbox(
            container_layout,
            "contact_configuration",
            "Contact Configuration",
            True
        )

        # =================================================
        # METER
        # =================================================

        self.add_section(
            container_layout,
            "Meter Configuration"
        )

        self.add_checkbox(
            container_layout,
            "meter_type",
            "Meter Type",
            True
        )

        self.add_checkbox(
            container_layout,
            "meter_functions",
            "Meter Functions",
            True
        )

        self.add_checkbox(
            container_layout,
            "accuracy_class",
            "Accuracy Class",
            True
        )

        # =================================================
        # PANEL-SPECIFIC VALUES
        # =================================================

        self.add_section(
            container_layout,
            "Panel / Component Specific Values"
        )

        # These are intentionally OFF.

        self.add_checkbox(
            container_layout,
            "serial_number",
            "Serial Number",
            False
        )

        self.add_checkbox(
            container_layout,
            "ct_primary",
            "CT Primary Current",
            False
        )

        self.add_checkbox(
            container_layout,
            "ct_secondary",
            "CT Secondary Current",
            False
        )

        self.add_checkbox(
            container_layout,
            "ct_ratio",
            "CT Ratio",
            False
        )

        container_layout.addStretch()

        scroll.setWidget(
            container
        )

        options_layout.addWidget(
            scroll
        )

        workspace.addWidget(
            options_frame,
            1
        )

        main_layout.addLayout(
            workspace,
            1
        )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        buttons.addStretch()

        cancel_button = QPushButton(
            "Cancel"
        )

        cancel_button.clicked.connect(
            self.reject
        )

        buttons.addWidget(
            cancel_button
        )

        self.copy_button = QPushButton(
            "Copy Configuration"
        )

        self.copy_button.setMinimumHeight(
            38
        )

        self.copy_button.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            self.copy_button
        )

        main_layout.addLayout(
            buttons
        )

    # =====================================================
    # SECTION
    # =====================================================

    @staticmethod
    def add_section(
        layout,
        title,
    ):

        label = QLabel(
            title
        )

        label.setStyleSheet(
            """
            QLabel {
                font-weight: 700;
                color: #dddddd;
                padding-top: 8px;
                padding-bottom: 3px;
            }
            """
        )

        layout.addWidget(
            label
        )

    # =====================================================
    # CHECKBOX
    # =====================================================

    def add_checkbox(
        self,
        layout,
        key,
        text,
        checked,
    ):

        checkbox = QCheckBox(
            text
        )

        checkbox.setChecked(
            checked
        )

        self.checkboxes[
            key
        ] = checkbox

        layout.addWidget(
            checkbox
        )

    # =====================================================
    # TREE
    # =====================================================

    def populate_tree(self):

        self.tree.clear()

        roots = (
            self.asset_manager
            .get_children(None)
        )

        for node in roots:

            item = self.create_tree_item(
                node
            )

            self.tree.addTopLevelItem(
                item
            )

        # IMPORTANT:
        # Source tree starts collapsed.

        self.tree.collapseAll()

    # =====================================================
    # CREATE TREE ITEM
    # =====================================================

    def create_tree_item(
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

        item.setData(
            0,
            Qt.ItemDataRole.UserRole + 1,
            str(
                getattr(
                    node,
                    "node_type",
                    ""
                )
            ).strip().upper()
        )

        children = (
            self.asset_manager
            .get_children(
                node.node_id
            )
        )

        for child in children:

            item.addChild(
                self.create_tree_item(
                    child
                )
            )

        return item

    # =====================================================
    # SOURCE SELECTION
    # =====================================================

    def on_source_selection_changed(
        self
    ):

        item = (
            self.tree.currentItem()
        )

        self.source_panel = None

        if item is None:

            self.selected_source_label.setText(
                "No panel selected"
            )

            self.copy_button.setEnabled(
                False
            )

            return

        node_type = item.data(
            0,
            Qt.ItemDataRole.UserRole + 1
        )

        node_id = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if node_type != "PANEL":

            self.selected_source_label.setText(
                "Select a PANEL."
            )

            self.copy_button.setEnabled(
                False
            )

            return

        if node_id == self.target_panel_id:

            self.selected_source_label.setText(
                "The target panel cannot be "
                "used as its own source."
            )

            self.copy_button.setEnabled(
                False
            )

            return

        self.source_panel = (
            self.asset_manager
            .get_node(
                node_id
            )
        )

        if self.source_panel is None:

            self.selected_source_label.setText(
                "Unable to load selected panel."
            )

            self.copy_button.setEnabled(
                False
            )

            return

        # Build hierarchy name.

        hierarchy = []

        current = self.source_panel

        while current is not None:

            hierarchy.insert(
                0,
                str(
                    getattr(
                        current,
                        "name",
                        ""
                    )
                )
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

        self.selected_source_label.setText(
            "Source:\n"
            +
            "  /  ".join(
                hierarchy
            )
        )

        self.copy_button.setEnabled(
            True
        )

    # =====================================================
    # SELECT ALL
    # =====================================================

    def select_all_changed(
        self,
        state,
    ):

        checked = (
            state
            == Qt.CheckState.Checked.value
        )

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

    # =====================================================
    # GET SELECTED ATTRIBUTES
    # =====================================================

    def get_selected_attributes(
        self
    ):

        return [
            key

            for key, checkbox
            in self.checkboxes.items()

            if checkbox.isChecked()
        ]

    # =====================================================
    # ACCEPT
    # =====================================================

    def accept(
        self
    ):

        if self.source_panel is None:

            QMessageBox.warning(
                self,
                "No Source Panel",
                "Please select an existing panel first."
            )

            return

        selected = (
            self.get_selected_attributes()
        )

        if not selected:

            QMessageBox.warning(
                self,
                "Nothing Selected",
                "Select at least one configuration "
                "attribute to copy."
            )

            return

        super().accept()