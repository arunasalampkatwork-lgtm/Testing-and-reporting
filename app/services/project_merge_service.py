from __future__ import annotations

import json
import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path
from uuid import uuid4

from app.config.settings import PROJECTS_DIR
from app.services.asset_library_manager import AssetLibraryManager


class ProjectMergeService:
    """
    Merge an exported .ptsproject into an existing project.

    The important distinction is:
        global asset = physical equipment
        project node = occurrence of that equipment in a project

    Therefore the merge:
      1. merges/reuses global physical assets;
      2. maps imported hierarchy onto an existing
         SUBSTATION / SWITCHBOARD / PANEL;
      3. creates only missing child nodes;
      4. creates new component IDs where necessary;
      5. imports test records with the destination project ID;
      6. preserves imported reports/other files under an
         Imported/<source project>/ folder.

    target_node_id is a node in the destination project's assets.json.
    The imported node matching the target type is treated as the
    corresponding existing physical asset. Its children are merged
    beneath the target.
    """

    MANIFEST_NAME = "project_manifest.json"

    def __init__(self, projects_directory: Path | None = None):
        self.projects_directory = Path(
            projects_directory or PROJECTS_DIR
        )
        self.projects_directory.mkdir(
            parents=True,
            exist_ok=True
        )
        self.asset_library = AssetLibraryManager()

    # =========================================================
    # PUBLIC API
    # =========================================================

    def merge_project(
        self,
        archive_file: Path,
        destination_project_folder: Path,
        target_node_id: str,
    ) -> dict:

        archive_file = Path(archive_file)
        destination_project_folder = Path(
            destination_project_folder
        )

        if not archive_file.exists():
            raise ValueError(
                "The selected project archive does not exist."
            )

        if not destination_project_folder.exists():
            raise ValueError(
                "The destination project does not exist."
            )

        if not target_node_id:
            raise ValueError(
                "Please select a destination substation, "
                "switchboard or panel."
            )

        with tempfile.TemporaryDirectory(
            prefix="pts_merge_"
        ) as temp_dir:

            temp_root = Path(temp_dir)

            self._safe_extract(
                archive_file,
                temp_root
            )

            manifest = self._load_manifest(
                temp_root
            )

            imported_project = manifest.get(
                "project",
                {}
            )

            source_title = str(
                imported_project.get(
                    "title",
                    "Imported Project"
                )
                or "Imported Project"
            ).strip()

            # -------------------------------------------------
            # First merge the global physical assets.
            # -------------------------------------------------

            asset_id_map = self._merge_global_assets(
                manifest.get(
                    "global_assets",
                    []
                )
            )

            # -------------------------------------------------
            # Merge hierarchy.
            # -------------------------------------------------

            node_map, merge_stats = (
                self._merge_asset_nodes(
                    imported_assets_file=(
                        temp_root / "assets.json"
                    ),
                    destination_project_folder=(
                        destination_project_folder
                    ),
                    target_node_id=target_node_id,
                    asset_id_map=asset_id_map
                )
            )

            # -------------------------------------------------
            # Merge components and remap component IDs.
            # -------------------------------------------------

            component_id_map = (
                self._merge_components(
                    imported_components_file=(
                        temp_root / "components.json"
                    ),
                    destination_project_folder=(
                        destination_project_folder
                    ),
                    node_map=node_map
                )
            )

            # -------------------------------------------------
            # Merge testing database.
            # -------------------------------------------------

            destination_project_id = (
                self._get_project_id(
                    destination_project_folder
                )
            )

            test_stats = self._merge_testing_database(
                imported_database=(
                    temp_root / "testing.db"
                ),
                destination_database=(
                    destination_project_folder /
                    "testing.db"
                ),
                destination_project_id=destination_project_id,
                node_map=node_map,
                component_id_map=component_id_map
            )

            # -------------------------------------------------
            # Preserve reports and other project artifacts.
            # -------------------------------------------------

            copied_files = self._copy_non_data_files(
                temp_root,
                destination_project_folder,
                source_title
            )

        return {
            "source_project": source_title,
            "destination_project": (
                destination_project_folder.name
            ),
            "nodes_created": merge_stats[
                "nodes_created"
            ],
            "nodes_reused": merge_stats[
                "nodes_reused"
            ],
            "components_created": len(
                component_id_map
            ),
            "tests_imported": (
                test_stats["tests_imported"]
            ),
            "test_rows_skipped": (
                test_stats["rows_skipped"]
            ),
            "assets_merged": len(
                asset_id_map
            ),
            "artifacts_copied": copied_files,
        }

    # =========================================================
    # MANIFEST
    # =========================================================

    def _load_manifest(
        self,
        temp_root: Path
    ) -> dict:

        manifest_file = (
            temp_root /
            self.MANIFEST_NAME
        )

        if not manifest_file.exists():
            raise ValueError(
                "The selected file is not a valid "
                "Protection Testing Suite project archive."
            )

        try:
            with open(
                manifest_file,
                "r",
                encoding="utf-8"
            ) as file:
                manifest = json.load(file)
        except Exception as error:
            raise ValueError(
                f"Could not read project manifest:\n{error}"
            ) from error

        if manifest.get(
            "format"
        ) != "ProtectionTestingSuiteProject":
            raise ValueError(
                "This archive was not created by "
                "Protection Testing Suite."
            )

        return manifest

    # =========================================================
    # GLOBAL ASSETS
    # =========================================================

    def _merge_global_assets(
        self,
        imported_assets
    ) -> dict[str, str]:

        self.asset_library.load()

        mapping = {}

        for source in imported_assets or []:

            if not isinstance(source, dict):
                continue

            source_id = source.get(
                "asset_id"
            )

            if not source_id:
                continue

            asset_type = str(
                source.get(
                    "asset_type",
                    ""
                )
                or ""
            ).strip().upper()

            asset_tag = str(
                source.get(
                    "asset_tag",
                    source.get(
                        "name",
                        ""
                    )
                )
                or ""
            ).strip()

            serial = str(
                source.get(
                    "serial_number",
                    ""
                )
                or ""
            ).strip()

            if not asset_type or not asset_tag:
                continue

            existing = (
                self.asset_library.find_duplicate(
                    asset_type=asset_type,
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
                        asset_type=asset_type,
                        asset_tag=asset_tag,
                        name=source.get(
                            "name",
                            ""
                        ),
                        description=source.get(
                            "description",
                            ""
                        ),
                        serial_number=serial,
                        manufacturer=source.get(
                            "manufacturer",
                            ""
                        ),
                        model=source.get(
                            "model",
                            ""
                        ),
                        metadata=source.get(
                            "metadata",
                            {}
                        )
                    )
                )
                destination_id = created[
                    "asset_id"
                ]

            mapping[
                str(source_id)
            ] = str(destination_id)

        self.asset_library.save()

        return mapping

    # =========================================================
    # ASSET HIERARCHY
    # =========================================================

    def _merge_asset_nodes(
        self,
        imported_assets_file: Path,
        destination_project_folder: Path,
        target_node_id: str,
        asset_id_map: dict[str, str]
    ) -> tuple[dict[str, str], dict]:

        if not imported_assets_file.exists():
            raise ValueError(
                "The project archive does not contain assets.json."
            )

        imported_nodes = self._load_json_list(
            imported_assets_file
        )

        destination_file = (
            destination_project_folder /
            "assets.json"
        )

        destination_nodes = (
            self._load_json_list(
                destination_file
            )
            if destination_file.exists()
            else []
        )

        target = next(
            (
                node for node in destination_nodes
                if node.get("node_id")
                == target_node_id
            ),
            None
        )

        if target is None:
            raise ValueError(
                "The selected destination asset could not be found."
            )

        target_type = str(
            target.get(
                "node_type",
                ""
            )
            or ""
        ).strip().upper()

        if target_type not in (
            "SUBSTATION",
            "SWITCHBOARD",
            "PANEL",
        ):
            raise ValueError(
                "Merge target must be a substation, "
                "switchboard or panel."
            )

        roots = [
            node for node in imported_nodes
            if node.get("parent_id") is None
        ]

        if not roots:
            raise ValueError(
                "The imported project contains no asset hierarchy."
            )

        # Map the imported node representing the selected
        # hierarchy level onto the existing target.
        merge_root = self._find_import_root_for_target(
            imported_nodes,
            roots,
            target_type
        )

        if merge_root is None:
            raise ValueError(
                f"The imported project does not contain a "
                f"{target_type.replace('_', ' ').title()} "
                "that can be merged into the selected target."
            )

        node_map = {
            merge_root["node_id"]: target_node_id
        }

        # -----------------------------------------------------
        # Existing physical assets in destination project.
        # -----------------------------------------------------

        existing_by_asset_id = {
            str(node.get("asset_id")): node
            for node in destination_nodes
            if node.get("asset_id")
        }

        # Merge descendants recursively.
        created = 0
        reused = 1

        children_by_parent = {}

        for node in imported_nodes:
            parent = node.get("parent_id")
            children_by_parent.setdefault(
                parent,
                []
            ).append(node)

        def merge_children(
            source_parent_id: str,
            destination_parent_id: str
        ):
            nonlocal created, reused

            for source_node in children_by_parent.get(
                source_parent_id,
                []
            ):

                source_id = source_node.get(
                    "node_id"
                )

                if not source_id:
                    continue

                source_asset_id = source_node.get(
                    "asset_id"
                )

                mapped_asset_id = (
                    asset_id_map.get(
                        str(source_asset_id)
                    )
                    if source_asset_id
                    else None
                )

                destination_node = None

                # First preference: same physical asset already
                # exists in the destination project.
                if mapped_asset_id:
                    destination_node = (
                        existing_by_asset_id.get(
                            str(mapped_asset_id)
                        )
                    )

                # Second preference: same node type/name under
                # the same parent.
                if destination_node is None:
                    source_type = str(
                        source_node.get(
                            "node_type",
                            ""
                        )
                    ).upper()

                    source_name = str(
                        source_node.get(
                            "name",
                            ""
                        )
                    ).strip().lower()

                    destination_node = next(
                        (
                            node
                            for node in destination_nodes
                            if node.get(
                                "parent_id"
                            ) == destination_parent_id
                            and str(
                                node.get(
                                    "node_type",
                                    ""
                                )
                            ).upper() == source_type
                            and str(
                                node.get(
                                    "name",
                                    ""
                                )
                            ).strip().lower()
                            == source_name
                        ),
                        None
                    )

                if destination_node is not None:
                    destination_id = (
                        destination_node["node_id"]
                    )
                    node_map[source_id] = destination_id
                    reused += 1

                    merge_children(
                        source_id,
                        destination_id
                    )
                    continue

                destination_id = (
                    self._new_node_id()
                )

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

                node_map[source_id] = destination_id

                if mapped_asset_id:
                    existing_by_asset_id[
                        str(mapped_asset_id)
                    ] = new_node

                created += 1

                merge_children(
                    source_id,
                    destination_id
                )

        merge_children(
            merge_root["node_id"],
            target_node_id
        )

        # -----------------------------------------------------
        # Persist.
        # -----------------------------------------------------

        destination_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            destination_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                destination_nodes,
                file,
                indent=4,
                ensure_ascii=False
            )

        return node_map, {
            "nodes_created": created,
            "nodes_reused": reused,
        }

    @staticmethod
    def _find_import_root_for_target(
        imported_nodes,
        roots,
        target_type
    ):
        # Exact root match first.
        exact = [
            node for node in roots
            if str(
                node.get(
                    "node_type",
                    ""
                )
            ).upper() == target_type
        ]

        if len(exact) == 1:
            return exact[0]

        if len(exact) > 1:
            # Prefer the one whose name is most representative
            # only when there is a single obvious name.
            # Otherwise require a deterministic first root.
            return exact[0]

        # An exported project may have a SUBSTATION root while
        # the user wants to merge directly into a SWITCHBOARD
        # or PANEL. Find the first node of that type.
        candidates = [
            node for node in imported_nodes
            if str(
                node.get(
                    "node_type",
                    ""
                )
            ).upper() == target_type
        ]

        if candidates:
            return candidates[0]

        return None

    # =========================================================
    # COMPONENTS
    # =========================================================

    def _merge_components(
        self,
        imported_components_file: Path,
        destination_project_folder: Path,
        node_map: dict[str, str]
    ) -> dict[str, str]:

        if not imported_components_file.exists():
            return {}

        imported_components = self._load_json_list(
            imported_components_file
        )

        destination_file = (
            destination_project_folder /
            "components.json"
        )

        destination_components = (
            self._load_json_list(
                destination_file
            )
            if destination_file.exists()
            else []
        )

        component_map = {}

        # Build destination lookup for sensible reuse.
        lookup = {}

        for component in destination_components:
            key = self._component_key(
                component
            )
            panel_id = component.get(
                "panel_id"
            )
            lookup[
                (
                    panel_id,
                    key
                )
            ] = component

        for source in imported_components:

            source_id = source.get(
                "component_id"
            )

            source_panel = source.get(
                "panel_id"
            )

            destination_panel = node_map.get(
                source_panel
            )

            if not source_id or not destination_panel:
                continue

            key = self._component_key(
                source
            )

            existing = lookup.get(
                (
                    destination_panel,
                    key
                )
            )

            if existing is not None:
                component_map[
                    source_id
                ] = existing[
                    "component_id"
                ]
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
            ] = destination_panel

            destination_components.append(
                new_component
            )

            lookup[
                (
                    destination_panel,
                    key
                )
            ] = new_component

            component_map[
                source_id
            ] = new_id

        destination_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            destination_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                destination_components,
                file,
                indent=4,
                ensure_ascii=False
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

    def _merge_testing_database(
        self,
        imported_database: Path,
        destination_database: Path,
        destination_project_id: str,
        node_map: dict[str, str],
        component_id_map: dict[str, str]
    ) -> dict:

        if not imported_database.exists():
            return {
                "tests_imported": 0,
                "rows_skipped": 0,
            }

        if not destination_database.exists():
            destination_database.parent.mkdir(
                parents=True,
                exist_ok=True
            )
            shutil.copy2(
                imported_database,
                destination_database
            )
            return {
                "tests_imported": (
                    self._count_database_rows(
                        destination_database
                    )
                ),
                "rows_skipped": 0,
            }

        imported = sqlite3.connect(
            imported_database
        )
        destination = sqlite3.connect(
            destination_database
        )

        tests_imported = 0
        rows_skipped = 0

        try:
            self._ensure_tables_from_import(
                imported,
                destination
            )

            for table in (
                "protection_tests",
                "component_tests",
            ):

                if not self._table_exists(
                    imported,
                    table
                ):
                    continue

                if not self._table_exists(
                    destination,
                    table
                ):
                    continue

                columns = self._table_columns(
                    imported,
                    table
                )

                rows = imported.execute(
                    f'SELECT {",".join(self._quote(c) for c in columns)} '
                    f'FROM {self._quote(table)}'
                ).fetchall()

                destination_columns = set(
                    self._table_columns(
                        destination,
                        table
                    )
                )

                for row in rows:

                    record = dict(
                        zip(
                            columns,
                            row
                        )
                    )

                    record["project_id"] = (
                        destination_project_id
                    )

                    if "panel_id" in record:
                        record["panel_id"] = (
                            node_map.get(
                                record["panel_id"],
                                record["panel_id"]
                            )
                        )

                    if table == "protection_tests":
                        if "relay_id" in record:
                            record["relay_id"] = (
                                component_id_map.get(
                                    record["relay_id"],
                                    record["relay_id"]
                                )
                            )

                    if table == "component_tests":
                        if "component_id" in record:
                            record["component_id"] = (
                                component_id_map.get(
                                    record["component_id"],
                                    record["component_id"]
                                )
                            )

                    # A test_id is the primary key. Never destroy
                    # an existing test because two projects happened
                    # to use the same generated ID.
                    if "test_id" in record:
                        test_id = record["test_id"]

                        if self._row_exists(
                            destination,
                            table,
                            "test_id",
                            test_id
                        ):
                            record[
                                "test_id"
                            ] = self._new_test_id(
                                table
                            )

                    usable = {
                        key: value
                        for key, value in record.items()
                        if key in destination_columns
                    }

                    if not usable:
                        rows_skipped += 1
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
                            f'({",".join(self._quote(c) for c in fields)}) '
                            f'VALUES ({placeholders})',
                            [
                                usable[field]
                                for field in fields
                            ]
                        )
                        tests_imported += 1
                    except sqlite3.IntegrityError:
                        rows_skipped += 1

            destination.commit()

        finally:
            imported.close()
            destination.close()

        return {
            "tests_imported": tests_imported,
            "rows_skipped": rows_skipped,
        }

    @staticmethod
    def _ensure_tables_from_import(
        imported,
        destination
    ):
        for table in (
            "protection_tests",
            "component_tests",
        ):
            if (
                ProjectMergeService._table_exists(
                    imported,
                    table
                )
                and
                not ProjectMergeService._table_exists(
                    destination,
                    table
                )
            ):
                schema = imported.execute(
                    "SELECT sql FROM sqlite_master "
                    "WHERE type='table' AND name=?",
                    (table,)
                ).fetchone()

                if schema and schema[0]:
                    destination.execute(
                        schema[0]
                    )

    # =========================================================
    # ARTIFACTS
    # =========================================================

    def _copy_non_data_files(
        self,
        temp_root: Path,
        destination_project_folder: Path,
        source_title: str
    ) -> int:

        ignored = {
            self.MANIFEST_NAME,
            "project.json",
            "assets.json",
            "components.json",
            "testing.db",
        }

        artifact_root = (
            destination_project_folder /
            "Imported" /
            self._safe_name(source_title)
        )

        copied = 0

        for source in temp_root.rglob("*"):

            if not source.is_file():
                continue

            relative = source.relative_to(
                temp_root
            )

            if (
                relative.name in ignored
                or self._is_transient(relative)
            ):
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
                source,
                target
            )

            copied += 1

        return copied

    # =========================================================
    # JSON / ZIP HELPERS
    # =========================================================

    @staticmethod
    def _load_json_list(
        path: Path
    ):
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
    def _safe_extract(
        archive_file: Path,
        destination: Path
    ):
        destination = destination.resolve()

        with zipfile.ZipFile(
            archive_file,
            "r"
        ) as archive:

            for member in archive.infolist():

                target = (
                    destination /
                    member.filename
                ).resolve()

                if (
                    target != destination
                    and destination not in target.parents
                ):
                    raise ValueError(
                        "The project archive contains an unsafe "
                        "file path."
                    )

            archive.extractall(
                destination
            )

    @staticmethod
    def _is_transient(
        relative: Path
    ) -> bool:
        parts = {
            part.lower()
            for part in relative.parts
        }

        return bool(
            parts.intersection(
                {
                    "__pycache__",
                    ".git",
                    ".pytest_cache",
                    ".mypy_cache",
                }
            )
        ) or relative.suffix.lower() in {
            ".pyc",
            ".pyo",
        }

    @staticmethod
    def _safe_name(
        value: str
    ) -> str:
        invalid = '<>:"/\\|?*'
        return "".join(
            "_"
            if char in invalid
            else char
            for char in str(value)
        ).strip() or "Imported_Project"

    # =========================================================
    # DATABASE HELPERS
    # =========================================================

    @staticmethod
    def _get_project_id(
        project_folder: Path
    ) -> str:

        project_file = (
            project_folder /
            "project.json"
        )

        if not project_file.exists():
            raise ValueError(
                "Destination project.json is missing."
            )

        with open(
            project_file,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        project_id = data.get(
            "project_id"
        )

        if not project_id:
            raise ValueError(
                "Destination project has no project_id."
            )

        return str(project_id)

    @staticmethod
    def _table_exists(
        connection,
        table
    ) -> bool:
        row = connection.execute(
            "SELECT 1 FROM sqlite_master "
            "WHERE type='table' AND name=?",
            (table,)
        ).fetchone()

        return row is not None

    @staticmethod
    def _table_columns(
        connection,
        table
    ) -> list[str]:
        return [
            row[1]
            for row in connection.execute(
                f"PRAGMA table_info({ProjectMergeService._quote(table)})"
            ).fetchall()
        ]

    @staticmethod
    def _row_exists(
        connection,
        table,
        column,
        value
    ) -> bool:
        return (
            connection.execute(
                f"SELECT 1 FROM {ProjectMergeService._quote(table)} "
                f"WHERE {ProjectMergeService._quote(column)}=? LIMIT 1",
                (value,)
            ).fetchone()
            is not None
        )

    @staticmethod
    def _count_database_rows(
        database_file
    ) -> int:
        connection = sqlite3.connect(
            database_file
        )
        try:
            total = 0
            for table in (
                "protection_tests",
                "component_tests",
            ):
                if ProjectMergeService._table_exists(
                    connection,
                    table
                ):
                    total += connection.execute(
                        f"SELECT COUNT(*) FROM "
                        f"{ProjectMergeService._quote(table)}"
                    ).fetchone()[0]
            return total
        finally:
            connection.close()

    @staticmethod
    def _quote(
        identifier
    ) -> str:
        return '"' + str(
            identifier
        ).replace(
            '"',
            '""'
        ) + '"'

    # =========================================================
    # ID HELPERS
    # =========================================================

    @staticmethod
    def _new_node_id() -> str:
        return f"AST-{uuid4().hex[:8].upper()}"

    @staticmethod
    def _new_component_id() -> str:
        return f"CMP-{uuid4().hex[:8].upper()}"

    @staticmethod
    def _new_test_id(
        table
    ) -> str:
        prefix = (
            "PT"
            if table == "protection_tests"
            else "CT"
        )
        return f"{prefix}-{uuid4().hex[:10].upper()}"
