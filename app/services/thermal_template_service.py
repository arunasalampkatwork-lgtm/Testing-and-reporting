import json
import uuid
from datetime import datetime

from app.models.thermal_template import (
    ThermalTemplate,
    ThermalCurvePoint,
    ThermalVariable,
)


class ThermalTemplateService:
    """Persistence and retrieval for relay-specific thermal templates."""

    def __init__(self, database):
        self.database = database

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
                "current_multiple": float(point.current_multiple),
                "operating_time": float(point.operating_time),
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
                result.append(ThermalCurvePoint(
                    current_multiple=float(item["current_multiple"]),
                    operating_time=float(item["operating_time"]),
                ))
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
                result.append(ThermalVariable(
                    name=str(item["name"]),
                    unit=str(item.get("unit", "")),
                    description=str(item.get("description", "")),
                    default_value=float(item.get("default_value", 0)),
                    is_input=bool(item.get("is_input", False)),
                ))
            except (KeyError, TypeError, ValueError):
                continue
        return result

    @staticmethod
    def _dump_parameters(parameters):
        return json.dumps({
            str(k): float(v)
            for k, v in (parameters or {}).items()
        })

    @staticmethod
    def _load_parameters(value):
        if not value:
            return {}
        try:
            data = json.loads(value)
            return {str(k): float(v) for k, v in data.items()}
        except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
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

    def create_template(
        self, protection_function, manufacturer, model, name,
        curve_type="POINT_TABLE", rated_current=0.0, pickup_current=1.0,
        thermal_constant=0.0, cooling_constant=0.0, curves=None,
        heating_curve=None, cooling_curve=None, equation="",
        independent_variable="I", dependent_variable="T", variables=None,
        parameters=None, x_min=1.0, x_max=20.0, notes="",
    ):
        protection_function = self._normalize(protection_function)
        manufacturer = self._normalize(manufacturer)
        model = self._normalize(model)
        name = self._normalize(name)
        if not protection_function:
            raise ValueError("Protection function is required.")
        if not manufacturer:
            raise ValueError("Manufacturer is required.")
        if not model:
            raise ValueError("Relay model is required.")
        if not name:
            raise ValueError("Template name is required.")

        existing = self.database.fetch_one(
            """
            SELECT template_id FROM thermal_templates
            WHERE protection_function = ?
              AND LOWER(manufacturer) = LOWER(?)
              AND LOWER(model) = LOWER(?)
              AND LOWER(name) = LOWER(?)
            """,
            (protection_function, manufacturer, model, name),
        )
        if existing is not None:
            raise ValueError("A thermal template with the same name already exists for this relay.")

        template_id = self._generate_template_id()
        timestamp = self._timestamp()
        self.database.execute(
            f"""
            INSERT INTO thermal_templates (
                template_id, protection_function, manufacturer, model, name,
                curve_type, rated_current, pickup_current, thermal_constant,
                cooling_constant, curve_json, heating_curve_json,
                cooling_curve_json, equation, independent_variable,
                dependent_variable, variables_json, parameters_json,
                x_min, x_max, notes, created_at, updated_at
            ) VALUES ({', '.join(['?'] * 23)})
            """,
            (
                template_id, protection_function, manufacturer, model, name,
                curve_type, float(rated_current or 0), float(pickup_current or 1),
                float(thermal_constant or 0), float(cooling_constant or 0),
                self._dump_curve(curves), self._dump_curve(heating_curve),
                self._dump_curve(cooling_curve), str(equation or ""),
                str(independent_variable or "I"), str(dependent_variable or "T"),
                self._dump_variables(variables), self._dump_parameters(parameters),
                float(x_min), float(x_max), str(notes or ""), timestamp, timestamp,
            ),
        )
        return template_id

    def update_template(self, template_id, **kwargs):
        existing = self.get_template(template_id)
        if existing is None:
            raise ValueError(f"Thermal template '{template_id}' was not found.")
        allowed = {
            "protection_function", "manufacturer", "model", "name", "curve_type",
            "rated_current", "pickup_current", "thermal_constant", "cooling_constant",
            "curves", "heating_curve", "cooling_curve", "equation", "independent_variable",
            "dependent_variable", "variables", "parameters", "x_min", "x_max", "notes",
        }
        data = {k: v for k, v in kwargs.items() if k in allowed}
        data.setdefault("protection_function", existing.protection_function)
        data.setdefault("manufacturer", existing.manufacturer)
        data.setdefault("model", existing.model)
        data.setdefault("name", existing.name)
        data.setdefault("curve_type", existing.curve_type)
        data.setdefault("rated_current", existing.rated_current)
        data.setdefault("pickup_current", existing.pickup_current)
        data.setdefault("thermal_constant", existing.thermal_constant)
        data.setdefault("cooling_constant", existing.cooling_constant)
        data.setdefault("curves", existing.curves)
        data.setdefault("heating_curve", existing.heating_curve)
        data.setdefault("cooling_curve", existing.cooling_curve)
        data.setdefault("equation", existing.equation)
        data.setdefault("independent_variable", existing.independent_variable)
        data.setdefault("dependent_variable", existing.dependent_variable)
        data.setdefault("variables", existing.variables)
        data.setdefault("parameters", existing.parameters)
        data.setdefault("x_min", existing.x_min)
        data.setdefault("x_max", existing.x_max)
        data.setdefault("notes", existing.notes)
        timestamp = self._timestamp()
        self.database.execute(
            """
            UPDATE thermal_templates SET
                protection_function=?, manufacturer=?, model=?, name=?, curve_type=?,
                rated_current=?, pickup_current=?, thermal_constant=?, cooling_constant=?,
                curve_json=?, heating_curve_json=?, cooling_curve_json=?, equation=?,
                independent_variable=?, dependent_variable=?, variables_json=?,
                parameters_json=?, x_min=?, x_max=?, notes=?, updated_at=?
            WHERE template_id=?
            """,
            (
                data["protection_function"], data["manufacturer"], data["model"], data["name"],
                data["curve_type"], float(data["rated_current"] or 0), float(data["pickup_current"] or 1),
                float(data["thermal_constant"] or 0), float(data["cooling_constant"] or 0),
                self._dump_curve(data["curves"]), self._dump_curve(data["heating_curve"]),
                self._dump_curve(data["cooling_curve"]), str(data["equation"] or ""),
                str(data["independent_variable"] or "I"), str(data["dependent_variable"] or "T"),
                self._dump_variables(data["variables"]), self._dump_parameters(data["parameters"]),
                float(data["x_min"]), float(data["x_max"]), str(data["notes"] or ""), timestamp,
                template_id,
            ),
        )
        return template_id

    def delete_template(self, template_id):
        self.database.execute("DELETE FROM thermal_templates WHERE template_id=?", (template_id,))

    def get_template(self, template_id):
        row = self.database.fetch_one(
            f"SELECT {self._select_columns()} FROM thermal_templates WHERE template_id=?",
            (template_id,),
        )
        return self._row_to_template(row) if row else None

    def _query(self, sql, params=()):
        rows = self.database.fetch_all(sql, params)
        return [self._row_to_template(row) for row in rows]

    def get_templates_for_relay(self, manufacturer, model, protection_function="49"):
        return self._query(
            f"""SELECT {self._select_columns()} FROM thermal_templates
                WHERE protection_function=? AND LOWER(manufacturer)=LOWER(?)
                AND LOWER(model)=LOWER(?) ORDER BY name""",
            (protection_function, manufacturer, model),
        )

    def get_templates_for_function(self, protection_function="49"):
        return self._query(
            f"""SELECT {self._select_columns()} FROM thermal_templates
                WHERE protection_function=? ORDER BY manufacturer, model, name""",
            (protection_function,),
        )

    def get_all_templates(self):
        return self._query(
            f"SELECT {self._select_columns()} FROM thermal_templates ORDER BY manufacturer, model, name"
        )

    def _row_to_template(self, row):
        return ThermalTemplate(
            template_id=row[0], protection_function=row[1], manufacturer=row[2], model=row[3],
            name=row[4], curve_type=row[5], rated_current=float(row[6] or 0),
            pickup_current=float(row[7] or 1), thermal_constant=float(row[8] or 0),
            cooling_constant=float(row[9] or 0), curves=self._load_curve(row[10]),
            heating_curve=self._load_curve(row[11]), cooling_curve=self._load_curve(row[12]),
            equation=row[13] or "", independent_variable=row[14] or "I",
            dependent_variable=row[15] or "T", variables=self._load_variables(row[16]),
            parameters=self._load_parameters(row[17]), x_min=float(row[18] or 1),
            x_max=float(row[19] or 20), notes=row[20] or "",
        )
