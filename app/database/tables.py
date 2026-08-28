def create_tables(database):

    # =====================================================
    # PROTECTION TESTS
    #
    # Used for numerical relay protection functions:
    #
    # 50
    # 51
    # 50N
    # 51N
    # 46
    # 27
    # 59
    # 81U
    # 81O
    # 81R
    # 67
    # 67N
    # 87
    # 87T
    # 87M
    # 49
    # etc.
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

    # =====================================================
    # THERMAL TEMPLATES
    #
    # A thermal template belongs to:
    #
    # protection function
    #       +
    # manufacturer
    #       +
    # relay model
    #
    # Curve points are stored as JSON.
    # =====================================================

    database.execute(
        """
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

            notes TEXT,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL,

            UNIQUE (
                protection_function,
                manufacturer,
                model,
                name
            )

        )
        """
    )

    # =====================================================
    # INDEX
    #
    # Makes relay/template lookup fast.
    # =====================================================

    database.execute(
        """
        CREATE INDEX IF NOT EXISTS
        idx_thermal_templates_relay

        ON thermal_templates (
            protection_function,
            manufacturer,
            model
        )
        """
    )