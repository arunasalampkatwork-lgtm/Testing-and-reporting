from __future__ import annotations

import json
import shutil
import tempfile
import zipfile
from pathlib import Path
from uuid import uuid4

from app.config.settings import PROJECTS_DIR
from app.services.asset_library_manager import AssetLibraryManager


class ProjectTransferService:
    """
    Export/import a complete Protection Testing Suite project.

    Export contains:
      - project.json
      - assets.json
      - components.json
      - testing.db
      - asset_links.json, when present
      - reports and any other project files
      - only the global asset-library records referenced by this project

    During import, referenced physical assets are merged into the
    destination global asset library. Existing matching assets are reused;
    new assets are created. Project-local node IDs/component IDs remain
    unchanged, so the copied testing database keeps its relationships.
    """

    FORMAT_NAME = "ProtectionTestingSuiteProject"
    FORMAT_VERSION = 1
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
    # EXPORT
    # =========================================================

    def export_project(
        self,
        project_folder: Path,
        output_file: Path
    ) -> Path:
        project_folder = Path(project_folder)
        output_file = Path(output_file)

        if not project_folder.exists() or not project_folder.is_dir():
            raise ValueError(
                f"Project folder does not exist:\n{project_folder}"
            )

        project_json = project_folder / "project.json"

        if not project_json.exists():
            raise ValueError(
                "The selected folder is not a valid project. "
                "project.json is missing."
            )

        try:
            with open(
                project_json,
                "r",
                encoding="utf-8"
            ) as file:
                project_data = json.load(file)
        except Exception as error:
            raise ValueError(
                f"Could not read project.json:\n{error}"
            ) from error

        referenced_asset_ids = self._get_referenced_asset_ids(
            project_folder
        )

        global_assets = []

        self.asset_library.load()

        for asset_id in referenced_asset_ids:
            asset = self.asset_library.get_asset(asset_id)

            if asset is not None:
                global_assets.append(
                    self._json_safe(asset)
                )

        manifest = {
            "format": self.FORMAT_NAME,
            "format_version": self.FORMAT_VERSION,
            "created_by": "Protection Testing Suite",
            "project": self._json_safe(project_data),
            "global_assets": global_assets,
        }

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if output_file.exists():
            output_file.unlink()

        with zipfile.ZipFile(
            output_file,
            "w",
            compression=zipfile.ZIP_DEFLATED
        ) as archive:

            archive.writestr(
                self.MANIFEST_NAME,
                json.dumps(
                    manifest,
                    indent=4,
                    ensure_ascii=False
                )
            )

            for path in project_folder.rglob("*"):
                if not path.is_file():
                    continue

                relative = path.relative_to(
                    project_folder
                )

                # Do not accidentally package transient Python/cache data.
                if self._is_transient(relative):
                    continue

                archive.write(
                    path,
                    arcname=str(relative)
                )

        return output_file

    # =========================================================
    # IMPORT
    # =========================================================

    def import_project(
        self,
        archive_file: Path,
        project_name: str | None = None
    ) -> tuple[Path, dict]:
        archive_file = Path(archive_file)

        if not archive_file.exists():
            raise ValueError(
                "The selected project archive does not exist."
            )

        if not zipfile.is_zipfile(archive_file):
            raise ValueError(
                "The selected file is not a valid Protection Testing "
                "Suite project archive."
            )

        with tempfile.TemporaryDirectory(
            prefix="pts_import_"
        ) as temp_dir:

            temp_root = Path(temp_dir)

            self._safe_extract(
                archive_file,
                temp_root
            )

            manifest_file = (
                temp_root /
                self.MANIFEST_NAME
            )

            if not manifest_file.exists():
                raise ValueError(
                    "This file is not a valid Protection Testing Suite "
                    "project archive. The project manifest is missing."
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

            self._validate_manifest(
                manifest
            )

            project_data = dict(
                manifest.get(
                    "project",
                    {}
                )
            )

            original_title = str(
                project_data.get(
                    "title",
                    "Imported Project"
                )
                or "Imported Project"
            ).strip()

            final_title = (
                str(project_name).strip()
                if project_name
                else original_title
            )

            if not final_title:
                final_title = "Imported Project"

            destination = (
                self.projects_directory /
                self._safe_folder_name(final_title)
            )

            if destination.exists():
                raise FileExistsError(
                    f"A project named '{final_title}' already exists."
                )

            # -------------------------------------------------
            # Merge global physical assets BEFORE copying the
            # project. This gives us an old-ID -> local-ID map.
            # -------------------------------------------------

            asset_id_map = self._merge_global_assets(
                manifest.get(
                    "global_assets",
                    []
                )
            )

            # -------------------------------------------------
            # Copy project files.
            # -------------------------------------------------

            source_files = [
                path
                for path in temp_root.rglob("*")
                if path.is_file()
                and path.name != self.MANIFEST_NAME
                and not self._is_transient(
                    path.relative_to(temp_root)
                )
            ]

            if not source_files:
                raise ValueError(
                    "The project archive contains no project files."
                )

            destination.mkdir(
                parents=True,
                exist_ok=False
            )

            try:
                for source in source_files:
                    relative = source.relative_to(
                        temp_root
                    )

                    target = (
                        destination /
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

                # -------------------------------------------------
                # Rewrite imported project assets so their
                # global asset IDs point to the destination
                # global asset library.
                # -------------------------------------------------

                self._rewrite_project_assets(
                    destination,
                    asset_id_map
                )

                # Update project title if the user chose a new name.
                project_data["title"] = final_title

                project_file = (
                    destination /
                    "project.json"
                )

                with open(
                    project_file,
                    "w",
                    encoding="utf-8"
                ) as file:
                    json.dump(
                        project_data,
                        file,
                        indent=4,
                        ensure_ascii=False
                    )

            except Exception:
                shutil.rmtree(
                    destination,
                    ignore_errors=True
                )
                raise

        return destination, {
            "project_name": final_title,
            "original_project_name": original_title,
            "global_assets_imported": len(
                manifest.get(
                    "global_assets",
                    []
                )
            ),
            "asset_id_map": asset_id_map,
        }

    # =========================================================
    # REFERENCED GLOBAL ASSETS
    # =========================================================

    def _get_referenced_asset_ids(
        self,
        project_folder: Path
    ) -> set[str]:
        assets_file = (
            project_folder /
            "assets.json"
        )

        if not assets_file.exists():
            return set()

        try:
            with open(
                assets_file,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)
        except Exception:
            return set()

        if isinstance(data, dict):
            assets = data.get(
                "assets",
                []
            )
        elif isinstance(data, list):
            assets = data
        else:
            assets = []

        result = set()

        for item in assets:
            if not isinstance(item, dict):
                continue

            asset_id = item.get(
                "asset_id"
            )

            if asset_id:
                result.add(
                    str(asset_id)
                )

        return result

    # =========================================================
    # GLOBAL ASSET MERGE
    # =========================================================

    def _merge_global_assets(
        self,
        imported_assets
    ) -> dict[str, str]:
        """
        Return {source_asset_id: destination_asset_id}.

        Matching is performed by the existing global asset library's
        normal duplicate rules: serial number first, then asset tag.
        Existing physical assets are reused rather than duplicated.
        """

        self.asset_library.load()

        asset_id_map = {}

        # First create/reuse every asset.
        for source in imported_assets:

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

            serial_number = str(
                source.get(
                    "serial_number",
                    ""
                )
                or ""
            ).strip()

            if not asset_type or not asset_tag:
                continue

            existing = self.asset_library.find_duplicate(
                asset_type=asset_type,
                asset_tag=asset_tag,
                serial_number=serial_number
            )

            if existing is not None:
                destination_id = existing[
                    "asset_id"
                ]

            else:
                created = self.asset_library.create_asset(
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
                    serial_number=serial_number,
                    manufacturer=source.get(
                        "manufacturer",
                        ""
                    ),
                    model=source.get(
                        "model",
                        ""
                    ),
                    metadata={}
                )

                destination_id = created[
                    "asset_id"
                ]

            asset_id_map[
                str(source_id)
            ] = str(destination_id)

        # Second pass: import/update non-core fields and repair
        # parent_asset_id references.
        for source in imported_assets:

            if not isinstance(source, dict):
                continue

            source_id = source.get(
                "asset_id"
            )

            destination_id = asset_id_map.get(
                str(source_id)
            )

            if not destination_id:
                continue

            existing = self.asset_library.get_asset(
                destination_id
            )

            if existing is None:
                continue

            metadata = dict(
                source.get(
                    "metadata",
                    {}
                )
                or {}
            )

            old_parent_id = metadata.get(
                "parent_asset_id"
            )

            if old_parent_id:
                metadata[
                    "parent_asset_id"
                ] = asset_id_map.get(
                    str(old_parent_id),
                    old_parent_id
                )

            updates = {
                "name": source.get(
                    "name",
                    existing.get("name", "")
                ),
                "description": source.get(
                    "description",
                    existing.get("description", "")
                ),
                "manufacturer": source.get(
                    "manufacturer",
                    existing.get("manufacturer", "")
                ),
                "model": source.get(
                    "model",
                    existing.get("model", "")
                ),
                "metadata": metadata,
            }

            # These fields are dynamically stored by AssetManager.
            for key in (
                "equipment_name",
                "equipment_type",
                "ct_count",
                "relay_count",
                "aux_count",
                "meter_count",
            ):
                if key in source:
                    updates[key] = source[key]

            # Do not overwrite an existing physical asset's serial
            # number merely because an imported copy has stale data.
            # The duplicate was already resolved using serial/tag.

            try:
                self.asset_library.update_asset(
                    destination_id,
                    updates
                )
            except Exception:
                # Existing physical asset data is authoritative.
                # The project can still point to it.
                pass

        self.asset_library.save()

        return asset_id_map

    # =========================================================
    # REWRITE PROJECT ASSETS
    # =========================================================

    def _rewrite_project_assets(
        self,
        project_folder: Path,
        asset_id_map: dict[str, str]
    ):
        assets_file = (
            project_folder /
            "assets.json"
        )

        if not assets_file.exists():
            return

        with open(
            assets_file,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            assets = data
            wrapper = None
        elif isinstance(data, dict):
            assets = data.get(
                "assets",
                []
            )
            wrapper = data
        else:
            return

        for asset in assets:
            if not isinstance(asset, dict):
                continue

            old_asset_id = asset.get(
                "asset_id"
            )

            if old_asset_id in asset_id_map:
                asset[
                    "asset_id"
                ] = asset_id_map[
                    old_asset_id
                ]

            old_linked_id = asset.get(
                "linked_asset_id"
            )

            if old_linked_id in asset_id_map:
                asset[
                    "linked_asset_id"
                ] = asset_id_map[
                    old_linked_id
                ]

        output = (
            assets
            if wrapper is None
            else wrapper
        )

        with open(
            assets_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                output,
                file,
                indent=4,
                ensure_ascii=False
            )

    # =========================================================
    # VALIDATION
    # =========================================================

    def _validate_manifest(
        self,
        manifest
    ):
        if not isinstance(manifest, dict):
            raise ValueError(
                "Invalid project manifest."
            )

        if manifest.get(
            "format"
        ) != self.FORMAT_NAME:
            raise ValueError(
                "This file was not created by "
                "Protection Testing Suite."
            )

        version = int(
            manifest.get(
                "format_version",
                0
            )
        )

        if version > self.FORMAT_VERSION:
            raise ValueError(
                "This project archive was created by a newer "
                "version of Protection Testing Suite."
            )

        if not isinstance(
            manifest.get(
                "global_assets",
                []
            ),
            list
        ):
            raise ValueError(
                "Invalid global asset section in project archive."
            )

    # =========================================================
    # SAFE ZIP EXTRACTION
    # =========================================================

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

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _safe_folder_name(
        title: str
    ) -> str:
        invalid = '<>:"/\\|?*'
        result = "".join(
            "_"
            if character in invalid
            else character
            for character in str(title)
        ).strip()

        return result or (
            f"Imported_Project_{uuid4().hex[:6]}"
        )

    @staticmethod
    def _is_transient(
        relative_path: Path
    ) -> bool:
        parts = {
            part.lower()
            for part in relative_path.parts
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
        ) or relative_path.suffix.lower() in {
            ".pyc",
            ".pyo",
        }

    @staticmethod
    def _json_safe(
        value
    ):
        try:
            json.dumps(value)
            return value
        except TypeError:
            return json.loads(
                json.dumps(
                    value,
                    default=str
                )
            )
