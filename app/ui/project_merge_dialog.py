from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
    QMessageBox,
    QSplitter,
)


class MappingTree(QTreeWidget):
    node_dropped = Signal(object, object)

    def __init__(self, role, parent=None):
        super().__init__(parent)
        self.role = role
        self.setHeaderLabel(
            "Source Project" if role == "source"
            else "Destination Project"
        )
        self.setDragEnabled(role == "source")
        self.setAcceptDrops(role == "destination")
        self.setDropIndicatorShown(True)
        self.setDragDropMode(
            QTreeWidget.DragDropMode.InternalMove
            if role == "source"
            else QTreeWidget.DragDropMode.DropOnly
        )
        self.setSelectionMode(
            QTreeWidget.SelectionMode.SingleSelection
        )

    def dragMoveEvent(self, event):
        if self.role == "destination":
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if self.role != "destination":
            super().dropEvent(event)
            return

        item = self.itemAt(event.position().toPoint())
        if item is None:
            event.ignore()
            return

        source_tree = self.window().source_tree
        source_item = source_tree.currentItem()

        if source_item is None:
            event.ignore()
            return

        self.node_dropped.emit(
            source_item,
            item
        )
        event.acceptProposedAction()


class ProjectMergeDialog(QDialog):
    """
    Visual source/destination hierarchy mapper.

    Source nodes are draggable.
    Destination nodes accept drops.

    Only SUBSTATION, SWITCHBOARD and PANEL nodes are mapping targets.
    Components are handled automatically once their panel is mapped.
    """

    def __init__(
        self,
        source_nodes,
        destination_nodes,
        parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle(
            "Compare & Merge Project"
        )
        self.resize(1100, 700)

        self.source_nodes = source_nodes or []
        self.destination_nodes = destination_nodes or []

        self.mapping = {}

        self.source_by_id = {
            str(node.get("node_id")): node
            for node in self.source_nodes
            if node.get("node_id")
        }

        self.destination_by_id = {
            str(node.get("node_id")): node
            for node in self.destination_nodes
            if node.get("node_id")
        }

        self.source_items = {}
        self.destination_items = {}

        self._build_ui()
        self._populate_trees()
        self._auto_match()

    # =========================================================
    # UI
    # =========================================================

    def _build_ui(self):

        layout = QVBoxLayout(self)

        title = QLabel(
            "Compare Project Hierarchies"
        )
        title.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
            }
            """
        )
        layout.addWidget(title)

        info = QLabel(
            "Drag a substation, switchboard or panel from the "
            "left tree onto its destination on the right. "
            "Matching nodes are shown automatically."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        self.source_tree = MappingTree(
            "source",
            self
        )
        self.destination_tree = MappingTree(
            "destination",
            self
        )

        splitter.addWidget(
            self.source_tree
        )
        splitter.addWidget(
            self.destination_tree
        )

        splitter.setSizes(
            [550, 550]
        )

        layout.addWidget(splitter)

        self.status_label = QLabel(
            "No mappings"
        )
        layout.addWidget(
            self.status_label
        )

        buttons = QHBoxLayout()

        auto_button = QPushButton(
            "Auto Match"
        )
        clear_button = QPushButton(
            "Clear Mappings"
        )
        cancel_button = QPushButton(
            "Cancel"
        )
        merge_button = QPushButton(
            "Merge"
        )

        auto_button.clicked.connect(
            self._auto_match
        )
        clear_button.clicked.connect(
            self._clear_mappings
        )
        cancel_button.clicked.connect(
            self.reject
        )
        merge_button.clicked.connect(
            self._accept_merge
        )

        buttons.addWidget(
            auto_button
        )
        buttons.addWidget(
            clear_button
        )
        buttons.addStretch()
        buttons.addWidget(
            cancel_button
        )
        buttons.addWidget(
            merge_button
        )

        layout.addLayout(buttons)

        self.destination_tree.node_dropped.connect(
            self._map_nodes
        )

    # =========================================================
    # TREE
    # =========================================================

    def _populate_trees(self):

        self.source_tree.clear()
        self.destination_tree.clear()

        self.source_items.clear()
        self.destination_items.clear()

        self._build_tree(
            self.source_tree,
            self.source_nodes,
            self.source_items
        )

        self._build_tree(
            self.destination_tree,
            self.destination_nodes,
            self.destination_items
        )

        # Do not expand the whole hierarchy by default.
        self.source_tree.collapseAll()
        self.destination_tree.collapseAll()

    def _build_tree(
        self,
        tree,
        nodes,
        item_map
    ):

        children = {}

        for node in nodes:
            parent_id = node.get(
                "parent_id"
            )
            children.setdefault(
                parent_id,
                []
            ).append(node)

        def add_children(
            parent_item,
            parent_id
        ):

            for node in sorted(
                children.get(parent_id, []),
                key=lambda value: (
                    self._type_order(
                        value.get("node_type")
                    ),
                    str(
                        value.get(
                            "name",
                            ""
                        )
                    ).lower()
                )
            ):

                node_type = str(
                    node.get(
                        "node_type",
                        ""
                    )
                ).upper()

                item = QTreeWidgetItem(
                    [
                        f"[{node_type}] "
                        f"{node.get('name', '')}"
                    ]
                )

                item.setData(
                    0,
                    Qt.ItemDataRole.UserRole,
                    node.get("node_id")
                )

                item.setData(
                    0,
                    Qt.ItemDataRole.UserRole + 1,
                    node_type
                )

                item.setToolTip(
                    0,
                    self._node_tooltip(node)
                )

                if parent_item is None:
                    tree.addTopLevelItem(item)
                else:
                    parent_item.addChild(item)

                item_map[
                    str(node.get("node_id"))
                ] = item

                add_children(
                    item,
                    node.get("node_id")
                )

        add_children(
            None,
            None
        )

    @staticmethod
    def _type_order(node_type):

        order = {
            "SUBSTATION": 0,
            "SWITCHBOARD": 1,
            "PANEL": 2,
        }

        return order.get(
            str(node_type or "").upper(),
            99
        )

    @staticmethod
    def _node_tooltip(node):

        parts = [
            f"Name: {node.get('name', '')}",
            f"Type: {node.get('node_type', '')}",
        ]

        if node.get("asset_id"):
            parts.append(
                f"Asset ID: {node['asset_id']}"
            )

        return "\n".join(parts)

    # =========================================================
    # MATCHING
    # =========================================================

    def _auto_match(self):

        self.mapping.clear()

        destination_candidates = {}

        for node in self.destination_nodes:

            node_type = str(
                node.get(
                    "node_type",
                    ""
                )
            ).upper()

            if node_type not in (
                "SUBSTATION",
                "SWITCHBOARD",
                "PANEL",
            ):
                continue

            keys = self._match_keys(
                node
            )

            for key in keys:
                destination_candidates.setdefault(
                    (
                        node_type,
                        key
                    ),
                    []
                ).append(node)

        for source in self.source_nodes:

            source_type = str(
                source.get(
                    "node_type",
                    ""
                )
            ).upper()

            if source_type not in (
                "SUBSTATION",
                "SWITCHBOARD",
                "PANEL",
            ):
                continue

            target = None

            for key in self._match_keys(
                source
            ):

                candidates = destination_candidates.get(
                    (
                        source_type,
                        key
                    ),
                    []
                )

                if len(candidates) == 1:
                    target = candidates[0]
                    break

            if target is not None:
                self.mapping[
                    source["node_id"]
                ] = target["node_id"]

        self._refresh_visuals()

    @staticmethod
    def _match_keys(node):

        keys = []

        asset_id = str(
            node.get(
                "asset_id",
                ""
            )
            or ""
        ).strip().lower()

        name = str(
            node.get(
                "name",
                ""
            )
            or ""
        ).strip().lower()

        asset_tag = str(
            node.get(
                "asset_tag",
                ""
            )
            or ""
        ).strip().lower()

        if asset_id:
            keys.append(
                f"asset:{asset_id}"
            )

        if asset_tag:
            keys.append(
                f"tag:{asset_tag}"
            )

        if name:
            keys.append(
                f"name:{name}"
            )

        return keys

    # =========================================================
    # DRAG/DROP MAPPING
    # =========================================================

    def _map_nodes(
        self,
        source_item,
        destination_item
    ):

        source_id = source_item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        destination_id = destination_item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        source = self.source_by_id.get(
            str(source_id)
        )

        destination = self.destination_by_id.get(
            str(destination_id)
        )

        if source is None or destination is None:
            return

        source_type = str(
            source.get(
                "node_type",
                ""
            )
        ).upper()

        destination_type = str(
            destination.get(
                "node_type",
                ""
            )
        ).upper()

        if source_type != destination_type:

            QMessageBox.warning(
                self,
                "Invalid Mapping",
                "A node can only be mapped to a destination "
                "node of the same type."
            )
            return

        self.mapping[
            str(source_id)
        ] = str(destination_id)

        self._refresh_visuals()

    def _clear_mappings(self):

        self.mapping.clear()
        self._refresh_visuals()

    # =========================================================
    # VISUAL STATE
    # =========================================================

    def _refresh_visuals(self):

        for item in self.source_items.values():
            item.setText(
                0,
                self._base_item_text(
                    item,
                    self.source_by_id
                )
            )

        for item in self.destination_items.values():
            item.setText(
                0,
                self._base_item_text(
                    item,
                    self.destination_by_id
                )
            )

        mapped_destinations = set(
            self.mapping.values()
        )

        for source_id, destination_id in self.mapping.items():

            source_item = self.source_items.get(
                str(source_id)
            )
            destination_item = (
                self.destination_items.get(
                    str(destination_id)
                )
            )

            if source_item:
                source_item.setText(
                    0,
                    "✓ "
                    + self._base_item_text(
                        source_item,
                        self.source_by_id
                    )
                )

            if destination_item:
                destination_item.setText(
                    0,
                    "✓ "
                    + self._base_item_text(
                        destination_item,
                        self.destination_by_id
                    )
                )

        self.status_label.setText(
            f"{len(self.mapping)} node mapping(s)"
        )

    @staticmethod
    def _base_item_text(
        item,
        node_map
    ):

        node_id = item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        node = node_map.get(
            str(node_id),
            {}
        )

        return (
            f"[{str(node.get('node_type', '')).upper()}] "
            f"{node.get('name', '')}"
        )

    # =========================================================
    # ACCEPT
    # =========================================================

    def _accept_merge(self):

        if not self.mapping:

            QMessageBox.warning(
                self,
                "Nothing Mapped",
                "Map at least one source node to a destination node."
            )
            return

        self.accept()

    def get_mapping(self):

        return dict(
            self.mapping
        )
