
import json
import uuid
from datetime import datetime
from pathlib import Path

from app.config.settings import DATA_DIR
from app.models.thermal_template import (
    ThermalTemplate,
    ThermalCurvePoint,
    ThermalVariable,
)


GLOBAL_LIBRARY_FILE = DATA_DIR / "thermal_templates.json"


class ThermalTemplateService:
    """
    Thermal-template persistence layer.

    Project templates live in the project's testing.db.
    Every template created/updated through this service is also stored in
    the global thermal-template library so it is available to every project.

    When a project already contains a template with the same template_id,
    the project copy wins. This preserves the curve used by an existing
    project/test even if the global definition is later changed.
    """

    def __init__(self, database):
        self.database = database
        self._ensure_global_library()

        # Migrate any thermal templates that already exist in this
        # project's testing.db into the global library.  This is what
        # makes templates created before the global-library feature
        # available to other projects as well.
        self._migrate_project_templates_to_global()

    # ------------------------------------------------------------------
    # Global library
    # ------------------------------------------------------------------

    @staticmethod
    def _ensure_global_library():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not GLOBAL_LIBRARY_FILE.exists():
            GLOBAL_LIBRARY_FILE.write_text(
                "[]",
                encoding="utf-8",
            )

    @staticmethod
    def _read_global_records():
        ThermalTemplateService._ensure_global_library()

        try:
            data = json.loads(
                GLOBAL_LIBRARY_FILE.read_text(
                    encoding="utf-8"
                )
            )
        except Exception:
            return []

        return data if isinstance(data, list) else []

    @staticmethod
    def _write_global_records(records):
        ThermalTemplateService._ensure_global_library()

        temp = GLOBAL_LIBRARY_FILE.with_suffix(".tmp")

        temp.write_text(
            json.dumps(
                records,
                indent=4,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        temp.replace(GLOBAL_LIBRARY_FILE)

    @classmethod
    def _global_upsert(cls, template):
        records = cls._read_global_records()

        record = cls._template_to_dict(template)

        replaced = False

        for index, existing in enumerate(records):
            if str(existing.get("template_id")) == str(
                template.template_id
            ):
                records[index] = record
                replaced = True
                break

        if not replaced:
            records.append(record)

        cls._write_global_records(records)

    @classmethod
    def _global_delete(cls, template_id):
        records = cls._read_global_records()

        records = [
            item
            for item in records
            if str(item.get("template_id"))
            != str(template_id)
        ]

        cls._write_global_records(records)

    @classmethod
    def get_global_templates(cls):
        return [
            cls._dict_to_template(item)
            for item in cls._read_global_records()
        ]

    def _thermal_table_exists(self):
        """
        Return True only when the current project database already has
        the thermal_templates table.

        This keeps service construction safe during project/database
        initialization, where create_tables() may not have run yet.
        """
        try:
            row = self.database.fetch_one(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                  AND name='thermal_templates'
                """
            )
            return row is not None
        except Exception:
            return False

    @staticmethod
    def _template_identity(template):
        """
        Stable logical identity used when merging project and global
        templates.  template_id is deliberately not the only key:
        older projects may contain the same relay/template definition
        under a different generated ID.
        """
        return (
            str(template.protection_function or "").strip().lower(),
            str(template.manufacturer or "").strip().lower(),
            str(template.model or "").strip().lower(),
            str(template.name or "").strip().lower(),
        )

    def _migrate_project_templates_to_global(self):
        """
        Copy templates already stored in the current project's
        thermal_templates table into the global JSON library.

        Existing global records are preserved.  If the same template_id
        already exists globally, the global copy is not silently
        overwritten during migration.  Normal create/update operations
        still explicitly synchronize their template through
        _global_upsert().
        """
        if not self._thermal_table_exists():
            return 0

        try:
            project_templates = self._query_project(
                f"""
                SELECT {self._select_columns()}
                FROM thermal_templates
                ORDER BY manufacturer, model, name
                """
            )
        except Exception:
            # A partially migrated/older database should not prevent
            # the application from opening. create_tables() will handle
            # schema migration separately.
            return 0

        if not project_templates:
            return 0

        records = self._read_global_records()

        global_ids = {
            str(item.get("template_id", "")).strip()
            for item in records
            if item.get("template_id")
        }

        global_identity = set()
        for item in records:
            try:
                template = self._dict_to_template(item)
                global_identity.add(
                    self._template_identity(template)
                )
            except Exception:
                continue

        added = 0

        for template in project_templates:
            template_id = str(
                template.template_id or ""
            ).strip()
            identity = self._template_identity(template)

            if template_id and template_id in global_ids:
                continue

            if identity in global_identity:
                continue

            records.append(
                self._template_to_dict(template)
            )

            if template_id:
                global_ids.add(template_id)

            global_identity.add(identity)
            added += 1

        if added:
            self._write_global_records(records)

        return added

    def sync_project_templates_to_global(self):
        """
        Public/manual synchronization hook.

        Useful after importing or restoring a project.  It is safe to
        call repeatedly; duplicates are ignored.
        """
        return self._migrate_project_templates_to_global()

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    @staticmethod
    def _template_to_dict(template):
        return {
            "template_id": template.template_id,
            "protection_function": template.protection_function,
            "manufacturer": template.manufacturer,
            "model": template.model,
            "name": template.name,
            "curve_type": template.curve_type,
            "rated_current": template.rated_current,
            "pickup_current": template.pickup_current,
            "thermal_constant": template.thermal_constant,
            "cooling_constant": template.cooling_constant,
            "curves": [
                {
                    "current_multiple": p.current_multiple,
                    "operating_time": p.operating_time,
                }
                for p in template.curves
            ],
            "heating_curve": [
                {
                    "current_multiple": p.current_multiple,
                    "operating_time": p.operating_time,
                }
                for p in template.heating_curve
            ],
            "cooling_curve": [
                {
                    "current_multiple": p.current_multiple,
                    "operating_time": p.operating_time,
                }
                for p in template.cooling_curve
            ],
            "equation": template.equation,
            "independent_variable": template.independent_variable,
            "dependent_variable": template.dependent_variable,
            "variables": [
                {
                    "name": v.name,
                    "unit": v.unit,
                    "description": v.description,
                    "default_value": v.default_value,
                    "is_input": v.is_input,
                }
                for v in template.variables
            ],
            "parameters": dict(template.parameters),
            "x_min": template.x_min,
            "x_max": template.x_max,
            "notes": template.notes,
        }

    @staticmethod
    def _dict_to_template(data):
        def curve(key):
            result = []
            for item in data.get(key, []) or []:
                try:
                    result.append(
                        ThermalCurvePoint(
                            current_multiple=float(
                                item["current_multiple"]
                            ),
                            operating_time=float(
                                item["operating_time"]
                            ),
                        )
                    )
                except (KeyError, TypeError, ValueError):
                    continue
            return result

        variables = []

        for item in data.get("variables", []) or []:
            try:
                variables.append(
                    ThermalVariable(
                        name=str(item["name"]),
                        unit=str(item.get("unit", "")),
                        description=str(
                            item.get("description", "")
                        ),
                        default_value=float(
                            item.get("default_value", 0)
                        ),
                        is_input=bool(
                            item.get("is_input", False)
                        ),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue

        parameters = {}

        for key, value in (
            data.get("parameters", {}) or {}
        ).items():
            try:
                parameters[str(key)] = float(value)
            except (TypeError, ValueError):
                continue

        return ThermalTemplate(
            template_id=str(
                data.get("template_id", "")
            ),
            protection_function=str(
                data.get("protection_function", "49")
            ),
            manufacturer=str(
                data.get("manufacturer", "")
            ),
            model=str(
                data.get("model", "")
            ),
            name=str(
                data.get("name", "")
            ),
            curve_type=str(
                data.get("curve_type", "POINT_TABLE")
            ),
            rated_current=float(
                data.get("rated_current", 0)
                or 0
            ),
            pickup_current=float(
                data.get("pickup_current", 1)
                or 1
            ),
            thermal_constant=float(
                data.get("thermal_constant", 0)
                or 0
            ),
            cooling_constant=float(
                data.get("cooling_constant", 0)
                or 0
            ),
            curves=curve("curves"),
            heating_curve=curve("heating_curve"),
            cooling_curve=curve("cooling_curve"),
            equation=str(
                data.get("equation", "")
            ),
            independent_variable=str(
                data.get("independent_variable", "I")
            ),
            dependent_variable=str(
                data.get("dependent_variable", "T")
            ),
            variables=variables,
            parameters=parameters,
            x_min=float(
                data.get("x_min", 1)
                or 1
            ),
            x_max=float(
                data.get("x_max", 20)
                or 20
            ),
            notes=str(
                data.get("notes", "")
            ),
        )

    # ------------------------------------------------------------------
    # SQLite serialization
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_template_id():
        return "THERMAL-" + uuid.uuid4().hex[:8].upper()

    @staticmethod
    def _timestamp():
        return datetime.now().isoformat(timespec="seconds")

    @staticmethod
    def _dump_curve(points):
        return json.dumps([
            {
                "current_multiple": float(
                    point.current_multiple
                ),
                "operating_time": float(
                    point.operating_time
                ),
            }
            for point in (points or [])
        ])

    @staticmethod
    def _load_curve(value):
        if not value:
            return []

        try:
            data = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []

        result = []

        for item in data:
            try:
                result.append(
                    ThermalCurvePoint(
                        current_multiple=float(
                            item["current_multiple"]
                        ),
                        operating_time=float(
                            item["operating_time"]
                        ),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue

        return result

    @staticmethod
    def _dump_variables(variables):
        return json.dumps([
            {
                "name": str(v.name),
                "unit": str(v.unit),
                "description": str(v.description),
                "default_value": float(v.default_value),
                "is_input": bool(v.is_input),
            }
            for v in (variables or [])
        ])

    @staticmethod
    def _load_variables(value):
        if not value:
            return []

        try:
            data = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []

        result = []

        for item in data:
            try:
                result.append(
                    ThermalVariable(
                        name=str(item["name"]),
                        unit=str(item.get("unit", "")),
                        description=str(
                            item.get("description", "")
                        ),
                        default_value=float(
                            item.get("default_value", 0)
                        ),
                        is_input=bool(
                            item.get("is_input", False)
                        ),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue

        return result

    @staticmethod
    def _dump_parameters(parameters):
        return json.dumps({
            str(key): float(value)
            for key, value in (parameters or {}).items()
        })

    @staticmethod
    def _load_parameters(value):
        if not value:
            return {}

        try:
            data = json.loads(value)

            return {
                str(key): float(value)
                for key, value in data.items()
            }

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError,
            AttributeError,
        ):
            return {}

    @staticmethod
    def _normalize(value):
        return str(value or "").strip()

    def _select_columns(self):
        return """
            template_id, protection_function, manufacturer, model, name,
            curve_type, rated_current, pickup_current, thermal_constant,
            cooling_constant, curve_json, heating_curve_json,
            cooling_curve_json, equation, independent_variable,
            dependent_variable, variables_json, parameters_json,
            x_min, x_max, notes, created_at, updated_at
        """

    # ------------------------------------------------------------------
    # Create / update / delete
    # ------------------------------------------------------------------

    def create_template(
        self,
        protection_function,
        manufacturer,
        model,
        name,
        curve_type="POINT_TABLE",
        rated_current=0.0,
        pickup_current=1.0,
        thermal_constant=0.0,
        cooling_constant=0.0,
        curves=None,
        heating_curve=None,
        cooling_curve=None,
        equation="",
        independent_variable="I",
        dependent_variable="T",
        variables=None,
        parameters=None,
        x_min=1.0,
        x_max=20.0,
        notes="",
    ):
        protection_function = self._normalize(
            protection_function
        )
        manufacturer = self._normalize(
            manufacturer
        )
        model = self._normalize(model)
        name = self._normalize(name)

        if not protection_function:
            raise ValueError(
                "Protection function is required."
            )

        if not manufacturer:
            raise ValueError(
                "Manufacturer is required."
            )

        if not model:
            raise ValueError(
                "Relay model is required."
            )

        if not name:
            raise ValueError(
                "Template name is required."
            )

        existing = self.database.fetch_one(
            """
            SELECT template_id
            FROM thermal_templates
            WHERE protection_function = ?
              AND LOWER(manufacturer) = LOWER(?)
              AND LOWER(model) = LOWER(?)
              AND LOWER(name) = LOWER(?)
            """,
            (
                protection_function,
                manufacturer,
                model,
                name,
            ),
        )

        if existing is not None:
            raise ValueError(
                "A thermal template with the same name "
                "already exists for this relay."
            )

        template_id = self._generate_template_id()
        timestamp = self._timestamp()

        self.database.execute(
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
                template_id,
                protection_function,
                manufacturer,
                model,
                name,
                curve_type,
                float(rated_current or 0),
                float(pickup_current or 1),
                float(thermal_constant or 0),
                float(cooling_constant or 0),
                self._dump_curve(curves),
                self._dump_curve(heating_curve),
                self._dump_curve(cooling_curve),
                str(equation or ""),
                str(independent_variable or "I"),
                str(dependent_variable or "T"),
                self._dump_variables(variables),
                self._dump_parameters(parameters),
                float(x_min),
                float(x_max),
                str(notes or ""),
                timestamp,
                timestamp,
            ),
        )

        template = self.get_template(template_id)

        self._global_upsert(template)

        return template_id

    def update_template(self, template_id, **kwargs):
        existing = self.get_template(template_id)

        if existing is None:
            raise ValueError(
                f"Thermal template '{template_id}' was not found."
            )

        allowed = {
            "protection_function",
            "manufacturer",
            "model",
            "name",
            "curve_type",
            "rated_current",
            "pickup_current",
            "thermal_constant",
            "cooling_constant",
            "curves",
            "heating_curve",
            "cooling_curve",
            "equation",
            "independent_variable",
            "dependent_variable",
            "variables",
            "parameters",
            "x_min",
            "x_max",
            "notes",
        }

        data = {
            key: value
            for key, value in kwargs.items()
            if key in allowed
        }

        for key in allowed:
            if key not in data:
                data[key] = getattr(
                    existing,
                    key,
                )

        timestamp = self._timestamp()

        self.database.execute(
            """
            UPDATE thermal_templates SET
                protection_function=?,
                manufacturer=?,
                model=?,
                name=?,
                curve_type=?,
                rated_current=?,
                pickup_current=?,
                thermal_constant=?,
                cooling_constant=?,
                curve_json=?,
                heating_curve_json=?,
                cooling_curve_json=?,
                equation=?,
                independent_variable=?,
                dependent_variable=?,
                variables_json=?,
                parameters_json=?,
                x_min=?,
                x_max=?,
                notes=?,
                updated_at=?
            WHERE template_id=?
            """,
            (
                data["protection_function"],
                data["manufacturer"],
                data["model"],
                data["name"],
                data["curve_type"],
                float(data["rated_current"] or 0),
                float(data["pickup_current"] or 1),
                float(data["thermal_constant"] or 0),
                float(data["cooling_constant"] or 0),
                self._dump_curve(data["curves"]),
                self._dump_curve(data["heating_curve"]),
                self._dump_curve(data["cooling_curve"]),
                str(data["equation"] or ""),
                str(
                    data["independent_variable"]
                    or "I"
                ),
                str(
                    data["dependent_variable"]
                    or "T"
                ),
                self._dump_variables(data["variables"]),
                self._dump_parameters(data["parameters"]),
                float(data["x_min"]),
                float(data["x_max"]),
                str(data["notes"] or ""),
                timestamp,
                template_id,
            ),
        )

        template = self.get_template(template_id)

        self._global_upsert(template)

        return template_id

    def delete_template(self, template_id):
        self.database.execute(
            """
            DELETE FROM thermal_templates
            WHERE template_id=?
            """,
            (template_id,),
        )

        self._global_delete(template_id)

    # ------------------------------------------------------------------
    # Project / global lookup
    # ------------------------------------------------------------------

    def get_template(self, template_id):
        row = self.database.fetch_one(
            f"""
            SELECT {self._select_columns()}
            FROM thermal_templates
            WHERE template_id=?
            """,
            (template_id,),
        )

        if row:
            return self._row_to_template(row)

        for template in self.get_global_templates():
            if str(template.template_id) == str(
                template_id
            ):
                return template

        return None

    def _query_project(self, sql, params=()):
        rows = self.database.fetch_all(
            sql,
            params,
        )

        return [
            self._row_to_template(row)
            for row in rows
        ]

    @classmethod
    def _merge_templates(cls, project_templates, global_templates):
        result = []
        seen_ids = set()
        seen_identity = set()

        # Project templates deliberately come first.  Therefore, when
        # the same logical template exists both locally and globally,
        # the project-local snapshot wins.
        for template in (
            list(project_templates)
            + list(global_templates)
        ):
            template_id = str(
                template.template_id or ""
            ).strip()

            identity = cls._template_identity(
                template
            )

            if template_id and template_id in seen_ids:
                continue

            if identity in seen_identity:
                continue

            if template_id:
                seen_ids.add(template_id)

            seen_identity.add(identity)
            result.append(template)

        return result

    def get_templates_for_relay(
        self,
        manufacturer,
        model,
        protection_function="49",
    ):
        project = self._query_project(
            f"""
            SELECT {self._select_columns()}
            FROM thermal_templates
            WHERE protection_function=?
              AND LOWER(manufacturer)=LOWER(?)
              AND LOWER(model)=LOWER(?)
            ORDER BY name
            """,
            (
                protection_function,
                manufacturer,
                model,
            ),
        )

        global_templates = [
            template
            for template in self.get_global_templates()
            if (
                str(template.protection_function)
                == str(protection_function)
                and str(template.manufacturer).strip().lower()
                == str(manufacturer).strip().lower()
                and str(template.model).strip().lower()
                == str(model).strip().lower()
            )
        ]

        return sorted(
            self._merge_templates(
                project,
                global_templates,
            ),
            key=lambda template: (
                template.name.lower()
            ),
        )

    def get_templates_for_function(
        self,
        protection_function="49",
    ):
        project = self._query_project(
            f"""
            SELECT {self._select_columns()}
            FROM thermal_templates
            WHERE protection_function=?
            ORDER BY manufacturer, model, name
            """,
            (protection_function,),
        )

        global_templates = [
            template
            for template in self.get_global_templates()
            if str(template.protection_function)
            == str(protection_function)
        ]

        return sorted(
            self._merge_templates(
                project,
                global_templates,
            ),
            key=lambda template: (
                template.manufacturer.lower(),
                template.model.lower(),
                template.name.lower(),
            ),
        )

    def get_all_templates(self):
        project = self._query_project(
            f"""
            SELECT {self._select_columns()}
            FROM thermal_templates
            ORDER BY manufacturer, model, name
            """
        )

        return sorted(
            self._merge_templates(
                project,
                self.get_global_templates(),
            ),
            key=lambda template: (
                template.manufacturer.lower(),
                template.model.lower(),
                template.name.lower(),
            ),
        )

    # ------------------------------------------------------------------
    # Import global definitions into a project database
    # ------------------------------------------------------------------

    def import_templates_into_project(
        self,
        templates,
        overwrite=False,
    ):
        imported = 0

        for template in templates or []:
            if not isinstance(
                template,
                ThermalTemplate,
            ):
                continue

            existing = self.database.fetch_one(
                """
                SELECT template_id
                FROM thermal_templates
                WHERE template_id=?
                """,
                (template.template_id,),
            )

            if existing and not overwrite:
                continue

            if existing:
                self._write_existing_template(
                    template
                )
            else:
                self._insert_template_object(
                    template
                )

            # Imported project templates should immediately become
            # available to every project as well.
            self._global_upsert(template)

            imported += 1

        return imported

    def _insert_template_object(self, template):
        timestamp = self._timestamp()

        self.database.execute(
            """
            INSERT OR IGNORE INTO thermal_templates (
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
                self._dump_curve(template.curves),
                self._dump_curve(template.heating_curve),
                self._dump_curve(template.cooling_curve),
                template.equation,
                template.independent_variable,
                template.dependent_variable,
                self._dump_variables(template.variables),
                self._dump_parameters(template.parameters),
                template.x_min,
                template.x_max,
                template.notes,
                timestamp,
                timestamp,
            ),
        )

    def _write_existing_template(self, template):
        self.database.execute(
            """
            UPDATE thermal_templates SET
                protection_function=?,
                manufacturer=?,
                model=?,
                name=?,
                curve_type=?,
                rated_current=?,
                pickup_current=?,
                thermal_constant=?,
                cooling_constant=?,
                curve_json=?,
                heating_curve_json=?,
                cooling_curve_json=?,
                equation=?,
                independent_variable=?,
                dependent_variable=?,
                variables_json=?,
                parameters_json=?,
                x_min=?,
                x_max=?,
                notes=?,
                updated_at=?
            WHERE template_id=?
            """,
            (
                template.protection_function,
                template.manufacturer,
                template.model,
                template.name,
                template.curve_type,
                template.rated_current,
                template.pickup_current,
                template.thermal_constant,
                template.cooling_constant,
                self._dump_curve(template.curves),
                self._dump_curve(template.heating_curve),
                self._dump_curve(template.cooling_curve),
                template.equation,
                template.independent_variable,
                template.dependent_variable,
                self._dump_variables(template.variables),
                self._dump_parameters(template.parameters),
                template.x_min,
                template.x_max,
                template.notes,
                self._timestamp(),
                template.template_id,
            ),
        )

    def _row_to_template(self, row):
        return ThermalTemplate(
            template_id=row[0],
            protection_function=row[1],
            manufacturer=row[2],
            model=row[3],
            name=row[4],
            curve_type=row[5],
            rated_current=float(row[6] or 0),
            pickup_current=float(row[7] or 1),
            thermal_constant=float(row[8] or 0),
            cooling_constant=float(row[9] or 0),
            curves=self._load_curve(row[10]),
            heating_curve=self._load_curve(row[11]),
            cooling_curve=self._load_curve(row[12]),
            equation=row[13] or "",
            independent_variable=row[14] or "I",
            dependent_variable=row[15] or "T",
            variables=self._load_variables(row[16]),
            parameters=self._load_parameters(row[17]),
            x_min=float(row[18] or 1),
            x_max=float(row[19] or 20),
            notes=row[20] or "",
        )
