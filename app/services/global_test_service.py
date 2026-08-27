from pathlib import Path
import json
import sqlite3
from collections import Counter
from datetime import datetime


class GlobalTestService:
    """
    Global test-history and dashboard service.

    Test records remain inside each project's testing.db.
    This service aggregates them across every project.
    """

    def __init__(self, projects_dir):
        self.projects_dir = Path(projects_dir)

    # =========================================================
    # DASHBOARD STATISTICS
    # =========================================================

    def get_dashboard_statistics(
        self,
        start_date=None,
        end_date=None,
    ):
        """
        Return global testing statistics for an inclusive date range.

        A component test is counted as ONE test session, regardless of
        how many measurements/phase rows it contains.

        Protection tests are treated as Numerical Relay tests because
        they are stored in protection_tests and reference relay_id.
        """

        records = self._load_all_test_records()

        if start_date:
            start_date = str(start_date)

        if end_date:
            end_date = str(end_date)

        filtered = [
            record
            for record in records
            if self._date_in_range(
                record.get("date"),
                start_date,
                end_date,
            )
        ]

        by_component_type = Counter()
        by_result = Counter()
        by_type_result = {}

        for record in filtered:

            component_type = (
                record.get("component_type")
                or "Unknown"
            )

            component_type = self._pretty_component_type(
                component_type
            )

            result = str(
                record.get("result")
                or ""
            ).strip().upper()

            if not result:
                result = "NOT TESTED"

            by_component_type[
                component_type
            ] += 1

            by_result[result] += 1

            if component_type not in by_type_result:
                by_type_result[
                    component_type
                ] = Counter()

            by_type_result[
                component_type
            ][result] += 1

        monthly = Counter()

        for record in filtered:
            date_value = record.get("date")

            if not date_value:
                continue

            try:
                parsed = self._parse_date(
                    date_value
                )

                monthly[
                    parsed.strftime("%Y-%m")
                ] += 1

            except Exception:
                pass

        return {
            "total": len(filtered),
            "pass": by_result.get("PASS", 0),
            "fail": by_result.get("FAIL", 0),
            "not_tested": by_result.get(
                "NOT TESTED",
                0
            ),
            "by_component_type": dict(
                sorted(
                    by_component_type.items(),
                    key=lambda item: (
                        -item[1],
                        item[0],
                    ),
                )
            ),
            "by_type_result": {
                key: dict(value)
                for key, value in sorted(
                    by_type_result.items()
                )
            },
            "monthly": dict(
                sorted(
                    monthly.items()
                )
            ),
            "records": filtered,
        }

    # =========================================================
    # COMPLETE GLOBAL HISTORY
    # =========================================================

    def get_all_test_records(self):
        return self._load_all_test_records()

    # =========================================================
    # ASSET-SPECIFIC HISTORY
    # =========================================================

    def get_history(
        self,
        asset,
        component=None,
    ):
        if not isinstance(asset, dict):
            return []

        panel_asset_ids = self._get_descendant_panel_ids(
            asset
        )

        if not panel_asset_ids:
            return []

        component_name = ""
        component_type = ""

        if isinstance(component, dict):
            component_name = self._clean(
                component.get("name", "")
            )
            component_type = self._clean(
                component.get(
                    "component_type",
                    ""
                )
            ).upper()

        history = []

        for record in self._load_all_test_records():

            if record.get(
                "panel_asset_id"
            ) not in panel_asset_ids:
                continue

            if component is not None:

                if self._clean(
                    record.get("component", "")
                ).lower() != component_name.lower():
                    continue

                record_type = self._clean(
                    record.get(
                        "component_type",
                        ""
                    )
                ).upper()

                if (
                    component_type
                    and record_type != component_type
                ):
                    continue

            history.append(
                record
            )

        history.sort(
            key=lambda item: str(
                item.get("date", "")
            ),
            reverse=True,
        )

        return history

    # =========================================================
    # PROJECT DATABASE SCAN
    # =========================================================

    def _load_all_test_records(self):

        records = []

        for project_folder in self._project_folders():

            database_path = (
                project_folder
                /
                "testing.db"
            )

            if not database_path.exists():
                continue

            components = self._load_json(
                project_folder
                /
                "components.json",
                []
            )

            assets = self._load_json(
                project_folder
                /
                "assets.json",
                []
            )

            component_map = {
                str(
                    item.get("component_id")
                ): item
                for item in components
                if item.get("component_id")
            }

            panel_map = {
                str(
                    item.get("node_id")
                ): item
                for item in assets
                if item.get("node_id")
            }

            # Some project assets.json formats may use asset_id
            # instead of node_id.
            for item in assets:
                if item.get("asset_id"):
                    panel_map.setdefault(
                        str(
                            item.get("asset_id")
                        ),
                        item,
                    )

            try:
                connection = sqlite3.connect(
                    str(database_path)
                )

                protection_rows = self._safe_query(
                    connection,
                    """
                    SELECT
                        test_id,
                        project_id,
                        panel_id,
                        relay_id,
                        protection_code,
                        test_date,
                        result,
                        remarks
                    FROM protection_tests
                    ORDER BY test_date DESC
                    """
                )

                component_rows = self._safe_query(
                    connection,
                    """
                    SELECT
                        test_id,
                        project_id,
                        panel_id,
                        component_id,
                        test_type,
                        test_date,
                        measurements_json,
                        result,
                        remarks
                    FROM component_tests
                    ORDER BY test_date DESC
                    """
                )

            finally:
                try:
                    connection.close()
                except Exception:
                    pass

            project_name = project_folder.name

            # -------------------------------------------------
            # PROTECTION TESTS
            # -------------------------------------------------

            for row in protection_rows:

                if len(row) < 8:
                    continue

                relay_id = row[3]

                component = component_map.get(
                    str(relay_id),
                    {}
                )

                records.append({
                    "test_id": row[0],
                    "project_id": row[1],
                    "project": project_name,
                    "panel_id": row[2],
                    "panel": self._panel_name(
                        panel_map.get(
                            str(row[2]),
                            {}
                        )
                    ),
                    "component_id": relay_id,
                    "component": self._component_name(
                        component,
                        relay_id,
                    ),
                    "component_type": "NUMERICAL_RELAY",
                    "test_type": "PROTECTION",
                    "test_function": row[4] or "",
                    "date": row[5] or "",
                    "result": row[6] or "",
                    "remarks": row[7] or "",
                    "record_type": "PROTECTION",
                })

            # -------------------------------------------------
            # COMPONENT TESTS
            # -------------------------------------------------

            for row in component_rows:

                if len(row) < 9:
                    continue

                component_id = row[3]

                component = component_map.get(
                    str(component_id),
                    {}
                )

                records.append({
                    "test_id": row[0],
                    "project_id": row[1],
                    "project": project_name,
                    "panel_id": row[2],
                    "panel": self._panel_name(
                        panel_map.get(
                            str(row[2]),
                            {}
                        )
                    ),
                    "component_id": component_id,
                    "component": self._component_name(
                        component,
                        component_id,
                    ),
                    "component_type": self._infer_component_type(
                        component,
                        row[4],
                    ),
                    "test_type": row[4] or "COMPONENT",
                    "test_function": self._test_function(
                        row[6],
                        row[4],
                    ),
                    "date": row[5] or "",
                    "result": row[7] or "",
                    "remarks": row[8] or "",
                    "record_type": "COMPONENT",
                })

        return records

    # =========================================================
    # HELPERS
    # =========================================================

    def _project_folders(self):
        if not self.projects_dir.exists():
            return []

        return [
            folder
            for folder in self.projects_dir.iterdir()
            if folder.is_dir()
        ]

    @staticmethod
    def _safe_query(
        connection,
        query,
    ):
        try:
            return connection.execute(
                query
            ).fetchall()
        except sqlite3.Error:
            return []

    @staticmethod
    def _load_json(
        path,
        default,
    ):
        try:
            with open(
                path,
                "r",
                encoding="utf-8",
            ) as file:
                return json.load(file)
        except Exception:
            return default

    @staticmethod
    def _clean(value):
        return str(
            value
            if value is not None
            else ""
        ).strip()

    @staticmethod
    def _panel_name(panel):
        if not isinstance(panel, dict):
            return ""

        return str(
            panel.get("name")
            or panel.get("asset_tag")
            or ""
        )

    @staticmethod
    def _component_name(
        component,
        fallback="",
    ):
        if not isinstance(component, dict):
            return str(
                fallback or ""
            )

        return str(
            component.get("name")
            or fallback
            or ""
        )

    @staticmethod
    def _infer_component_type(
        component,
        test_type,
    ):
        if isinstance(component, dict):

            value = (
                component.get(
                    "component_type"
                )
                or component.get(
                    "type"
                )
            )

            if value:
                return str(
                    value
                ).upper()

        value = str(
            test_type
            or ""
        ).strip().upper()

        mapping = {
            "CT": "CT",
            "AUX_RELAY": "AUXILIARY_RELAY",
            "AUX RELAY": "AUXILIARY_RELAY",
            "METER": "METER",
            "RELAY": "NUMERICAL_RELAY",
            "NUMERICAL_RELAY": "NUMERICAL_RELAY",
        }

        return mapping.get(
            value,
            value or "UNKNOWN",
        )

    @staticmethod
    def _test_function(
        measurements_json,
        test_type,
    ):
        try:
            measurements = json.loads(
                measurements_json
            ) if measurements_json else {}

            if isinstance(
                measurements,
                dict
            ):
                if measurements.get(
                    "phase_tests"
                ):
                    return "RATIO / PHASE TEST"

                if measurements.get(
                    "functions"
                ):
                    return "METER FUNCTIONS"

        except Exception:
            pass

        return str(
            test_type
            or ""
        )

    @staticmethod
    def _pretty_component_type(
        value
    ):
        value = str(
            value
            or "Unknown"
        ).strip().upper()

        mapping = {
            "CT": "CT",
            "CURRENT TRANSFORMER": "CT",
            "NUMERICAL_RELAY": "Numerical Relay",
            "NUMERICAL RELAY": "Numerical Relay",
            "AUXILIARY_RELAY": "Auxiliary Relay",
            "AUX RELAY": "Auxiliary Relay",
            "METER": "Meter",
            "AMMETER": "Meter",
            "VOLTMETER": "Meter",
            "MULTIFUNCTION_METER": "Meter",
            "MULTIFUNCTION METER": "Meter",
        }

        return mapping.get(
            value,
            value.replace("_", " ").title(),
        )

    @staticmethod
    def _parse_date(value):
        value = str(
            value
        ).strip()

        formats = (
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
        )

        for fmt in formats:
            try:
                return datetime.strptime(
                    value,
                    fmt,
                )
            except ValueError:
                continue

        # ISO fallback.
        return datetime.fromisoformat(
            value.replace(
                "Z",
                ""
            )
        )

    @classmethod
    def _date_in_range(
        cls,
        value,
        start_date,
        end_date,
    ):
        if not value:
            return False

        try:
            date_value = cls._parse_date(
                value
            ).date()
        except Exception:
            return False

        if start_date:
            start = cls._parse_date(
                start_date
            ).date()

            if date_value < start:
                return False

        if end_date:
            end = cls._parse_date(
                end_date
            ).date()

            if date_value > end:
                return False

        return True

    def _get_descendant_panel_ids(
        self,
        asset,
    ):
        assets = self._get_all_global_assets()

        selected_id = asset.get(
            "asset_id"
        )

        if not selected_id:
            return set()

        children = {}

        for item in assets:
            metadata = (
                item.get("metadata")
                or {}
            )

            parent_id = metadata.get(
                "parent_asset_id"
            )

            if parent_id:
                children.setdefault(
                    parent_id,
                    []
                ).append(
                    item
                )

        panel_ids = set()
        pending = [selected_id]
        visited = set()

        while pending:

            current_id = pending.pop()

            if current_id in visited:
                continue

            visited.add(
                current_id
            )

            current = next(
                (
                    item
                    for item in assets
                    if item.get("asset_id")
                    == current_id
                ),
                None,
            )

            if current is None:
                continue

            asset_type = str(
                current.get(
                    "asset_type",
                    ""
                )
            ).upper()

            if asset_type == "PANEL":
                panel_ids.add(
                    current_id
                )

            for child in children.get(
                current_id,
                []
            ):
                child_id = child.get(
                    "asset_id"
                )

                if child_id:
                    pending.append(
                        child_id
                    )

        return panel_ids

    def _get_all_global_assets(self):
        try:
            from app.services.asset_library_manager import (
                AssetLibraryManager
            )

            library = AssetLibraryManager()

            try:
                library.load()
            except Exception:
                pass

            return (
                library.get_all_assets()
                or []
            )

        except Exception:
            return []
