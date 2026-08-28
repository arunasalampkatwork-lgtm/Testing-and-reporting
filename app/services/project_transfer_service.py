
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
from app.services.thermal_template_service import (
    ThermalTemplateService,
)


class ProjectTransferService:
    """
    Complete .ptsproject export/import service.

    Thermal templates are included in the project archive in two ways:

    1. The project's testing.db contains project snapshots.
    2. project_manifest.json contains the global thermal-template library
       visible to the project at export time.

    On import, global templates are inserted into the imported project's
    testing.db when the template ID is not already present. This makes the
    imported .ptsproject self-contained and portable.
    """

    FORMAT_NAME = "ProtectionTestingSuiteProject"
    FORMAT_VERSION = 2
    MANIFEST_NAME = "project_manifest.json"

    def __init__(self, projects_directory=None):
        self.projects_directory = Path(
            projects_directory or PROJECTS_DIR
        )
        self.projects_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.asset_library = AssetLibraryManager()

    # =========================================================
    # EXPORT
    # =========================================================

    def export_project(
        self,
        project_folder,
        output_file,
    ):
        project_folder = Path(project_folder)
        output_file = Path(output_file)

        if not project_folder.is_dir():
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
            project_data = json.loads(
                project_json.read_text(
                    encoding="utf-8"
                )
            )
        except Exception as error:
            raise ValueError(
                f"Could not read project.json:\n{error}"
            ) from error

        referenced_asset_ids = (
            self._get_referenced_asset_ids(
                project_folder
            )
        )

        global_assets = []

        self.asset_library.load()

        for asset_id in referenced_asset_ids:
            asset = self.asset_library.get_asset(
                asset_id
            )

            if asset is not None:
                global_assets.append(
                    self._json_safe(asset)
                )

        # -----------------------------------------------------
        # Thermal templates
        #
        # Include every global template visible at export time.
        # Project-local snapshots remain inside testing.db.
        # -----------------------------------------------------

        global_thermal_templates = (
            ThermalTemplateService
            .get_global_templates()
        )

        thermal_records = [
            ThermalTemplateService._template_to_dict(
                template
            )
            for template in global_thermal_templates
        ]

        manifest = {
            "format": self.FORMAT_NAME,
            "format_version": self.FORMAT_VERSION,
            "created_by": "Protection Testing Suite",
            "project": self._json_safe(
                project_data
            ),
            "global_assets": global_assets,
            "thermal_templates": thermal_records,
        }

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if output_file.exists():
            output_file.unlink()

        with zipfile.ZipFile(
            output_file,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:

            archive.writestr(
                self.MANIFEST_NAME,
                json.dumps(
                    manifest,
                    indent=4,
                    ensure_ascii=False,
                ),
            )

            # Explicit copy of the template library into the project
            # archive. This is useful for inspection/recovery and makes
            # the archive self-describing.
            archive.writestr(
                "thermal_templates.json",
                json.dumps(
                    thermal_records,
                    indent=4,
                    ensure_ascii=False,
                ),
            )

            for path in project_folder.rglob("*"):
                if not path.is_file():
                    continue

                relative = path.relative_to(
                    project_folder
                )

                if self._is_transient(relative):
                    continue

                archive.write(
                    path,
                    arcname=str(relative),
                )

        return output_file

    # =========================================================
    # IMPORT
    # =========================================================

    def import_project(
        self,
        archive_file,
        project_name=None,
    ):
        archive_file = Path(archive_file)

        if not archive_file.exists():
            raise ValueError(
                "The selected project archive does not exist."
            )

        if not zipfile.is_zipfile(archive_file):
            raise ValueError(
                "The selected file is not a valid Protection "
                "Testing Suite project archive."
            )

        with tempfile.TemporaryDirectory(
            prefix="pts_import_"
        ) as temp_dir:

            temp_root = Path(temp_dir)

            self._safe_extract(
                archive_file,
                temp_root,
            )

            manifest_file = (
                temp_root /
                self.MANIFEST_NAME
            )

            if not manifest_file.exists():
                raise ValueError(
                    "The project manifest is missing."
                )

            try:
                manifest = json.loads(
                    manifest_file.read_text(
                        encoding="utf-8"
                    )
                )
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
                    {},
                )
            )

            original_title = str(
                project_data.get(
                    "title",
                    "Imported Project",
                )
                or "Imported Project"
            ).strip()

            final_title = (
                str(project_name).strip()
                if project_name
                else original_title
            ) or "Imported Project"

            destination = (
                self.projects_directory /
                self._safe_folder_name(
                    final_title
                )
            )

            if destination.exists():
                raise FileExistsError(
                    f"A project named '{final_title}' "
                    "already exists."
                )

            asset_id_map = (
                self._merge_global_assets(
                    manifest.get(
                        "global_assets",
                        [],
                    )
                )
            )

            source_files = [
                path
                for path in temp_root.rglob("*")
                if (
                    path.is_file()
                    and path.name != self.MANIFEST_NAME
                    and not self._is_transient(
                        path.relative_to(temp_root)
                    )
                )
            ]

            if not source_files:
                raise ValueError(
                    "The project archive contains no project files."
                )

            destination.mkdir(
                parents=True,
                exist_ok=False,
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
                        exist_ok=True,
                    )

                    shutil.copy2(
                        source,
                        target,
                    )

                self._rewrite_project_assets(
                    destination,
                    asset_id_map,
                )

                project_data["title"] = final_title

                (
                    destination /
                    "project.json"
                ).write_text(
                    json.dumps(
                        project_data,
                        indent=4,
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

                imported_thermal = (
                    self._import_thermal_templates(
                        destination,
                        manifest.get(
                            "thermal_templates",
                            [],
                        ),
                    )
                )

            except Exception:
                shutil.rmtree(
                    destination,
                    ignore_errors=True,
                )
                raise

        return destination, {
            "project_name": final_title,
            "original_project_name": original_title,
            "global_assets_imported": len(
                manifest.get(
                    "global_assets",
                    [],
                )
            ),
            "thermal_templates_imported": imported_thermal,
            "asset_id_map": asset_id_map,
        }

    # =========================================================
    # THERMAL TEMPLATE IMPORT
    # =========================================================

    def _import_thermal_templates(
        self,
        project_folder,
        records,
    ):
        """
        Insert global template snapshots into the project's testing.db.

        Existing template IDs are preserved. This is intentional:
        a project containing an older template remains historically stable.
        """

        database_path = (
            Path(project_folder) /
            "testing.db"
        )

        if not database_path.exists():
            return 0

        if not records:
            return 0

        imported = 0

        connection = sqlite3.connect(
            str(database_path)
        )

        try:
            columns = {
                row[1]
                for row in connection.execute(
                    "PRAGMA table_info(thermal_templates)"
                ).fetchall()
            }

            if "thermal_templates" not in (
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table'"
                ).fetchall()
            ):
                connection.execute("""
                    CREATE TABLE IF NOT EXISTS thermal_templates (
                        template_id TEXT PRIMARY KEY,
                        protection_function TEXT NOT NULL,
                        manufacturer TEXT NOT NULL,
                        model TEXT NOT NULL,
                        name TEXT NOT NULL,
                        curve_type TEXT NOT NULL,
                        rated_current REAL DEFAULT 0,
                        pickup_current REAL DEFAULT 1,
                        thermal_constant REAL DEFAULT 0,
                        cooling_constant REAL DEFAULT 0,
                        curve_json TEXT,
                        heating_curve_json TEXT,
                        cooling_curve_json TEXT,
                        equation TEXT DEFAULT '',
                        independent_variable TEXT DEFAULT 'I',
                        dependent_variable TEXT DEFAULT 'T',
                        variables_json TEXT DEFAULT '[]',
                        parameters_json TEXT DEFAULT '{}',
                        x_min REAL DEFAULT 1,
                        x_max REAL DEFAULT 20,
                        notes TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        UNIQUE(
                            protection_function,
                            manufacturer,
                            model,
                            name
                        )
                    )
                """)
                columns = {
                    row[1]
                    for row in connection.execute(
                        "PRAGMA table_info(thermal_templates)"
                    ).fetchall()
                }

            migrations = [
                ("equation", "ALTER TABLE thermal_templates ADD COLUMN equation TEXT DEFAULT ''"),
                ("independent_variable", "ALTER TABLE thermal_templates ADD COLUMN independent_variable TEXT DEFAULT 'I'"),
                ("dependent_variable", "ALTER TABLE thermal_templates ADD COLUMN dependent_variable TEXT DEFAULT 'T'"),
                ("variables_json", "ALTER TABLE thermal_templates ADD COLUMN variables_json TEXT DEFAULT '[]'"),
                ("parameters_json", "ALTER TABLE thermal_templates ADD COLUMN parameters_json TEXT DEFAULT '{}'"),
                ("x_min", "ALTER TABLE thermal_templates ADD COLUMN x_min REAL DEFAULT 1"),
                ("x_max", "ALTER TABLE thermal_templates ADD COLUMN x_max REAL DEFAULT 20"),
            ]

            for name, sql in migrations:
                if name not in columns:
                    connection.execute(sql)

            required = {
                "template_id",
                "protection_function",
                "manufacturer",
                "model",
                "name",
                "curve_type",
                "rated_current",
                "pickup_current",
                "thermal_constant",
                "cooling_constant",
                "curve_json",
                "heating_curve_json",
                "cooling_curve_json",
                "equation",
                "independent_variable",
                "dependent_variable",
                "variables_json",
                "parameters_json",
                "x_min",
                "x_max",
                "notes",
                "created_at",
                "updated_at",
            }

            if not required.issubset(columns):
                # Old project database. The application's normal
                # create_tables migration must run before import.
                return 0

            for record in records:
                template = (
                    ThermalTemplateService
                    ._dict_to_template(record)
                )

                exists = connection.execute(
                    """
                    SELECT template_id
                    FROM thermal_templates
                    WHERE template_id=?
                    """,
                    (template.template_id,),
                ).fetchone()

                if exists:
                    continue

                timestamp = (
                    datetime_now()
                )

                connection.execute(
                    """
                    INSERT INTO thermal_templates (
                        template_id,
                        protection_function,
                        manufacturer,
                        model,
                        name,
                        curve_type,
                        rated_current,
                        pickup_current,
                        thermal_constant,
                        cooling_constant,
                        curve_json,
                        heating_curve_json,
                        cooling_curve_json,
                        equation,
                        independent_variable,
                        dependent_variable,
                        variables_json,
                        parameters_json,
                        x_min,
                        x_max,
                        notes,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        ?, ?, ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?,
                        ?, ?, ?, ?, ?,
                        ?, ?, ?, ?, ?
                    )
                    """,
                    (
                        template.template_id,
                        template.protection_function,
                        template.manufacturer,
                        template.model,
                        template.name,
                        template.curve_type,
                        template.rated_current,
                        template.pickup_current,
                        template.thermal_constant,
                        template.cooling_constant,
                        ThermalTemplateService._dump_curve(
                            template.curves
                        ),
                        ThermalTemplateService._dump_curve(
                            template.heating_curve
                        ),
                        ThermalTemplateService._dump_curve(
                            template.cooling_curve
                        ),
                        template.equation,
                        template.independent_variable,
                        template.dependent_variable,
                        ThermalTemplateService._dump_variables(
                            template.variables
                        ),
                        ThermalTemplateService._dump_parameters(
                            template.parameters
                        ),
                        template.x_min,
                        template.x_max,
                        template.notes,
                        timestamp,
                        timestamp,
                    ),
                )

                imported += 1

            connection.commit()

        finally:
            connection.close()

        return imported

    # =========================================================
    # ASSET HANDLING
    # =========================================================

    def _get_referenced_asset_ids(
        self,
        project_folder,
    ):
        assets_file = (
            Path(project_folder) /
            "assets.json"
        )

        if not assets_file.exists():
            return set()

        try:
            data = json.loads(
                assets_file.read_text(
                    encoding="utf-8"
                )
            )
        except Exception:
            return set()

        if isinstance(data, dict):
            assets = data.get(
                "assets",
                [],
            )
        elif isinstance(data, list):
            assets = data
        else:
            assets = []

        return {
            str(item["asset_id"])
            for item in assets
            if isinstance(item, dict)
            and item.get("asset_id")
        }

    def _merge_global_assets(
        self,
        imported_assets,
    ):
        self.asset_library.load()

        asset_id_map = {}

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
                    "",
                )
                or ""
            ).strip().upper()

            asset_tag = str(
                source.get(
                    "asset_tag",
                    source.get(
                        "name",
                        "",
                    ),
                )
                or ""
            ).strip()

            serial_number = str(
                source.get(
                    "serial_number",
                    "",
                )
                or ""
            ).strip()

            if not asset_type or not asset_tag:
                continue

            existing = (
                self.asset_library.find_duplicate(
                    asset_type=asset_type,
                    asset_tag=asset_tag,
                    serial_number=serial_number,
                )
            )

            if existing is not None:
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
                            "",
                        ),
                        description=source.get(
                            "description",
                            "",
                        ),
                        serial_number=serial_number,
                        manufacturer=source.get(
                            "manufacturer",
                            "",
                        ),
                        model=source.get(
                            "model",
                            "",
                        ),
                        metadata={},
                    )
                )

                destination_id = created[
                    "asset_id"
                ]

            asset_id_map[
                str(source_id)
            ] = str(destination_id)

        self.asset_library.save()

        return asset_id_map

    def _rewrite_project_assets(
        self,
        project_folder,
        asset_id_map,
    ):
        assets_file = (
            Path(project_folder) /
            "assets.json"
        )

        if not assets_file.exists():
            return

        data = json.loads(
            assets_file.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, list):
            assets = data
            wrapper = None
        elif isinstance(data, dict):
            assets = data.get(
                "assets",
                [],
            )
            wrapper = data
        else:
            return

        for asset in assets:
            if not isinstance(asset, dict):
                continue

            for key in (
                "asset_id",
                "linked_asset_id",
            ):
                old = asset.get(key)

                if old in asset_id_map:
                    asset[key] = asset_id_map[old]

        output = (
            assets
            if wrapper is None
            else wrapper
        )

        assets_file.write_text(
            json.dumps(
                output,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    # =========================================================
    # VALIDATION / ZIP SAFETY
    # =========================================================

    def _validate_manifest(
        self,
        manifest,
    ):
        if not isinstance(manifest, dict):
            raise ValueError(
                "Invalid project manifest."
            )

        if manifest.get("format") != (
            self.FORMAT_NAME
        ):
            raise ValueError(
                "This file was not created by "
                "Protection Testing Suite."
            )

        version = int(
            manifest.get(
                "format_version",
                0,
            )
        )

        if version > self.FORMAT_VERSION:
            raise ValueError(
                "This project archive was created by "
                "a newer version of Protection Testing Suite."
            )

        if not isinstance(
            manifest.get(
                "global_assets",
                [],
            ),
            list,
        ):
            raise ValueError(
                "Invalid global asset section."
            )

        if not isinstance(
            manifest.get(
                "thermal_templates",
                [],
            ),
            list,
        ):
            raise ValueError(
                "Invalid thermal-template section."
            )

    @staticmethod
    def _safe_extract(
        archive_file,
        destination,
    ):
        destination = Path(
            destination
        ).resolve()

        with zipfile.ZipFile(
            archive_file,
            "r",
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
                        "The project archive contains "
                        "an unsafe file path."
                    )

            archive.extractall(
                destination
            )

    @staticmethod
    def _safe_folder_name(title):
        invalid = '<>:"/\\|?*'

        result = "".join(
            "_"
            if char in invalid
            else char
            for char in str(title)
        ).strip()

        return result or (
            f"Imported_Project_{uuid4().hex[:6]}"
        )

    @staticmethod
    def _is_transient(relative_path):
        parts = {
            part.lower()
            for part in Path(
                relative_path
            ).parts
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
        ) or Path(
            relative_path
        ).suffix.lower() in {
            ".pyc",
            ".pyo",
        }

    @staticmethod
    def _json_safe(value):
        try:
            json.dumps(value)
            return value
        except TypeError:
            return json.loads(
                json.dumps(
                    value,
                    default=str,
                )
            )


def datetime_now():
    from datetime import datetime

    return datetime.now().isoformat(
        timespec="seconds"
    )
