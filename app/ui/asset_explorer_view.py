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
    QSplitter,
    QScrollArea,
)


class AssetExplorerView(QWidget):
    """
    GLOBAL ASSET EXPLORER

    This view is completely independent of the currently
    opened project.

    Hierarchy:

        Substation
            └── Switchboard
                    └── Panel
                            └── Components

    The explorer reads physical assets from GlobalAssetService.

    It does NOT use:
        - AssetManager
        - ComponentManager
        - current project
        - current project folder
    """

    def __init__(
        self,
        global_asset_service,
        parent=None,
    ):

        super().__init__(parent)

        self.global_asset_service = (
            global_asset_service
        )

        self._tree_nodes = {}

        self._all_assets = []

        self._build_ui()

        self.refresh()

    # =========================================================
    # UI
    # =========================================================

    def _build_ui(self):

        root = QVBoxLayout(
            self
        )

        root.setContentsMargins(
            16,
            16,
            16,
            16
        )

        root.setSpacing(
            12
        )

        # =====================================================
        # HEADER
        # =====================================================

        header = QLabel(
            "Asset Explorer"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 24px;
                font-weight: 700;
                padding: 4px 2px;
            }
            """
        )

        root.addWidget(
            header
        )

        subtitle = QLabel(
            "Global physical asset hierarchy"
        )

        subtitle.setStyleSheet(
            """
            QLabel {
                color: #999999;
                font-size: 13px;
                padding-left: 2px;
            }
            """
        )

        root.addWidget(
            subtitle
        )

        # =====================================================
        # SEARCH / FILTER
        # =====================================================

        filter_frame = QFrame()

        filter_frame.setObjectName(
            "FilterFrame"
        )

        filter_layout = QHBoxLayout(
            filter_frame
        )

        filter_layout.setContentsMargins(
            10,
            8,
            10,
            8
        )

        filter_layout.setSpacing(
            8
        )

        self.search_edit = QLineEdit()

        self.search_edit.setPlaceholderText(
            "Search substation, switchboard, panel, "
            "asset tag, manufacturer or model..."
        )

        self.search_edit.textChanged.connect(
            self.apply_filters
        )

        filter_layout.addWidget(
            self.search_edit,
            1
        )

        self.type_filter = QComboBox()

        self.type_filter.addItems(
            [
                "All Assets",
                "Substations",
                "Switchboards",
                "Panels",
                "Components",
            ]
        )

        self.type_filter.currentIndexChanged.connect(
            self.apply_filters
        )

        filter_layout.addWidget(
            self.type_filter
        )

        refresh_button = QPushButton(
            "Refresh"
        )

        refresh_button.clicked.connect(
            self.refresh
        )

        filter_layout.addWidget(
            refresh_button
        )

        root.addWidget(
            filter_frame
        )

        # =====================================================
        # SPLITTER
        # =====================================================

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        splitter.setChildrenCollapsible(
            False
        )

        # =====================================================
        # LEFT: GLOBAL ASSET TREE
        # =====================================================

        tree_frame = QFrame()

        tree_layout = QVBoxLayout(
            tree_frame
        )

        tree_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        tree_header = QLabel(
            "Asset Structure"
        )

        tree_header.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: 700;
                padding: 8px;
            }
            """
        )

        tree_layout.addWidget(
            tree_header
        )

        self.tree = QTreeWidget()

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

        self.tree.itemSelectionChanged.connect(
            self._selection_changed
        )

        tree_layout.addWidget(
            self.tree
        )

        splitter.addWidget(
            tree_frame
        )

        # =====================================================
        # RIGHT: DETAILS
        # =====================================================

        details_frame = QFrame()

        details_frame.setObjectName(
            "DetailsFrame"
        )

        details_outer = QVBoxLayout(
            details_frame
        )

        details_outer.setContentsMargins(
            0,
            0,
            0,
            0
        )

        # -----------------------------------------------------
        # DETAILS HEADER
        # -----------------------------------------------------

        self.details_title = QLabel(
            "Select an asset"
        )

        self.details_title.setStyleSheet(
            """
            QLabel {
                font-size: 21px;
                font-weight: 700;
                padding: 10px;
            }
            """
        )

        details_outer.addWidget(
            self.details_title
        )

        self.details_subtitle = QLabel(
            "Asset configuration will appear here."
        )

        self.details_subtitle.setStyleSheet(
            """
            QLabel {
                color: #999999;
                padding: 0 10px 10px 10px;
            }
            """
        )

        details_outer.addWidget(
            self.details_subtitle
        )

        # -----------------------------------------------------
        # SCROLL AREA
        # -----------------------------------------------------

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        self.details_container = QWidget()

        self.details_layout = QVBoxLayout(
            self.details_container
        )

        self.details_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        self.details_layout.setSpacing(
            10
        )

        scroll.setWidget(
            self.details_container
        )

        details_outer.addWidget(
            scroll
        )

        splitter.addWidget(
            details_frame
        )

        splitter.setStretchFactor(
            0,
            5
        )

        splitter.setStretchFactor(
            1,
            4
        )

        root.addWidget(
            splitter,
            1
        )

        # =====================================================
        # STYLE
        # =====================================================

        self.setStyleSheet(
            """
            QFrame#FilterFrame {
                background: #292929;
                border: 1px solid #404040;
                border-radius: 8px;
            }

            QFrame#DetailsFrame {
                background: #292929;
                border: 1px solid #404040;
                border-radius: 8px;
            }

            QTreeWidget {
                background: #242424;
                border: 1px solid #3d3d3d;
                border-radius: 7px;
                outline: none;
            }

            QTreeWidget::item {
                padding: 7px 5px;
                min-height: 28px;
            }

            QTreeWidget::item:hover {
                background: #333333;
            }

            QTreeWidget::item:selected {
                background: #3b3b3b;
                border-left: 3px solid #f39c12;
            }

            QLineEdit,
            QComboBox {
                min-height: 32px;
                padding: 4px 8px;
                border: 1px solid #444444;
                border-radius: 6px;
                background: #303030;
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

            QLabel#DetailSection {
                font-size: 15px;
                font-weight: 700;
                padding: 8px 4px;
                border-bottom: 1px solid #444444;
            }

            QLabel#DetailValue {
                padding: 7px 9px;
                background: #303030;
                border-radius: 5px;
                color: #eeeeee;
            }
            """
        )

    # =========================================================
    # REFRESH
    # =========================================================

    def refresh(self):

        try:

            service = (
                self.global_asset_service
            )

            # -------------------------------------------------
            # Let the service reload its backing data if it
            # supports refresh/load.
            # -------------------------------------------------

            if hasattr(
                service,
                "refresh"
            ):

                service.refresh()

            elif hasattr(
                service,
                "load"
            ):

                service.load()

            elif hasattr(
                service,
                "reload"
            ):

                service.reload()

            # -------------------------------------------------
            # Obtain global assets.
            # -------------------------------------------------

            assets = (
                self._get_global_assets()
            )

            self._all_assets = assets

            self.apply_filters()

        except Exception as error:

            self.tree.clear()

            self.details_title.setText(
                "Asset Explorer"
            )

            self.details_subtitle.setText(
                f"Unable to load global assets: {error}"
            )

    # =========================================================
    # GET GLOBAL ASSETS
    # =========================================================

    def _get_global_assets(self):

        service = self.global_asset_service

        assets_by_id = {}

        # =====================================================
        # GLOBAL ASSET DATA IS CURRENTLY EXPOSED THROUGH
        # get_all_nodes()
        #
        # Each project node points to its master physical
        # asset through node.asset_id.
        #
        # We use the GLOBAL asset record for configuration
        # and hierarchy information.
        # =====================================================

        try:

            records = (
                service.get_all_nodes()
                or []
            )

        except Exception:

            records = []

        for record in records:

            if not isinstance(
                record,
                dict
            ):
                continue

            node = record.get(
                "node"
            )

            manager = record.get(
                "asset_manager"
            )

            if node is None:

                continue

            node_type = str(
                getattr(
                    node,
                    "node_type",
                    ""
                )
                or ""
            ).strip().upper()

            # -------------------------------------------------
            # Only physical assets belong in the global
            # explorer hierarchy.
            # -------------------------------------------------

            if node_type not in (
                "SUBSTATION",
                "SWITCHBOARD",
                "PANEL",
            ):

                continue

            asset_id = getattr(
                node,
                "asset_id",
                None
            )

            if not asset_id:

                continue

            asset_id = str(
                asset_id
            )

            # -------------------------------------------------
            # Avoid duplicate physical assets when the same
            # global asset is referenced by multiple projects.
            # -------------------------------------------------

            if asset_id in assets_by_id:

                continue

            global_asset = None

            # -------------------------------------------------
            # Load the actual master asset record.
            # -------------------------------------------------

            try:

                if manager is not None:

                    library = getattr(
                        manager,
                        "asset_library",
                        None
                    )

                    if library is not None:

                        # Ensure latest configuration is visible.
                        try:

                            library.load()

                        except Exception:

                            pass

                        global_asset = (
                            library.get_asset(
                                asset_id
                            )
                        )

            except Exception:

                global_asset = None

            # -------------------------------------------------
            # If the master record cannot be loaded, create
            # a fallback record from the project node.
            # -------------------------------------------------

            if global_asset is None:

                global_asset = {
                    "asset_id":
                        asset_id,

                    "asset_type":
                        node_type,

                    "name":
                        getattr(
                            node,
                            "name",
                            ""
                        ),

                    "asset_tag":
                        getattr(
                            node,
                            "name",
                            ""
                        ),

                    "manufacturer":
                        getattr(
                            node,
                            "manufacturer",
                            ""
                        ),

                    "model":
                        getattr(
                            node,
                            "model",
                            ""
                        ),

                    "serial_number":
                        getattr(
                            node,
                            "serial_number",
                            ""
                        ),

                    "metadata":
                        {}
                }

            else:

                # Make a copy so we don't accidentally modify
                # the AssetLibrary's internal dictionary.

                global_asset = dict(
                    global_asset
                )

            # -------------------------------------------------
            # Ensure essential fields exist.
            # -------------------------------------------------

            global_asset[
                "asset_id"
            ] = asset_id

            global_asset[
                "asset_type"
            ] = (
                str(
                    global_asset.get(
                        "asset_type",
                        node_type
                    )
                    or node_type
                )
                .strip()
                .upper()
            )

            global_asset[
                "name"
            ] = (
                str(
                    global_asset.get(
                        "name",
                        ""
                    )
                    or getattr(
                        node,
                        "name",
                        ""
                    )
                )
                .strip()
            )

            global_asset[
                "asset_tag"
            ] = (
                str(
                    global_asset.get(
                        "asset_tag",
                        ""
                    )
                    or getattr(
                        node,
                        "name",
                        ""
                    )
                )
                .strip()
            )

            # -------------------------------------------------
            # Preserve project-node configuration as fallback.
            # -------------------------------------------------

            for field in (
                "manufacturer",
                "model",
                "serial_number",
                "equipment_name",
                "equipment_type",
                "ct_count",
                "relay_count",
                "aux_count",
                "meter_count",
            ):

                if (
                    field not in global_asset
                    or global_asset.get(
                        field
                    ) in (
                        None,
                        ""
                    )
                ):

                    global_asset[
                        field
                    ] = getattr(
                        node,
                        field,
                        ""
                    )

            # -------------------------------------------------
            # Metadata
            # -------------------------------------------------

            metadata = (
                global_asset.get(
                    "metadata",
                    {}
                )
                or {}
            )

            if not isinstance(
                metadata,
                dict
            ):

                metadata = {}

            global_asset[
                "metadata"
            ] = metadata

            assets_by_id[
                asset_id
            ] = global_asset

        # =====================================================
        # SECOND PASS
        #
        # Some global assets may exist in the AssetLibrary but
        # not currently be represented by a project node.
        #
        # Pull those directly from every AssetManager's
        # AssetLibrary as well.
        # =====================================================

        try:

            for project in (
                service.get_projects()
                or []
            ):

                manager = project.get(
                    "asset_manager"
                )

                if manager is None:
                    continue

                library = getattr(
                    manager,
                    "asset_library",
                    None
                )

                if library is None:
                    continue

                try:

                    library.load()

                except Exception:

                    pass

                try:

                    library_assets = (
                        library.get_all_assets()
                        or []
                    )

                except Exception:

                    library_assets = []

                for asset in library_assets:

                    if not isinstance(
                        asset,
                        dict
                    ):
                        continue

                    asset_type = str(
                        asset.get(
                            "asset_type",
                            ""
                        )
                        or ""
                    ).strip().upper()

                    if asset_type not in (
                        "SUBSTATION",
                        "SWITCHBOARD",
                        "PANEL",
                    ):

                        continue

                    asset_id = asset.get(
                        "asset_id"
                    )

                    if not asset_id:
                        continue

                    asset_id = str(
                        asset_id
                    )

                    if asset_id in assets_by_id:
                        continue

                    assets_by_id[
                        asset_id
                    ] = dict(
                        asset
                    )

        except Exception:

            pass

        return list(
            assets_by_id.values()
        )
    # =========================================================
    # NORMALISE ASSETS
    # =========================================================

    def _normalise_assets(
        self,
        assets
    ):

        if assets is None:
            return []

        # -----------------------------------------------------
        # Dictionary of assets
        # -----------------------------------------------------

        if isinstance(
            assets,
            dict
        ):

            # Common format:
            #
            # {
            #     asset_id: {...},
            #     asset_id: {...}
            # }

            values = list(
                assets.values()
            )

        else:

            try:

                values = list(
                    assets
                )

            except TypeError:

                return []

        normalised = []

        for asset in values:

            if isinstance(
                asset,
                dict
            ):

                item = dict(
                    asset
                )

            else:

                item = {
                    "asset_id":
                        getattr(
                            asset,
                            "asset_id",
                            getattr(
                                asset,
                                "node_id",
                                ""
                            )
                        ),

                    "asset_type":
                        getattr(
                            asset,
                            "asset_type",
                            getattr(
                                asset,
                                "node_type",
                                ""
                            )
                        ),

                    "name":
                        getattr(
                            asset,
                            "name",
                            ""
                        ),

                    "asset_tag":
                        getattr(
                            asset,
                            "asset_tag",
                            ""
                        ),

                    "serial_number":
                        getattr(
                            asset,
                            "serial_number",
                            ""
                        ),

                    "manufacturer":
                        getattr(
                            asset,
                            "manufacturer",
                            ""
                        ),

                    "model":
                        getattr(
                            asset,
                            "model",
                            ""
                        ),

                    "metadata":
                        getattr(
                            asset,
                            "metadata",
                            {}
                        ),
                }

            item["asset_type"] = str(
                item.get(
                    "asset_type",
                    item.get(
                        "node_type",
                        ""
                    )
                )
                or ""
            ).strip().upper()

            item["name"] = str(
                item.get(
                    "name",
                    ""
                )
                or ""
            ).strip()

            item["asset_tag"] = str(
                item.get(
                    "asset_tag",
                    ""
                )
                or ""
            ).strip()

            item["asset_id"] = str(
                item.get(
                    "asset_id",
                    ""
                )
                or ""
            ).strip()

            if not item["name"]:

                item["name"] = (
                    item["asset_tag"]
                    or item["asset_id"]
                    or "Unnamed Asset"
                )

            metadata = item.get(
                "metadata"
            )

            if not isinstance(
                metadata,
                dict
            ):

                metadata = {}

            item["metadata"] = metadata

            normalised.append(
                item
            )

        return normalised

    # =========================================================
    # FILTER
    # =========================================================

    def apply_filters(self):

        search_text = (
            self.search_edit
            .text()
            .strip()
            .lower()
        )

        selected_type = (
            self.type_filter
            .currentText()
        )

        self.tree.clear()

        self._tree_nodes = {}

        # -----------------------------------------------------
        # First determine which assets match.
        # -----------------------------------------------------

        assets = []

        for asset in self._all_assets:

            asset_type = str(
                asset.get(
                    "asset_type",
                    ""
                )
            ).upper()

            if selected_type == "Substations":

                if asset_type != "SUBSTATION":
                    continue

            elif selected_type == "Switchboards":

                if asset_type != "SWITCHBOARD":
                    continue

            elif selected_type == "Panels":

                if asset_type != "PANEL":
                    continue

            elif selected_type == "Components":

                # Components may be stored inside panel
                # metadata rather than as top-level assets.
                continue

            if search_text:

                searchable = " ".join(
                    [
                        str(
                            asset.get(
                                "name",
                                ""
                            )
                        ),
                        str(
                            asset.get(
                                "asset_tag",
                                ""
                            )
                        ),
                        str(
                            asset.get(
                                "manufacturer",
                                ""
                            )
                        ),
                        str(
                            asset.get(
                                "model",
                                ""
                            )
                        ),
                        str(
                            asset.get(
                                "serial_number",
                                ""
                            )
                        ),
                    ]
                ).lower()

                if search_text not in searchable:

                    continue

            assets.append(
                asset
            )

        # -----------------------------------------------------
        # If searching/filtering, preserve hierarchy by also
        # including parents of matching assets.
        # -----------------------------------------------------

        visible_ids = {
            asset.get("asset_id")
            for asset in assets
        }

        if search_text:

            changed = True

            while changed:

                changed = False

                for asset in self._all_assets:

                    asset_id = (
                        asset.get(
                            "asset_id"
                        )
                    )

                    if asset_id in visible_ids:
                        continue

                    parent_id = (
                        self._get_parent_asset_id(
                            asset
                        )
                    )

                    if parent_id in visible_ids:

                        visible_ids.add(
                            asset_id
                        )

                        changed = True

            assets = [
                asset
                for asset in self._all_assets
                if asset.get(
                    "asset_id"
                ) in visible_ids
            ]

        # -----------------------------------------------------
        # Build hierarchy.
        # -----------------------------------------------------

        self._populate_tree(
            assets
        )

    # =========================================================
    # POPULATE TREE
    # =========================================================

    def _populate_tree(
        self,
        assets
    ):

        by_id = {}

        for asset in assets:

            asset_id = (
                asset.get(
                    "asset_id"
                )
            )

            if asset_id:

                by_id[
                    asset_id
                ] = asset

        # -----------------------------------------------------
        # Root assets = substations
        # -----------------------------------------------------

        substations = [
            asset
            for asset in assets
            if str(
                asset.get(
                    "asset_type",
                    ""
                )
            ).upper()
            == "SUBSTATION"
        ]

        # Sort alphabetically.
        substations.sort(
            key=lambda item:
                str(
                    item.get(
                        "name",
                        ""
                    )
                ).lower()
        )

        for substation in substations:

            item = self._create_tree_item(
                substation
            )

            self.tree.addTopLevelItem(
                item
            )

            self._tree_nodes[
                item
            ] = substation

            self._add_children(
                item,
                substation,
                assets
            )

        # -----------------------------------------------------
        # Fallback for orphaned global assets.
        #
        # This is useful for old data created before the
        # parent_asset_id migration was completed.
        # -----------------------------------------------------

        displayed_ids = set()

        for item in self._tree_nodes.values():

            asset_id = (
                item.get(
                    "asset_id"
                )
            )

            if asset_id:
                displayed_ids.add(
                    asset_id
                )

        orphans = [
            asset
            for asset in assets
            if asset.get(
                "asset_id"
            ) not in displayed_ids
        ]

        orphans.sort(
            key=lambda item:
                (
                    str(
                        item.get(
                            "asset_type",
                            ""
                        )
                    ),
                    str(
                        item.get(
                            "name",
                            ""
                        )
                    ).lower()
                )
        )

        for asset in orphans:

            # Components are not global physical assets and
            # should not appear as root nodes.
            if str(
                asset.get(
                    "asset_type",
                    ""
                )
            ).upper() not in (
                "SUBSTATION",
                "SWITCHBOARD",
                "PANEL",
            ):

                continue

            item = self._create_tree_item(
                asset
            )

            self.tree.addTopLevelItem(
                item
            )

            self._tree_nodes[
                item
            ] = asset

            self._add_children(
                item,
                asset,
                assets
            )

        self.tree.expandToDepth(
            0
        )
        
        self._collapse_all_items()

    # =========================================================
    # ADD CHILDREN
    # =========================================================

    def _add_children(
        self,
        parent_item,
        parent_asset,
        assets
    ):

        parent_asset_id = (
            parent_asset.get(
                "asset_id"
            )
        )

        children = []

        for asset in assets:

            if asset.get(
                "asset_id"
            ) == parent_asset_id:

                continue

            child_parent_id = (
                self._get_parent_asset_id(
                    asset
                )
            )

            if child_parent_id == parent_asset_id:

                children.append(
                    asset
                )

        children.sort(
            key=lambda item:
                (
                    self._asset_type_order(
                        item.get(
                            "asset_type"
                        )
                    ),
                    str(
                        item.get(
                            "name",
                            ""
                        )
                    ).lower()
                )
        )

        for child in children:

            item = self._create_tree_item(
                child
            )

            parent_item.addChild(
                item
            )

            self._tree_nodes[
                item
            ] = child

            self._add_children(
                item,
                child,
                assets
            )

        # -----------------------------------------------------
        # Components stored in panel metadata
        # -----------------------------------------------------

        if str(
            parent_asset.get(
                "asset_type",
                ""
            )
        ).upper() == "PANEL":

            components = self._get_components(
                parent_asset
            )

            for component in components:

                item = self._create_component_item(
                    component
                )

                parent_item.addChild(
                    item
                )

                self._tree_nodes[
                    item
                ] = component

    # =========================================================
    # TREE ITEM
    # =========================================================

    def _create_tree_item(
        self,
        asset
    ):

        item = QTreeWidgetItem()

        item.setText(
            0,
            str(
                asset.get(
                    "name",
                    ""
                )
            )
        )

        item.setText(
            1,
            self._display_type(
                asset.get(
                    "asset_type",
                    ""
                )
            )
        )

        item.setText(
            2,
            str(
                asset.get(
                    "asset_tag",
                    ""
                )
            )
        )

        item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            asset
        )

        return item

    # =========================================================
    # COMPONENT ITEM
    # =========================================================

    def _create_component_item(
        self,
        component
    ):

        item = QTreeWidgetItem()

        name = str(
            component.get(
                "name",
                "Component"
            )
        )

        component_type = str(
            component.get(
                "component_type",
                ""
            )
        )

        item.setText(
            0,
            name
        )

        item.setText(
            1,
            self._display_type(
                component_type
            )
        )

        item.setText(
            2,
            str(
                component.get(
                    "serial_number",
                    ""
                )
            )
        )

        item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            component
        )

        return item

    # =========================================================
    # PARENT ASSET ID
    # =========================================================

    def _get_parent_asset_id(
        self,
        asset
    ):

        metadata = (
            asset.get(
                "metadata",
                {}
            )
            or {}
        )

        if isinstance(
            metadata,
            dict
        ):

            parent_id = (
                metadata.get(
                    "parent_asset_id"
                )
            )

            if parent_id:

                return str(
                    parent_id
                )

        # -----------------------------------------------------
        # Some versions may store it directly.
        # -----------------------------------------------------

        parent_id = asset.get(
            "parent_asset_id"
        )

        if parent_id:

            return str(
                parent_id
            )

        return None

    # =========================================================
    # COMPONENTS
    # =========================================================

    def _get_components(
        self,
        panel_asset
    ):

        metadata = (
            panel_asset.get(
                "metadata",
                {}
            )
            or {}
        )

        if not isinstance(
            metadata,
            dict
        ):

            return []

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
            item
            for item in components
            if isinstance(
                item,
                dict
            )
        ]

    # =========================================================
    # ASSET TYPE ORDER
    # =========================================================

    @staticmethod
    def _asset_type_order(
        asset_type
    ):

        asset_type = str(
            asset_type
            or ""
        ).upper()

        return {
            "SUBSTATION": 0,
            "SWITCHBOARD": 1,
            "PANEL": 2,
        }.get(
            asset_type,
            99
        )

    # =========================================================
    # DISPLAY TYPE
    # =========================================================

    @staticmethod
    def _display_type(
        asset_type
    ):

        value = str(
            asset_type
            or ""
        ).strip().upper()

        replacements = {
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

            "CURRENT_TRANSFORMER":
                "CT",

            "CURRENT TRANSFORMER":
                "CT",

            "CT":
                "CT",

            "METER":
                "Meter",
        }

        return replacements.get(
            value,
            value.replace(
                "_",
                " "
            ).title()
        )

    # =========================================================
    # SELECTION
    # =========================================================

    def _selection_changed(
        self
    ):

        selected = (
            self.tree.selectedItems()
        )

        if not selected:

            self._clear_details()

            return

        item = selected[0]

        data = (
            self._tree_nodes.get(
                item
            )
        )

        if data is None:

            data = item.data(
                0,
                Qt.ItemDataRole.UserRole
            )

        if data is None:

            self._clear_details()

            return

        self._show_details(
            data
        )

    # =========================================================
    # DETAILS
    # =========================================================

    def _show_details(
        self,
        data
    ):

        self._clear_detail_widgets()

        asset_type = str(
            data.get(
                "asset_type",
                data.get(
                    "component_type",
                    ""
                )
            )
            or ""
        ).upper()

        name = str(
            data.get(
                "name",
                ""
            )
            or ""
        )

        self.details_title.setText(
            name or "Asset"
        )

        self.details_subtitle.setText(
            self._display_type(
                asset_type
            )
        )

        # -----------------------------------------------------
        # COMPONENT
        # -----------------------------------------------------

        if asset_type not in (
            "SUBSTATION",
            "SWITCHBOARD",
            "PANEL",
        ):

            self._show_component_details(
                data
            )

            return

        # -----------------------------------------------------
        # PHYSICAL ASSET
        # -----------------------------------------------------

        fields = [
            (
                "Asset ID",
                data.get(
                    "asset_id",
                    ""
                )
            ),
            (
                "Asset Tag",
                data.get(
                    "asset_tag",
                    ""
                )
            ),
            (
                "Manufacturer",
                data.get(
                    "manufacturer",
                    ""
                )
            ),
            (
                "Model",
                data.get(
                    "model",
                    ""
                )
            ),
            (
                "Serial Number",
                data.get(
                    "serial_number",
                    ""
                )
            ),
        ]

        metadata = data.get(
            "metadata",
            {}
        )

        if not isinstance(
            metadata,
            dict
        ):

            metadata = {}

        # -----------------------------------------------------
        # PANEL CONFIGURATION
        # -----------------------------------------------------

        if asset_type == "PANEL":

            panel_configuration = (
                metadata.get(
                    "panel_configuration",
                    {}
                )
                or {}
            )

            if isinstance(
                panel_configuration,
                dict
            ):

                fields.extend(
                    [
                        (
                            "Feed Equipment",
                            panel_configuration.get(
                                "equipment_name",
                                data.get(
                                    "equipment_name",
                                    ""
                                )
                            )
                        ),
                        (
                            "Equipment Type",
                            panel_configuration.get(
                                "equipment_type",
                                data.get(
                                    "equipment_type",
                                    ""
                                )
                            )
                        ),
                        (
                            "Number of CTs",
                            panel_configuration.get(
                                "ct_count",
                                data.get(
                                    "ct_count",
                                    ""
                                )
                            )
                        ),
                        (
                            "Numerical Relays",
                            panel_configuration.get(
                                "relay_count",
                                data.get(
                                    "relay_count",
                                    ""
                                )
                            )
                        ),
                        (
                            "Auxiliary Relays",
                            panel_configuration.get(
                                "aux_count",
                                data.get(
                                    "aux_count",
                                    ""
                                )
                            )
                        ),
                        (
                            "Meters",
                            panel_configuration.get(
                                "meter_count",
                                data.get(
                                    "meter_count",
                                    ""
                                )
                            )
                        ),
                    ]
                )

        self._add_detail_section(
            "Asset Configuration"
        )

        for label, value in fields:

            self._add_detail_row(
                label,
                value
            )

        # -----------------------------------------------------
        # PANEL COMPONENTS
        # -----------------------------------------------------

        if asset_type == "PANEL":

            components = (
                self._get_components(
                    data
                )
            )

            self._add_detail_section(
                f"Components ({len(components)})"
            )

            if not components:

                self._add_detail_row(
                    "Status",
                    "No components configured"
                )

            else:

                for component in components:

                    component_name = (
                        component.get(
                            "name",
                            ""
                        )
                    )

                    component_type = (
                        component.get(
                            "component_type",
                            ""
                        )
                    )

                    self._add_detail_row(
                        component_name,
                        self._display_type(
                            component_type
                        )
                    )

        self.details_layout.addStretch()

    # =========================================================
    # COMPONENT DETAILS
    # =========================================================

    def _show_component_details(
        self,
        component
    ):

        self._add_detail_section(
            "Component Configuration"
        )

        fields = [
            (
                "Component ID",
                component.get(
                    "component_id",
                    ""
                )
            ),
            (
                "Component Type",
                self._display_type(
                    component.get(
                        "component_type",
                        ""
                    )
                )
            ),
            (
                "Manufacturer",
                component.get(
                    "manufacturer",
                    ""
                )
            ),
            (
                "Model",
                component.get(
                    "model",
                    ""
                )
            ),
            (
                "Serial Number",
                component.get(
                    "serial_number",
                    ""
                )
            ),
            (
                "Description",
                component.get(
                    "description",
                    ""
                )
            ),
        ]

        # -----------------------------------------------------
        # CT
        # -----------------------------------------------------

        if str(
            component.get(
                "component_type",
                ""
            )
        ).upper() in (
            "CT",
            "CURRENT_TRANSFORMER",
            "CURRENT TRANSFORMER",
        ):

            fields.extend(
                [
                    (
                        "CT Primary",
                        component.get(
                            "ct_primary",
                            ""
                        )
                    ),
                    (
                        "CT Secondary",
                        component.get(
                            "ct_secondary",
                            ""
                        )
                    ),
                    (
                        "CT Ratio",
                        component.get(
                            "ct_ratio",
                            ""
                        )
                    ),
                    (
                        "CT Class",
                        component.get(
                            "ct_class",
                            ""
                        )
                    ),
                    (
                        "Burden",
                        component.get(
                            "burden",
                            ""
                        )
                    ),
                    (
                        "Core",
                        component.get(
                            "core",
                            ""
                        )
                    ),
                ]
            )

        # -----------------------------------------------------
        # NUMERICAL RELAY
        # -----------------------------------------------------

        elif str(
            component.get(
                "component_type",
                ""
            )
        ).upper() == "NUMERICAL_RELAY":

            fields.extend(
                [
                    (
                        "VT Ratio",
                        component.get(
                            "vt_ratio",
                            ""
                        )
                    ),
                    (
                        "Firmware",
                        component.get(
                            "firmware",
                            ""
                        )
                    ),
                ]
            )

            functions = (
                component.get(
                    "protection_functions",
                    []
                )
                or []
            )

            if functions:

                fields.append(
                    (
                        "Protection Functions",
                        ", ".join(
                            str(function)
                            for function in functions
                        )
                    )
                )

        # -----------------------------------------------------
        # AUXILIARY RELAY
        # -----------------------------------------------------

        elif str(
            component.get(
                "component_type",
                ""
            )
        ).upper() in (
            "AUXILIARY_RELAY",
            "AUX RELAY",
        ):

            fields.extend(
                [
                    (
                        "Coil Voltage",
                        component.get(
                            "coil_voltage",
                            ""
                        )
                    ),
                    (
                        "Contact Configuration",
                        component.get(
                            "contact_configuration",
                            ""
                        )
                    ),
                ]
            )

        # -----------------------------------------------------
        # METER
        # -----------------------------------------------------

        elif str(
            component.get(
                "component_type",
                ""
            )
        ).upper() == "METER":

            fields.extend(
                [
                    (
                        "Meter Type",
                        component.get(
                            "meter_type",
                            ""
                        )
                    ),
                    (
                        "Accuracy Class",
                        component.get(
                            "accuracy_class",
                            ""
                        )
                    ),
                ]
            )

            meter_functions = (
                component.get(
                    "meter_functions",
                    []
                )
                or []
            )

            if meter_functions:

                fields.append(
                    (
                        "Meter Functions",
                        ", ".join(
                            str(function)
                            for function in meter_functions
                        )
                    )
                )

        for label, value in fields:

            self._add_detail_row(
                label,
                value
            )

        self.details_layout.addStretch()

    # =========================================================
    # DETAIL SECTION
    # =========================================================

    def _add_detail_section(
        self,
        title
    ):

        label = QLabel(
            title
        )

        label.setObjectName(
            "DetailSection"
        )

        self.details_layout.addWidget(
            label
        )

    # =========================================================
    # DETAIL ROW
    # =========================================================

    def _add_detail_row(
        self,
        label,
        value
    ):

        frame = QFrame()

        frame.setObjectName(
            "DetailRow"
        )

        layout = QFormLayout(
            frame
        )

        layout.setContentsMargins(
            4,
            3,
            4,
            3
        )

        label_widget = QLabel(
            str(
                label
            )
        )

        label_widget.setMinimumWidth(
            150
        )

        value_widget = QLabel(
            self._format_value(
                value
            )
        )

        value_widget.setObjectName(
            "DetailValue"
        )

        value_widget.setWordWrap(
            True
        )

        layout.addRow(
            label_widget,
            value_widget
        )

        self.details_layout.addWidget(
            frame
        )

    # =========================================================
    # FORMAT VALUE
    # =========================================================

    @staticmethod
    def _format_value(
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

            return "; ".join(
                f"{key}: {val}"
                for key, val in value.items()
            )

        return str(
            value
        )

    # =========================================================
    # CLEAR DETAILS
    # =========================================================

    def _clear_details(
        self
    ):

        self.details_title.setText(
            "Select an asset"
        )

        self.details_subtitle.setText(
            "Asset configuration will appear here."
        )

        self._clear_detail_widgets()

    # =========================================================
    # CLEAR DETAIL WIDGETS
    # =========================================================

    def _clear_detail_widgets(
        self
    ):

        while (
            self.details_layout.count()
        ):

            item = (
                self.details_layout
                .takeAt(0)
            )

            widget = (
                item.widget()
            )

            if widget is not None:

                widget.deleteLater()

    # =========================================================
    # EXPAND / COLLAPSE HELPERS
    # =========================================================

    def expand_all(
        self
    ):
        """
        Expand the complete asset hierarchy.
        """

        self.tree.expandAll()


    def collapse_all(
        self
    ):
        """
        Collapse the complete asset hierarchy.
        """

        self.tree.collapseAll()


    def _collapse_all_items(
        self
    ):
        """
        Force every item in the Asset Explorer to start collapsed.

        This recursively collapses every item after the hierarchy
        has been completely constructed.
        """

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