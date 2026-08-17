import json
import uuid
from datetime import datetime


class TestService:

    def __init__(
        self,
        database
    ):

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

    @staticmethod
    def _load_json(
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

        test_id = (
            self._generate_test_id()
        )

        test_date = (
            self._current_timestamp()
        )

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
                json.dumps(
                    settings or {}
                ),
                json.dumps(
                    measurements or {}
                ),
                result,
                remarks
            )
        )

        return test_id

    # =====================================================
    # SAVE COMPONENT TEST
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

        test_id = (
            self._generate_test_id()
        )

        test_date = (
            self._current_timestamp()
        )

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
# UPDATE COMPONENT TEST
# =====================================================

    def update_component_test(
        self,
        test_id,
        measurements,
        result="NOT TESTED",
        remarks=""
    ):

        existing = self.get_component_test(
            test_id
        )

        if existing is None:

            raise ValueError(
                f"Component test '{test_id}' "
                "was not found."
            )

        self.database.execute(
            """
            UPDATE component_tests

            SET
                measurements_json = ?,
                result = ?,
                remarks = ?

            WHERE test_id = ?
            """,
            (
                json.dumps(
                    measurements or {}
                ),
                result,
                remarks,
                test_id
            )
        )

        return test_id
    # =====================================================
    # GET ALL PROTECTION TESTS
    # =====================================================

    def get_all_tests(self):

        return self.database.fetch_all(
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

        if row is None:

            return None

        return {

            "test_id":
                row[0],

            "project_id":
                row[1],

            "panel_id":
                row[2],

            "relay_id":
                row[3],

            "protection_code":
                row[4],

            "test_date":
                row[5],

            "settings":
                self._load_json(
                    row[6]
                ),

            "measurements":
                self._load_json(
                    row[7]
                ),

            "result":
                row[8],

            "remarks":
                row[9],
        }

    # =====================================================
    # GET ALL COMPONENT TESTS
    # =====================================================

    def get_all_component_tests(self):

        return self.database.fetch_all(
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

        if row is None:

            return None

        return {

            "test_id":
                row[0],

            "project_id":
                row[1],

            "panel_id":
                row[2],

            "component_id":
                row[3],

            "test_type":
                row[4],

            "test_date":
                row[5],

            "measurements":
                self._load_json(
                    row[6]
                ),

            "result":
                row[7],

            "remarks":
                row[8],
        }

    # =====================================================
    # GET PANEL COMPONENT TESTS
    # =====================================================

    def get_component_tests_for_panel(
        self,
        project_id,
        panel_id
    ):

        return self.database.fetch_all(
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
                project_id = ?
                AND panel_id = ?

            ORDER BY
                test_date DESC
            """,
            (
                project_id,
                panel_id
            )
        )