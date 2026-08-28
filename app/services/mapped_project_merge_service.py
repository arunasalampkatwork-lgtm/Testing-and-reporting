from __future__ import annotations

import json
import shutil
import sqlite3
from pathlib import Path
from uuid import uuid4

from app.services.asset_library_manager import (
    AssetLibraryManager
)


class MappedProjectMergeService:
    """
    Executes the mapping produced by ProjectMergeDialog.

    The mapping is:
        source_node_id -> destination_node_id

    A mapped node itself is reused. Unmapped descendants are copied
    underneath the mapped destination node. If a descendant has an
    automatic physical-asset match in the destination project, the
    existing project node is reused.

    Components are merged after hierarchy mapping.
    Test rows are copied when their tables/columns exist and their
    foreign keys can be remapped.
    """

    def __init__(self, projects_directory=None):

        from app.config.settings import PROJECTS_DIR

        self.projects_directory = Path(
            projects_directory or PROJECTS_DIR
        )

        self.asset_library = AssetLibraryManager()

    # =========================================================
    # PUBLIC
    # =========================================================

    def merge(
        self,
        source_project_folder,
        destination_project_folder,
        mapping,
    ):

        source_project_folder = Path(
            source_project_folder
        )
        destination_project_folder = Path(
            destination_project_folder
        )

        mapping = {
            str(source): str(destination)
            for source, destination in (
                mapping or {}
            ).items()
        }

        if not mapping:
            raise ValueError(
                "No project mapping was supplied."
            )

        source_assets_file = (
            source_project_folder /
            "assets.json"
        )

        destination_assets_file = (
            destination_project_folder /
            "assets.json"
        )

        source_components_file = (
            source_project_folder /
            "components.json"
        )

        destination_components_file = (
            destination_project_folder /
            "components.json"
        )

        source_nodes = self._load_list(
            source_assets_file
        )

        destination_nodes = self._load_list(
            destination_assets_file
        )

        source_components = self._load_list(
            source_components_file
        )

        destination_components = self._load_list(
            destination_components_file
        )

        self.asset_library.load()

        # -----------------------------------------------------
        # Global physical asset mapping.
        # -----------------------------------------------------

        asset_map = self._merge_global_assets(
            source_nodes
        )

        # -----------------------------------------------------
        # Existing destination indexes.
        # -----------------------------------------------------

        destination_by_id = {
            str(node.get("node_id")): node
            for node in destination_nodes
            if node.get("node_id")
        }

        destination_by_asset = {
            str(node.get("asset_id")): node
            for node in destination_nodes
            if node.get("asset_id")
        }

        node_map = dict(mapping)

        # Validate supplied mappings.
        for source_id, destination_id in node_map.items():

            if source_id not in {
                str(node.get("node_id"))
                for node in source_nodes
            }:
                raise ValueError(
                    f"Mapped source node '{source_id}' "
                    "does not exist."
                )

            if destination_id not in destination_by_id:
                raise ValueError(
                    f"Mapped destination node '{destination_id}' "
                    "does not exist."
                )

        children = {}

        for node in source_nodes:
            children.setdefault(
                node.get("parent_id"),
                []
            ).append(node)

        created_nodes = 0
        reused_nodes = len(node_map)

        # -----------------------------------------------------
        # For every mapped source node, recursively copy its
        # descendants.
        # -----------------------------------------------------

        processed = set()

        def copy_children(
            source_parent_id,
            destination_parent_id
        ):

            nonlocal created_nodes, reused_nodes

            for source_node in children.get(
                source_parent_id,
                []
            ):

                source_id = str(
                    source_node.get(
                        "node_id"
                    )
                )

                if source_id in processed:
                    continue

                source_asset_id = source_node.get(
                    "asset_id"
                )

                mapped_asset_id = (
                    asset_map.get(
                        str(source_asset_id)
                    )
                    if source_asset_id
                    else None
                )

                existing = None

                if mapped_asset_id:
                    existing = destination_by_asset.get(
                        str(mapped_asset_id)
                    )

                if existing is None:
                    existing = self._find_child_match(
                        source_node,
                        destination_parent_id,
                        destination_nodes
                    )

                if existing is not None:

                    destination_id = str(
                        existing["node_id"]
                    )

                    node_map[source_id] = (
                        destination_id
                    )

                    processed.add(
                        source_id
                    )

                    reused_nodes += 1

                    copy_children(
                        source_id,
                        destination_id
                    )

                    continue

                destination_id = self._new_node_id()

                new_node = dict(
                    source_node
                )

                new_node["node_id"] = (
                    destination_id
                )

                new_node["parent_id"] = (
                    destination_parent_id
                )

                if mapped_asset_id:

                    new_node["asset_id"] = (
                        mapped_asset_id
                    )

                    if "linked_asset_id" in new_node:
                        new_node[
                            "linked_asset_id"
                        ] = mapped_asset_id

                destination_nodes.append(
                    new_node
                )

                destination_by_id[
                    destination_id
                ] = new_node

                if mapped_asset_id:
                    destination_by_asset[
                        str(mapped_asset_id)
                    ] = new_node

                node_map[source_id] = (
                    destination_id
                )

                processed.add(
                    source_id
                )

                created_nodes += 1

                copy_children(
                    source_id,
                    destination_id
                )

        # A mapped node may be anywhere in the hierarchy.
        for source_id, destination_id in list(
            node_map.items()
        ):
            copy_children(
                source_id,
                destination_id
            )

        self._save_list(
            destination_assets_file,
            destination_nodes
        )

        # -----------------------------------------------------
        # Components
        # -----------------------------------------------------

        component_map = self._merge_components(
            source_components,
            destination_components,
            node_map,
            destination_components_file
        )

        # -----------------------------------------------------
        # Tests
        # -----------------------------------------------------

        test_count = self._merge_tests(
            source_project_folder /
            "testing.db",
            destination_project_folder /
            "testing.db",
            node_map,
            component_map
        )

        # -----------------------------------------------------
        # Reports/artifacts
        # -----------------------------------------------------

        artifacts = self._copy_artifacts(
            source_project_folder,
            destination_project_folder
        )

        return {
            "nodes_created": created_nodes,
            "nodes_reused": reused_nodes,
            "components_created": len(
                component_map
            ),
            "tests_imported": test_count,
            "assets_merged": len(
                asset_map
            ),
            "artifacts_copied": artifacts,
        }

    # =========================================================
    # GLOBAL ASSETS
    # =========================================================

    def _merge_global_assets(
        self,
        source_nodes
    ):

        mapping = {}

        for node in source_nodes:

            source_asset_id = node.get(
                "asset_id"
            )

            if not source_asset_id:
                continue

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

            asset_tag = str(
                node.get(
                    "asset_tag",
                    node.get(
                        "name",
                        ""
                    )
                )
                or ""
            ).strip()

            if not asset_tag:
                asset_tag = str(
                    node.get(
                        "name",
                        ""
                    )
                ).strip()

            serial = str(
                node.get(
                    "serial_number",
                    ""
                )
                or ""
            ).strip()

            existing = (
                self.asset_library.find_duplicate(
                    asset_type=node_type,
                    asset_tag=asset_tag,
                    serial_number=serial
                )
            )

            if existing:

                destination_id = existing[
                    "asset_id"
                ]

            else:

                created = (
                    self.asset_library.create_asset(
                        asset_type=node_type,
                        asset_tag=asset_tag,
                        name=node.get(
                            "name",
                            ""
                        ),
                        serial_number=serial,
                        manufacturer=node.get(
                            "manufacturer",
                            ""
                        ),
                        model=node.get(
                            "model",
                            ""
                        ),
                        metadata=node.get(
                            "metadata",
                            {}
                        )
                    )
                )

                destination_id = created[
                    "asset_id"
                ]

            mapping[
                str(source_asset_id)
            ] = str(destination_id)

        self.asset_library.save()

        return mapping

    # =========================================================
    # COMPONENTS
    # =========================================================

    def _merge_components(
        self,
        source_components,
        destination_components,
        node_map,
        destination_file
    ):

        component_map = {}

        existing = {}

        for component in destination_components:

            panel_id = component.get(
                "panel_id"
            )

            key = self._component_key(
                component
            )

            existing[
                (
                    str(panel_id),
                    key
                )
            ] = component

        for source in source_components:

            source_panel_id = source.get(
                "panel_id"
            )

            destination_panel_id = node_map.get(
                str(source_panel_id)
            )

            if not destination_panel_id:
                continue

            key = self._component_key(
                source
            )

            existing_component = existing.get(
                (
                    str(destination_panel_id),
                    key
                )
            )

            if existing_component is not None:

                component_map[
                    str(
                        source.get(
                            "component_id"
                        )
                    )
                ] = str(
                    existing_component.get(
                        "component_id"
                    )
                )

                continue

            new_id = self._new_component_id()

            new_component = dict(
                source
            )

            new_component[
                "component_id"
            ] = new_id

            new_component[
                "panel_id"
            ] = destination_panel_id

            destination_components.append(
                new_component
            )

            existing[
                (
                    str(destination_panel_id),
                    key
                )
            ] = new_component

            component_map[
                str(
                    source.get(
                        "component_id"
                    )
                )
            ] = new_id

        self._save_list(
            destination_file,
            destination_components
        )

        return component_map

    @staticmethod
    def _component_key(
        component
    ):

        serial = str(
            component.get(
                "serial_number",
                ""
            )
            or ""
        ).strip().lower()

        if serial:
            return (
                "serial",
                serial
            )

        return (
            "name",
            str(
                component.get(
                    "name",
                    ""
                )
                or ""
            ).strip().lower(),
            str(
                component.get(
                    "component_type",
                    ""
                )
                or ""
            ).strip().upper()
        )

    # =========================================================
    # TEST DATABASE
    # =========================================================

    def _merge_tests(
        self,
        source_db,
        destination_db,
        node_map,
        component_map
    ):

        source_db = Path(source_db)
        destination_db = Path(destination_db)

        if not source_db.exists():
            return 0

        if not destination_db.exists():
            shutil.copy2(
                source_db,
                destination_db
            )
            return 0

        source = sqlite3.connect(
            source_db
        )
        destination = sqlite3.connect(
            destination_db
        )

        imported = 0

        try:

            tables = [
                row[0]
                for row in source.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' "
                    "AND name NOT LIKE 'sqlite_%'"
                ).fetchall()
            ]

            for table in tables:

                source_columns = self._columns(
                    source,
                    table
                )

                destination_columns = self._columns(
                    destination,
                    table
                )

                if not source_columns:
                    continue

                if not destination_columns:
                    continue

                rows = source.execute(
                    f'SELECT {",".join(self._quote(c) for c in source_columns)} '
                    f'FROM {self._quote(table)}'
                ).fetchall()

                for row in rows:

                    record = dict(
                        zip(
                            source_columns,
                            row
                        )
                    )

                    self._remap_record(
                        record,
                        node_map,
                        component_map
                    )

                    # Never reuse a conflicting primary key.
                    pk = self._primary_key(
                        source,
                        table
                    )

                    if pk and record.get(pk) is not None:

                        if self._exists(
                            destination,
                            table,
                            pk,
                            record[pk]
                        ):

                            record[
                                pk
                            ] = self._new_test_id()

                    usable = {
                        key: value
                        for key, value in record.items()
                        if key in destination_columns
                    }

                    if not usable:
                        continue

                    fields = list(
                        usable.keys()
                    )

                    placeholders = ",".join(
                        "?"
                        for _ in fields
                    )

                    try:

                        destination.execute(
                            f'INSERT INTO {self._quote(table)} '
                            f'({",".join(self._quote(f) for f in fields)}) '
                            f'VALUES ({placeholders})',
                            [
                                usable[field]
                                for field in fields
                            ]
                        )

                        imported += 1

                    except sqlite3.IntegrityError:
                        # A duplicate/invalid row should not destroy
                        # the rest of the import.
                        continue

            destination.commit()

        finally:

            source.close()
            destination.close()

        return imported

    @staticmethod
    def _remap_record(
        record,
        node_map,
        component_map
    ):

        for key in list(record.keys()):

            value = record[key]

            if value is None:
                continue

            key_lower = key.lower()

            if key_lower in (
                "panel_id",
                "node_id",
                "asset_node_id",
            ):

                record[key] = node_map.get(
                    str(value),
                    value
                )

            elif key_lower in (
                "component_id",
                "relay_id",
                "ct_id",
                "meter_id",
                "aux_relay_id",
            ):

                record[key] = component_map.get(
                    str(value),
                    value
                )

    # =========================================================
    # ARTIFACTS
    # =========================================================

    def _copy_artifacts(
        self,
        source,
        destination
    ):

        ignored = {
            "project.json",
            "assets.json",
            "components.json",
            "testing.db",
            "asset_links.json",
            "project_manifest.json",
        }

        artifact_root = (
            destination /
            "Imported" /
            self._safe_name(
                source.name
            )
        )

        count = 0

        for path in source.rglob("*"):

            if not path.is_file():
                continue

            relative = path.relative_to(
                source
            )

            if relative.name in ignored:
                continue

            if "__pycache__" in relative.parts:
                continue

            target = (
                artifact_root /
                relative
            )

            target.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            shutil.copy2(
                path,
                target
            )

            count += 1

        return count

    # =========================================================
    # MATCH
    # =========================================================

    @staticmethod
    def _find_child_match(
        source,
        destination_parent_id,
        destination_nodes
    ):

        source_type = str(
            source.get(
                "node_type",
                ""
            )
        ).upper()

        source_name = str(
            source.get(
                "name",
                ""
            )
            or ""
        ).strip().lower()

        source_tag = str(
            source.get(
                "asset_tag",
                ""
            )
            or ""
        ).strip().lower()

        for node in destination_nodes:

            if str(
                node.get(
                    "parent_id"
                )
            ) != str(
                destination_parent_id
            ):
                continue

            if str(
                node.get(
                    "node_type",
                    ""
                )
            ).upper() != source_type:
                continue

            node_name = str(
                node.get(
                    "name",
                    ""
                )
                or ""
            ).strip().lower()

            node_tag = str(
                node.get(
                    "asset_tag",
                    ""
                )
                or ""
            ).strip().lower()

            if source_tag and source_tag == node_tag:
                return node

            if source_name and source_name == node_name:
                return node

        return None

    # =========================================================
    # JSON
    # =========================================================

    @staticmethod
    def _load_list(
        path
    ):

        if not Path(path).exists():
            return []

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            return data.get(
                "assets",
                data.get(
                    "components",
                    []
                )
            )

        return []

    @staticmethod
    def _save_list(
        path,
        data
    ):

        Path(path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

    # =========================================================
    # SQLITE
    # =========================================================

    @staticmethod
    def _columns(
        connection,
        table
    ):

        return [
            row[1]
            for row in connection.execute(
                f"PRAGMA table_info({MappedProjectMergeService._quote(table)})"
            ).fetchall()
        ]

    @staticmethod
    def _primary_key(
        connection,
        table
    ):

        rows = connection.execute(
            f"PRAGMA table_info({MappedProjectMergeService._quote(table)})"
        ).fetchall()

        for row in rows:
            if row[5]:
                return row[1]

        return None

    @staticmethod
    def _exists(
        connection,
        table,
        column,
        value
    ):

        return (
            connection.execute(
                f"SELECT 1 FROM {MappedProjectMergeService._quote(table)} "
                f"WHERE {MappedProjectMergeService._quote(column)}=? LIMIT 1",
                (value,)
            ).fetchone()
            is not None
        )

    @staticmethod
    def _quote(
        identifier
    ):

        return '"' + str(
            identifier
        ).replace(
            '"',
            '""'
        ) + '"'

    # =========================================================
    # IDs
    # =========================================================

    @staticmethod
    def _new_node_id():

        return (
            f"AST-{uuid4().hex[:8].upper()}"
        )

    @staticmethod
    def _new_component_id():

        return (
            f"CMP-{uuid4().hex[:8].upper()}"
        )

    @staticmethod
    def _new_test_id():

        return (
            f"TEST-{uuid4().hex[:10].upper()}"
        )

    @staticmethod
    def _safe_name(
        value
    ):

        invalid = '<>:"/\\|?*'

        return "".join(
            "_"
            if char in invalid
            else char
            for char in str(value)
        ).strip() or "Imported_Project"
