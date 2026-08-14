def create_tables(database):

    # =====================================================
    # PROTECTION TESTS
    #
    # Used for numerical relay protection functions:
    # 50, 51, 50N, 51N, 27, 59, 81U, 81O, 81R,
    # 67, 67N, 87, 87T, 87M, etc.
    # =====================================================

    database.execute(
        """
        CREATE TABLE IF NOT EXISTS protection_tests (

            test_id TEXT PRIMARY KEY,

            project_id TEXT NOT NULL,

            panel_id TEXT NOT NULL,

            relay_id TEXT NOT NULL,

            protection_code TEXT NOT NULL,

            test_date TEXT NOT NULL,

            settings_json TEXT,

            measurements_json TEXT,

            result TEXT,

            remarks TEXT

        )
        """
    )

    # =====================================================
    # COMPONENT TESTS
    #
    # Used for equipment/components that are not individual
    # relay protection functions.
    #
    # Examples:
    #
    #   CT
    #   AUX_RELAY
    #   Future:
    #   CB
    #   VT
    #   BATTERY
    #   etc.
    # =====================================================

    database.execute(
        """
        CREATE TABLE IF NOT EXISTS component_tests (

            test_id TEXT PRIMARY KEY,

            project_id TEXT NOT NULL,

            panel_id TEXT NOT NULL,

            component_id TEXT NOT NULL,

            test_type TEXT NOT NULL,

            test_date TEXT NOT NULL,

            measurements_json TEXT,

            result TEXT,

            remarks TEXT

        )
        """
    )