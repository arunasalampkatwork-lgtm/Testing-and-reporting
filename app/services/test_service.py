import json
import uuid
from datetime import datetime


class TestService:

    def __init__(self, database):
        self.database = database

    # =====================================================
    # INTERNAL HELPERS
    # =====================================================

    def _generate_test_id(self):
        return (
            "TEST-"
            + uuid.uuid4().hex[:8].upper()
        )

    def _current_timestamp(self):
        return datetime.now().isoformat(
            timespec="seconds"
        )

    # =====================================================
    # SAVE PROTECTION TEST
    # =====================================================

    def save_protection_test(
        self,
        project_id,
        panel_id,
        relay_id,
        protection_code,
        settings,
        measurements,
        result="NOT TESTED",
        remarks=""
    ):

        test_id = self._generate_test_id()

        test_date = self._current_timestamp()

        self.database.execute(
            """
            INSERT INTO protection_tests (

                test_id,
                project_id,
                panel_id,
                relay_id,
                protection_code,
                test_date,
                settings_json,
                measurements_json,
                result,
                remarks

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,

            (
                test_id,
                project_id,
                panel_id,
                relay_id,
                protection_code,
                test_date,
                json.dumps(settings or {}),
                json.dumps(measurements or {}),
                result,
                remarks
            )
        )

        return test_id

    # =====================================================
    # SAVE COMPONENT TEST
    #
    # Used by:
    #   CTTestingDialog
    #   AuxRelayTestingDialog
    #
    # Examples:
    #
    #   test_type = "CT"
    #
    #   test_type = "AUX_RELAY"
    # =====================================================

    def save_component_test(
        self,
        project_id,
        panel_id,
        component_id,
        test_type,
        measurements,
        result="NOT TESTED",
        remarks=""
    ):

        test_id = self._generate_test_id()

        test_date = self._current_timestamp()

        self.database.execute(
            """
            INSERT INTO component_tests (

                test_id,
                project_id,
                panel_id,
                component_id,
                test_type,
                test_date,
                measurements_json,
                result,
                remarks

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,

            (
                test_id,
                project_id,
                panel_id,
                component_id,
                test_type,
                test_date,
                json.dumps(
                    measurements or {}
                ),
                result,
                remarks
            )
        )

        return test_id

    # =====================================================
    # GET ALL PROTECTION TESTS
    # =====================================================

    def get_all_tests(self):

        rows = self.database.fetch_all(
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

        return rows

    # =====================================================
    # GET ONE PROTECTION TEST
    # =====================================================

    def get_test(
        self,
        test_id
    ):

        row = self.database.fetch_one(
            """
            SELECT
                test_id,
                project_id,
                panel_id,
                relay_id,
                protection_code,
                test_date,
                settings_json,
                measurements_json,
                result,
                remarks

            FROM protection_tests

            WHERE test_id = ?
            """,

            (
                test_id,
            )
        )

        if not row:
            return None

        return {

            "test_id": row[0],

            "project_id": row[1],

            "panel_id": row[2],

            "relay_id": row[3],

            "protection_code": row[4],

            "test_date": row[5],

            "settings": self._load_json(
                row[6]
            ),

            "measurements": self._load_json(
                row[7]
            ),

            "result": row[8],

            "remarks": row[9]
        }

    # =====================================================
    # GET ALL COMPONENT TESTS
    # =====================================================

    def get_all_component_tests(self):

        rows = self.database.fetch_all(
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

        return rows

    # =====================================================
    # GET ONE COMPONENT TEST
    # =====================================================

    def get_component_test(
        self,
        test_id
    ):

        row = self.database.fetch_one(
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

            WHERE test_id = ?
            """,

            (
                test_id,
            )
        )

        if not row:
            return None

        return {

            "test_id": row[0],

            "project_id": row[1],

            "panel_id": row[2],

            "component_id": row[3],

            "test_type": row[4],

            "test_date": row[5],

            "measurements": self._load_json(
                row[6]
            ),

            "result": row[7],

            "remarks": row[8]
        }

    # =====================================================
    # GET COMPONENT TESTS
    #
    # Useful for:
    #
    #   CT-1 test history
    #   AUX-1 test history
    #   future report generation
    # =====================================================

    def get_component_tests(
        self,
        component_id
    ):

        rows = self.database.fetch_all(
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

            WHERE component_id = ?

            ORDER BY test_date DESC
            """,

            (
                component_id,
            )
        )

        results = []

        for row in rows:

            results.append({

                "test_id": row[0],

                "project_id": row[1],

                "panel_id": row[2],

                "component_id": row[3],

                "test_type": row[4],

                "test_date": row[5],

                "measurements": self._load_json(
                    row[6]
                ),

                "result": row[7],

                "remarks": row[8]
            })

        return results

    # =====================================================
    # GET COMPONENT TESTS BY TYPE
    # =====================================================

    def get_component_tests_by_type(
        self,
        component_id,
        test_type
    ):

        rows = self.database.fetch_all(
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

            WHERE
                component_id = ?
                AND test_type = ?

            ORDER BY test_date DESC
            """,

            (
                component_id,
                test_type
            )
        )

        results = []

        for row in rows:

            results.append({

                "test_id": row[0],

                "project_id": row[1],

                "panel_id": row[2],

                "component_id": row[3],

                "test_type": row[4],

                "test_date": row[5],

                "measurements": self._load_json(
                    row[6]
                ),

                "result": row[7],

                "remarks": row[8]
            })

        return results

    # =====================================================
    # GET LATEST COMPONENT TEST
    # =====================================================

    def get_latest_component_test(
        self,
        component_id,
        test_type=None
    ):

        if test_type:

            row = self.database.fetch_one(
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

                WHERE
                    component_id = ?
                    AND test_type = ?

                ORDER BY test_date DESC

                LIMIT 1
                """,

                (
                    component_id,
                    test_type
                )
            )

        else:

            row = self.database.fetch_one(
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

                WHERE component_id = ?

                ORDER BY test_date DESC

                LIMIT 1
                """,

                (
                    component_id,
                )
            )

        if not row:
            return None

        return {

            "test_id": row[0],

            "project_id": row[1],

            "panel_id": row[2],

            "component_id": row[3],

            "test_type": row[4],

            "test_date": row[5],

            "measurements": self._load_json(
                row[6]
            ),

            "result": row[7],

            "remarks": row[8]
        }

    # =====================================================
    # INTERNAL JSON LOADER
    # =====================================================

    def _load_json(
        self,
        value
    ):

        if not value:
            return {}

        try:

            return json.loads(
                value
            )

        except (
            json.JSONDecodeError,
            TypeError
        ):

            return {}