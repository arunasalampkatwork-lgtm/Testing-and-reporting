from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QFrame,
    QLineEdit,
    QComboBox,
    QPushButton,
    QMessageBox,
    QSplitter,
    QFileDialog,
)

from app.services.asset_library_manager import (
    AssetLibraryManager
)

from app.services.asset_export_service import (
    AssetExportService
)


class AssetExplorerView(QWidget):

    """
    =========================================================
    GLOBAL ASSET EXPLORER
    =========================================================

    This view is completely project-independent.

    Hierarchy:

        Substation
            |
            +-- Switchboard
                    |
                    +-- Panel
                            |
                            +-- CT
                            +-- Numerical Relay
                            +-- Auxiliary Relay
                            +-- Meter

    The physical hierarchy is taken from the GLOBAL asset
    library using:

        metadata["parent_asset_id"]

    No project needs to be opened.
    """

    def __init__(
        self,
        global_asset_service=None,
        parent=None,
    ):

        super().__init__(parent)

        # =================================================
        # GLOBAL SERVICE
        # =================================================

        self.global_asset_service = (
            global_asset_service
        )

        # =================================================
        # GLOBAL ASSET LIBRARY
        #
        # Keep a direct AssetLibraryManager reference as a
        # fallback. This also makes the view usable even if
        # MainWindow does not pass a service.
        # =================================================

        self.asset_library = (
            AssetLibraryManager()
        )

        # =================================================
        # DATA
        # =================================================

        self.assets = []

        self.assets_by_id = {}

        self.tree_items = {}

        # =================================================
        # UI
        # =================================================

        self._build_ui()

        self.refresh()

    # =====================================================
    # BUILD UI
    # =====================================================

    def _build_ui(
        self
    ):

        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            12,
            12,
            12,
            12
        )

        root.setSpacing(
            10
        )

        # =================================================
        # TITLE
        # =================================================

        title = QLabel(
            "Asset Explorer"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 24px;
                font-weight: 700;
                padding: 4px;
            }
            """
        )

        root.addWidget(
            title
        )

        # =================================================
        # SUBTITLE
        # =================================================

        subtitle = QLabel(
            "Global physical asset hierarchy and configuration"
        )

        subtitle.setStyleSheet(
            """
            QLabel {
                color: #999999;
                padding-left: 4px;
                padding-bottom: 4px;
            }
            """
        )

        root.addWidget(
            subtitle
        )

        # =================================================
        # FILTER BAR
        # =================================================

        filter_row = QHBoxLayout()

        filter_row.setSpacing(
            8
        )

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        self.search_edit = QLineEdit()

        self.search_edit.setPlaceholderText(
            "Search asset, tag, manufacturer, model, component..."
        )

        self.search_edit.setClearButtonEnabled(
            True
        )

        filter_row.addWidget(
            self.search_edit,
            1
        )

        # -------------------------------------------------
        # TYPE FILTER
        # -------------------------------------------------

        self.type_filter = QComboBox()

        self.type_filter.addItems(
            [
                "All",
                "Substation",
                "Switchboard",
                "Panel",
                "Component",
            ]
        )

        filter_row.addWidget(
            self.type_filter
        )

        # -------------------------------------------------
        # REFRESH
        # -------------------------------------------------

        refresh_button = QPushButton(
            "Refresh"
        )

        refresh_button.clicked.connect(
            self.refresh
        )

        filter_row.addWidget(
            refresh_button
        )

        # -------------------------------------------------
        # EXPORT EXCEL
        # -------------------------------------------------

        self.export_button = QPushButton(
            "Export Excel"
        )

        self.export_button.setToolTip(
            "Export the complete global asset register to Excel"
        )

        self.export_button.clicked.connect(
            self.export_excel
        )

        filter_row.addWidget(
            self.export_button
        )

        root.addLayout(
            filter_row
        )

        # =================================================
        # MAIN SPLITTER
        # =================================================

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        splitter.setChildrenCollapsible(
            False
        )

        # =================================================
        # LEFT: ASSET TREE
        # =================================================

        self.tree = QTreeWidget()

        self.tree.setColumnCount(
            3
        )

        self.tree.setHeaderLabels(
            [
                "Asset",
                "Type",
                "Asset Tag",
            ]
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

        self.tree.setAlternatingRowColors(
            False
        )

        self.tree.setSelectionMode(
            QTreeWidget.SelectionMode.SingleSelection
        )

        self.tree.itemSelectionChanged.connect(
            self._selection_changed
        )

        splitter.addWidget(
            self.tree
        )

        # =================================================
        # RIGHT: DETAILS
        # =================================================

        self.details_frame = QFrame()

        self.details_frame.setObjectName(
            "ExplorerDetails"
        )

        self.details_layout = QVBoxLayout(
            self.details_frame
        )

        self.details_layout.setContentsMargins(
            18,
            18,
            18,
            18
        )

        self.details_layout.setSpacing(
            10
        )

        # -------------------------------------------------
        # DETAILS TITLE
        # -------------------------------------------------

        self.details_title = QLabel(
            "Select an asset"
        )

        self.details_title.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: 700;
            }
            """
        )

        self.details_layout.addWidget(
            self.details_title
        )

        # -------------------------------------------------
        # DETAILS SUBTITLE
        # -------------------------------------------------

        self.details_subtitle = QLabel(
            "Configuration will appear here."
        )

        self.details_subtitle.setStyleSheet(
            """
            QLabel {
                color: #999999;
            }
            """
        )

        self.details_subtitle.setWordWrap(
            True
        )

        self.details_layout.addWidget(
            self.details_subtitle
        )

        # -------------------------------------------------
        # DETAILS FORM
        # -------------------------------------------------

        self.details_content = QFormLayout()

        self.details_content.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight
        )

        self.details_content.setFormAlignment(
            Qt.AlignmentFlag.AlignTop
        )

        self.details_content.setSpacing(
            8
        )

        self.details_layout.addLayout(
            self.details_content
        )

        self.details_layout.addStretch()

        splitter.addWidget(
            self.details_frame
        )

        splitter.setSizes(
            [
                650,
                650,
            ]
        )

        root.addWidget(
            splitter,
            1
        )

        # =================================================
        # STYLE
        # =================================================

        self.setStyleSheet(
            """
            QLineEdit,
            QComboBox {
                min-height: 34px;
                padding: 5px 9px;
                border: 1px solid #444444;
                border-radius: 6px;
                background: #292929;
            }

            QLineEdit:focus,
            QComboBox:focus {
                border: 1px solid #e58a18;
            }

            QPushButton {
                min-height: 34px;
                padding: 5px 14px;
                border: 1px solid #444444;
                border-radius: 6px;
                background: #303030;
            }

            QPushButton:hover {
                background: #3a3a3a;
            }

            QPushButton:pressed {
                background: #252525;
            }

            QTreeWidget {
                background: #292929;
                border: 1px solid #3e3e3e;
                border-radius: 7px;
                padding: 4px;
            }

            QTreeWidget::item {
                height: 32px;
                padding: 3px 6px;
                border-radius: 4px;
            }

            QTreeWidget::item:hover {
                background: #353535;
            }

            QTreeWidget::item:selected {
                background: #3b3b3b;
                border-left: 3px solid #e58a18;
            }

            QHeaderView::section {
                background: #353535;
                padding: 7px;
                border: 0px;
                border-right: 1px solid #444444;
                font-weight: 600;
            }

            QFrame#ExplorerDetails {
                background: #242424;
                border: 1px solid #414141;
                border-radius: 8px;
            }

            QLabel#DetailLabel {
                color: #aaaaaa;
                font-weight: 600;
            }

            QLabel#DetailValue {
                color: #eeeeee;
            }
            """
        )

        # =================================================
        # SIGNALS
        # =================================================

        self.search_edit.textChanged.connect(
            self._apply_filter
        )

        self.type_filter.currentTextChanged.connect(
            self._apply_filter
        )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(
        self
    ):

        try:

            self._load_global_assets()

            self._populate_tree()

            self._clear_details()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Asset Explorer Error",
                f"Unable to load global assets:\n\n{error}"
            )

    # =====================================================
    # LOAD GLOBAL ASSETS
    # =====================================================

    def _load_global_assets(
        self
    ):

        assets = []

        # =================================================
        # FIRST TRY GLOBAL SERVICE
        # =================================================

        if self.global_asset_service is not None:

            try:

                if hasattr(
                    self.global_asset_service,
                    "refresh"
                ):

                    self.global_asset_service.refresh()

            except Exception:

                pass

            # -------------------------------------------------
            # get_all_assets()
            # -------------------------------------------------

            try:

                if hasattr(
                    self.global_asset_service,
                    "get_all_assets"
                ):

                    assets = (
                        self.global_asset_service
                        .get_all_assets()
                        or []
                    )

            except Exception:

                assets = []

            # -------------------------------------------------
            # get_assets()
            # -------------------------------------------------

            if not assets:

                try:

                    if hasattr(
                        self.global_asset_service,
                        "get_assets"
                    ):

                        assets = (
                            self.global_asset_service
                            .get_assets()
                            or []
                        )

                except Exception:

                    assets = []

        # =================================================
        # FALLBACK TO ASSET LIBRARY
        # =================================================

        if not assets:

            try:

                self.asset_library.load()

            except Exception:

                pass

            assets = (
                self.asset_library
                .get_all_assets()
                or []
            )

        # =================================================
        # NORMALIZE
        # =================================================

        normalized = {}

        for asset in assets:

            if not isinstance(
                asset,
                dict
            ):

                continue

            asset_id = (
                asset.get(
                    "asset_id"
                )
            )

            if not asset_id:

                continue

            asset_id = str(
                asset_id
            )

            asset_type = self._asset_type(
                asset
            )

            # -------------------------------------------------
            # Only physical assets belong in the hierarchy.
            # -------------------------------------------------

            if asset_type not in (
                "SUBSTATION",
                "SWITCHBOARD",
                "PANEL",
            ):

                continue

            # -------------------------------------------------
            # Avoid duplicate global records.
            # -------------------------------------------------

            if asset_id in normalized:

                continue

            normalized[
                asset_id
            ] = dict(
                asset
            )

        self.assets = list(
            normalized.values()
        )

        self.assets_by_id = (
            normalized
        )

    # =====================================================
    # POPULATE TREE
    # =====================================================

    def _populate_tree(
        self
    ):

        self.tree.blockSignals(
            True
        )

        try:

            self.tree.clear()

            self.tree_items.clear()

            # =================================================
            # PHYSICAL ASSET GROUPS
            # =================================================

            substations = []

            switchboards = []

            panels = []

            for asset in self.assets:

                asset_type = self._asset_type(
                    asset
                )

                if asset_type == "SUBSTATION":

                    substations.append(
                        asset
                    )

                elif asset_type == "SWITCHBOARD":

                    switchboards.append(
                        asset
                    )

                elif asset_type == "PANEL":

                    panels.append(
                        asset
                    )

            # =================================================
            # SUBSTATIONS
            # =================================================

            for substation in sorted(
                substations,
                key=lambda item:
                    self._display_name(
                        item
                    ).lower()
            ):

                substation_item = (
                    self._create_asset_item(
                        substation
                    )
                )

                self.tree.addTopLevelItem(
                    substation_item
                )

                # -------------------------------------------------
                # SWITCHBOARDS UNDER SUBSTATION
                # -------------------------------------------------

                substation_id = (
                    substation.get(
                        "asset_id"
                    )
                )

                child_switchboards = [

                    switchboard

                    for switchboard
                    in switchboards

                    if self._parent_id(
                        switchboard
                    )
                    == substation_id

                ]

                for switchboard in sorted(
                    child_switchboards,
                    key=lambda item:
                        self._display_name(
                            item
                        ).lower()
                ):

                    switchboard_item = (
                        self._create_asset_item(
                            switchboard
                        )
                    )

                    substation_item.addChild(
                        switchboard_item
                    )

                    # -------------------------------------------------
                    # PANELS UNDER SWITCHBOARD
                    # -------------------------------------------------

                    switchboard_id = (
                        switchboard.get(
                            "asset_id"
                        )
                    )

                    child_panels = [

                        panel

                        for panel
                        in panels

                        if self._parent_id(
                            panel
                        )
                        == switchboard_id

                    ]

                    for panel in sorted(
                        child_panels,
                        key=lambda item:
                            self._display_name(
                                item
                            ).lower()
                    ):

                        panel_item = (
                            self._create_asset_item(
                                panel
                            )
                        )

                        switchboard_item.addChild(
                            panel_item
                        )

                        # -------------------------------------------------
                        # COMPONENTS UNDER PANEL
                        # -------------------------------------------------

                        components = (
                            self._get_components(
                                panel
                            )
                        )

                        for component in sorted(
                            components,
                            key=lambda item:
                                str(
                                    item.get(
                                        "name",
                                        ""
                                    )
                                    or ""
                                ).lower()
                        ):

                            component_item = (
                                self._create_component_item(
                                    component,
                                    panel,
                                )
                            )

                            panel_item.addChild(
                                component_item
                            )

            # =================================================
            # ORPHAN SWITCHBOARDS
            #
            # If a switchboard has a missing/incorrect parent,
            # don't silently throw it away.
            # =================================================

            top_level_ids = {
                self._item_asset_id(
                    self.tree.topLevelItem(index)
                )
                for index in range(
                    self.tree.topLevelItemCount()
                )
            }

            for switchboard in sorted(
                switchboards,
                key=lambda item:
                    self._display_name(
                        item
                    ).lower()
            ):

                parent_id = (
                    self._parent_id(
                        switchboard
                    )
                )

                if (
                    parent_id
                    and
                    parent_id in self.assets_by_id
                ):

                    continue

                switchboard_id = (
                    switchboard.get(
                        "asset_id"
                    )
                )

                if switchboard_id in (
                    top_level_ids
                ):

                    continue

                item = (
                    self._create_asset_item(
                        switchboard
                    )
                )

                self.tree.addTopLevelItem(
                    item
                )

            # =================================================
            # ORPHAN PANELS
            # =================================================

            existing_asset_ids = set(
                self.tree_items.keys()
            )

            for panel in sorted(
                panels,
                key=lambda item:
                    self._display_name(
                        item
                    ).lower()
            ):

                panel_id = (
                    panel.get(
                        "asset_id"
                    )
                )

                if panel_id in existing_asset_ids:

                    continue

                item = (
                    self._create_asset_item(
                        panel
                    )
                )

                self.tree.addTopLevelItem(
                    item
                )

                components = (
                    self._get_components(
                        panel
                    )
                )

                for component in components:

                    component_item = (
                        self._create_component_item(
                            component,
                            panel,
                        )
                    )

                    item.addChild(
                        component_item
                    )

            # =================================================
            # IMPORTANT:
            #
            # EVERYTHING IS COLLAPSED BY DEFAULT.
            # =================================================

            self._collapse_all_items()

            # =================================================
            # COLUMN WIDTHS
            # =================================================

            self.tree.resizeColumnToContents(
                0
            )

            self.tree.setColumnWidth(
                0,
                max(
                    self.tree.columnWidth(0),
                    260,
                )
            )

            self.tree.setColumnWidth(
                1,
                150
            )

            self.tree.setColumnWidth(
                2,
                220
            )

        finally:

            self.tree.blockSignals(
                False
            )

    # =====================================================
    # CREATE ASSET ITEM
    # =====================================================

    def _create_asset_item(
        self,
        asset
    ):

        name = (
            self._display_name(
                asset
            )
        )

        asset_type = (
            self._pretty_type(
                self._asset_type(
                    asset
                )
            )
        )

        asset_tag = str(
            asset.get(
                "asset_tag",
                ""
            )
            or ""
        )

        item = QTreeWidgetItem(
            [
                name,
                asset_type,
                asset_tag,
            ]
        )

        item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            {
                "kind": "asset",
                "asset": asset,
            }
        )

        asset_id = asset.get(
            "asset_id"
        )

        if asset_id:

            self.tree_items[
                str(asset_id)
            ] = item

        return item

    # =====================================================
    # CREATE COMPONENT ITEM
    # =====================================================

    def _create_component_item(
        self,
        component,
        panel
    ):

        name = str(
            component.get(
                "name",
                ""
            )
            or "Component"
        )

        component_type = (
            self._pretty_type(
                component.get(
                    "component_type",
                    "COMPONENT"
                )
            )
        )

        item = QTreeWidgetItem(
            [
                name,
                component_type,
                "",
            ]
        )

        item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            {
                "kind": "component",
                "component": component,
                "panel": panel,
            }
        )

        component_id = (
            component.get(
                "component_id"
            )
        )

        if component_id:

            self.tree_items[
                str(component_id)
            ] = item

        return item

    # =====================================================
    # COMPONENTS FROM PANEL
    # =====================================================

    def _get_components(
        self,
        panel
    ):

        metadata = (
            panel.get(
                "metadata",
                {}
            )
            or {}
        )

        components = (
            metadata.get(
                "components",
                []
            )
            or []
        )

        if not isinstance(
            components,
            list
        ):

            return []

        return [
            component
            for component
            in components
            if isinstance(
                component,
                dict
            )
        ]

    # =====================================================
    # SELECTION
    # =====================================================

    def _selection_changed(
        self
    ):

        item = (
            self.tree.currentItem()
        )

        if item is None:

            self._clear_details()

            return

        data = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            data,
            dict
        ):

            self._clear_details()

            return

        kind = data.get(
            "kind"
        )

        if kind == "asset":

            asset = data.get(
                "asset"
            )

            self._show_asset_details(
                asset
            )

        elif kind == "component":

            component = data.get(
                "component"
            )

            panel = data.get(
                "panel"
            )

            self._show_component_details(
                component,
                panel
            )

    # =====================================================
    # ASSET DETAILS
    # =====================================================

    def _show_asset_details(
        self,
        asset
    ):

        if not isinstance(
            asset,
            dict
        ):

            self._clear_details()

            return

        self._clear_details()

        name = (
            self._display_name(
                asset
            )
        )

        asset_type = (
            self._pretty_type(
                self._asset_type(
                    asset
                )
            )
        )

        self.details_title.setText(
            name
        )

        self.details_subtitle.setText(
            asset_type
        )

        self._add_detail(
            "Asset ID",
            asset.get(
                "asset_id",
                ""
            )
        )

        self._add_detail(
            "Asset Tag",
            asset.get(
                "asset_tag",
                ""
            )
        )

        self._add_detail(
            "Manufacturer",
            asset.get(
                "manufacturer",
                ""
            )
        )

        self._add_detail(
            "Model",
            asset.get(
                "model",
                ""
            )
        )

        self._add_detail(
            "Serial Number",
            asset.get(
                "serial_number",
                ""
            )
        )

        # -------------------------------------------------
        # PANEL-SPECIFIC
        # -------------------------------------------------

        if self._asset_type(
            asset
        ) == "PANEL":

            self._add_detail(
                "Feed Equipment",
                asset.get(
                    "equipment_name",
                    ""
                )
            )

            self._add_detail(
                "Equipment Type",
                asset.get(
                    "equipment_type",
                    ""
                )
            )

            self._add_detail(
                "CT Count",
                asset.get(
                    "ct_count",
                    0
                )
            )

            self._add_detail(
                "Numerical Relays",
                asset.get(
                    "relay_count",
                    0
                )
            )

            self._add_detail(
                "Auxiliary Relays",
                asset.get(
                    "aux_count",
                    0
                )
            )

            components = (
                self._get_components(
                    asset
                )
            )

            self._add_detail(
                "Configured Components",
                len(
                    components
                )
            )

    # =====================================================
    # COMPONENT DETAILS
    # =====================================================

    def _show_component_details(
        self,
        component,
        panel=None
    ):

        if not isinstance(
            component,
            dict
        ):

            self._clear_details()

            return

        self._clear_details()

        component_name = str(
            component.get(
                "name",
                ""
            )
            or "Component"
        )

        component_type = (
            self._pretty_type(
                component.get(
                    "component_type",
                    ""
                )
            )
        )

        self.details_title.setText(
            component_name
        )

        self.details_subtitle.setText(
            component_type
        )

        # =================================================
        # COMMON
        # =================================================

        self._add_detail(
            "Component ID",
            component.get(
                "component_id",
                ""
            )
        )

        self._add_detail(
            "Manufacturer",
            component.get(
                "manufacturer",
                ""
            )
        )

        self._add_detail(
            "Model",
            component.get(
                "model",
                ""
            )
        )

        self._add_detail(
            "Serial Number",
            component.get(
                "serial_number",
                ""
            )
        )

        self._add_detail(
            "Description",
            component.get(
                "description",
                ""
            )
        )

        # =================================================
        # CT
        # =================================================

        normalized_type = (
            str(
                component.get(
                    "component_type",
                    ""
                )
                or ""
            )
            .strip()
            .upper()
        )

        if normalized_type in (
            "CT",
            "CURRENT TRANSFORMER",
        ):

            self._add_detail(
                "CT Primary",
                component.get(
                    "ct_primary",
                    ""
                )
            )

            self._add_detail(
                "CT Secondary",
                component.get(
                    "ct_secondary",
                    ""
                )
            )

            self._add_detail(
                "CT Ratio",
                component.get(
                    "ct_ratio",
                    ""
                )
            )

            self._add_detail(
                "CT Class",
                component.get(
                    "ct_class",
                    ""
                )
            )

            self._add_detail(
                "Rated Burden",
                component.get(
                    "burden",
                    ""
                )
            )

            self._add_detail(
                "Core",
                component.get(
                    "core",
                    ""
                )
            )

        # =================================================
        # NUMERICAL RELAY
        # =================================================

        if normalized_type == (
            "NUMERICAL_RELAY"
        ):

            self._add_detail(
                "VT Ratio",
                component.get(
                    "vt_ratio",
                    ""
                )
            )

            self._add_detail(
                "Firmware",
                component.get(
                    "firmware",
                    ""
                )
            )

            functions = (
                component.get(
                    "protection_functions",
                    []
                )
                or []
            )

            self._add_detail(
                "Protection Functions",
                self._list_to_text(
                    functions
                )
            )

        # =================================================
        # AUXILIARY RELAY
        # =================================================

        if normalized_type in (
            "AUXILIARY_RELAY",
            "AUX RELAY",
        ):

            self._add_detail(
                "Coil Voltage",
                component.get(
                    "coil_voltage",
                    ""
                )
            )

            self._add_detail(
                "Contact Configuration",
                component.get(
                    "contact_configuration",
                    ""
                )
            )

        # =================================================
        # METERS
        # =================================================

        if normalized_type in (
            "METER",
            "AMMETER",
            "VOLTMETER",
            "MULTIFUNCTION_METER",
        ):

            self._add_detail(
                "Meter Type",
                component.get(
                    "meter_type",
                    ""
                )
            )

            functions = (
                component.get(
                    "meter_functions",
                    []
                )
                or []
            )

            self._add_detail(
                "Meter Functions",
                self._list_to_text(
                    functions
                )
            )

            self._add_detail(
                "Accuracy Class",
                component.get(
                    "accuracy_class",
                    ""
                )
            )

    # =====================================================
    # ADD DETAIL
    # =====================================================

    def _add_detail(
        self,
        label,
        value
    ):

        label_widget = QLabel(
            str(
                label
            )
        )

        label_widget.setObjectName(
            "DetailLabel"
        )

        value_widget = QLabel(
            str(
                value
                if value not in (
                    None,
                    ""
                )
                else "-"
            )
        )

        value_widget.setObjectName(
            "DetailValue"
        )

        value_widget.setWordWrap(
            True
        )

        self.details_content.addRow(
            label_widget,
            value_widget
        )

    # =====================================================
    # CLEAR DETAILS
    # =====================================================

    def _clear_details(
        self
    ):

        while (
            self.details_content.rowCount()
            > 0
        ):

            self.details_content.removeRow(
                0
            )

        self.details_title.setText(
            "Select an asset"
        )

        self.details_subtitle.setText(
            "Configuration will appear here."
        )

    # =====================================================
    # FILTER
    # =====================================================

    def _apply_filter(
        self
    ):

        search_text = (
            self.search_edit
            .text()
            .strip()
            .lower()
        )

        selected_type = (
            self.type_filter
            .currentText()
            .strip()
            .upper()
        )

        # -------------------------------------------------
        # No filters
        # -------------------------------------------------

        if (
            not search_text
            and selected_type == "ALL"
        ):

            self._show_all_tree_items()

            self._collapse_all_items()

            return

        # -------------------------------------------------
        # Evaluate recursively
        # -------------------------------------------------

        for index in range(
            self.tree.topLevelItemCount()
        ):

            item = (
                self.tree.topLevelItem(
                    index
                )
            )

            self._filter_item(
                item,
                search_text,
                selected_type
            )

    # =====================================================
    # FILTER ITEM
    # =====================================================

    def _filter_item(
        self,
        item,
        search_text,
        selected_type
    ):

        data = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        own_match = (
            self._item_matches(
                item,
                data,
                search_text,
                selected_type
            )
        )

        child_match = False

        for index in range(
            item.childCount()
        ):

            child = (
                item.child(index)
            )

            if self._filter_item(
                child,
                search_text,
                selected_type
            ):

                child_match = True

        visible = (
            own_match
            or
            child_match
        )

        item.setHidden(
            not visible
        )

        # -------------------------------------------------
        # Expand only when filtering.
        # -------------------------------------------------

        if search_text or selected_type != "ALL":

            item.setExpanded(
                child_match
            )

        return visible

    # =====================================================
    # ITEM MATCH
    # =====================================================

    def _item_matches(
        self,
        item,
        data,
        search_text,
        selected_type
    ):

        if not isinstance(
            data,
            dict
        ):

            return False

        kind = data.get(
            "kind"
        )

        if kind == "asset":

            asset = data.get(
                "asset",
                {}
            )

            item_type = self._asset_type(
                asset
            )

            if (
                selected_type != "ALL"
                and
                selected_type
                != self._pretty_type(
                    item_type
                ).upper()
            ):

                return False

            searchable = " ".join(
                [
                    str(
                        asset.get(
                            "name",
                            ""
                        )
                        or ""
                    ),

                    str(
                        asset.get(
                            "asset_tag",
                            ""
                        )
                        or ""
                    ),

                    str(
                        asset.get(
                            "manufacturer",
                            ""
                        )
                        or ""
                    ),

                    str(
                        asset.get(
                            "model",
                            ""
                        )
                        or ""
                    ),

                    str(
                        asset.get(
                            "serial_number",
                            ""
                        )
                        or ""
                    ),
                ]
            ).lower()

        elif kind == "component":

            component = data.get(
                "component",
                {}
            )

            item_type = str(
                component.get(
                    "component_type",
                    ""
                )
                or ""
            ).upper()

            if (
                selected_type != "ALL"
                and
                selected_type != "COMPONENT"
            ):

                return False

            searchable = " ".join(
                [
                    str(
                        component.get(
                            "name",
                            ""
                        )
                        or ""
                    ),

                    item_type,

                    str(
                        component.get(
                            "manufacturer",
                            ""
                        )
                        or ""
                    ),

                    str(
                        component.get(
                            "model",
                            ""
                        )
                        or ""
                    ),

                    str(
                        component.get(
                            "serial_number",
                            ""
                        )
                        or ""
                    ),
                ]
            ).lower()

        else:

            return False

        if not search_text:

            return True

        return (
            search_text
            in searchable
        )

    # =====================================================
    # SHOW ALL ITEMS
    # =====================================================

    def _show_all_tree_items(
        self
    ):

        def show_item(
            item
        ):

            item.setHidden(
                False
            )

            for index in range(
                item.childCount()
            ):

                show_item(
                    item.child(index)
                )

        for index in range(
            self.tree.topLevelItemCount()
        ):

            show_item(
                self.tree.topLevelItem(
                    index
                )
            )

    # =====================================================
    # COLLAPSE EVERYTHING
    # =====================================================

    def _collapse_all_items(
        self
    ):

        def collapse_item(
            item
        ):

            item.setExpanded(
                False
            )

            for index in range(
                item.childCount()
            ):

                collapse_item(
                    item.child(index)
                )

        for index in range(
            self.tree.topLevelItemCount()
        ):

            collapse_item(
                self.tree.topLevelItem(
                    index
                )
            )

    # =====================================================
    # EXPORT EXCEL
    # =====================================================

    def export_excel(
        self
    ):

        default_name = (
            "Protection_Asset_Register.xlsx"
        )

        output_path, _ = (
            QFileDialog.getSaveFileName(
                self,
                "Export Global Asset Register",
                default_name,
                "Excel Workbook (*.xlsx)",
            )
        )

        if not output_path:

            return

        try:

            # -------------------------------------------------
            # Always reload the global library before export.
            # -------------------------------------------------

            try:

                self.asset_library.load()

            except Exception:

                pass

            exporter = (
                AssetExportService(
                    self.asset_library
                )
            )

            exporter.export_asset_register(
                output_path
            )

            QMessageBox.information(
                self,
                "Export Complete",
                "Global asset register exported successfully.\n\n"
                f"{output_path}",
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Excel Export Failed",
                f"Unable to export the asset register:\n\n"
                f"{error}",
            )

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _asset_type(
        asset
    ):

        return str(
            asset.get(
                "asset_type",
                ""
            )
            or ""
        ).strip().upper()

    @staticmethod
    def _display_name(
        asset
    ):

        return str(
            asset.get(
                "name",
                ""
            )
            or
            asset.get(
                "asset_tag",
                ""
            )
            or
            "Unnamed Asset"
        ).strip()

    @staticmethod
    def _parent_id(
        asset
    ):

        metadata = (
            asset.get(
                "metadata",
                {}
            )
            or {}
        )

        return metadata.get(
            "parent_asset_id"
        )

    @staticmethod
    def _pretty_type(
        value
    ):

        value = str(
            value
            or ""
        ).strip().upper()

        mapping = {

            "SUBSTATION":
                "Substation",

            "SWITCHBOARD":
                "Switchboard",

            "PANEL":
                "Panel",

            "NUMERICAL_RELAY":
                "Numerical Relay",

            "AUXILIARY_RELAY":
                "Auxiliary Relay",

            "AUX RELAY":
                "Auxiliary Relay",

            "CURRENT TRANSFORMER":
                "CT",

            "CT":
                "CT",

            "METER":
                "Meter",

            "AMMETER":
                "Ammeter",

            "VOLTMETER":
                "Voltmeter",

            "MULTIFUNCTION_METER":
                "Multifunction Meter",
        }

        return mapping.get(
            value,
            value.replace(
                "_",
                " "
            ).title()
        )

    @staticmethod
    def _list_to_text(
        value
    ):

        if isinstance(
            value,
            (list, tuple)
        ):

            return ", ".join(
                str(item)
                for item in value
            )

        if value is None:

            return ""

        return str(
            value
        )

    @staticmethod
    def _item_asset_id(
        item
    ):

        if item is None:

            return None

        data = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(
            data,
            dict
        ):

            return None

        asset = data.get(
            "asset"
        )

        if not isinstance(
            asset,
            dict
        ):

            return None

        return asset.get(
            "asset_id"
        )