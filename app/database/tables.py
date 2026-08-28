def create_tables(database):
    database.execute("""
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
    """)

    database.execute("""
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
    """)

    database.execute("""
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
            UNIQUE(protection_function, manufacturer, model, name)
        )
    """)

    # Existing installations may already have the original thermal table.
    # Add the equation-builder columns without destroying existing templates.
    columns = {
        row[1] for row in database.fetch_all("PRAGMA table_info(thermal_templates)")
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
            database.execute(sql)

    database.execute("""
        CREATE INDEX IF NOT EXISTS idx_thermal_templates_relay
        ON thermal_templates(protection_function, manufacturer, model)
    """)
