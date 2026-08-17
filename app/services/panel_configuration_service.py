from copy import deepcopy


class PanelConfigurationService:
    """
    Handles selective copying of panel configuration.

    IMPORTANT:
        This service copies configuration only.

        It does NOT copy:
            - panel identity
            - panel node ID
            - component IDs
            - test history
            - test sessions
            - test results
    """

    # =====================================================
    # PANEL ATTRIBUTES
    # =====================================================

    PANEL_ATTRIBUTES = {

        "equipment_name":
            "Feed Equipment",

        "equipment_type":
            "Equipment Type",
    }

    # =====================================================
    # COMPONENT ATTRIBUTES
    # =====================================================

    COMPONENT_ATTRIBUTES = {

        "component_type":
            "Component Type",

        "manufacturer":
            "Manufacturer",

        "model":
            "Model",

        "serial_number":
            "Serial Number",

        "description":
            "Description",

        # -------------------------------------------------
        # CT
        # -------------------------------------------------

        "ct_primary":
            "CT Primary",

        "ct_secondary":
            "CT Secondary",

        "ct_ratio":
            "CT Ratio",

        "ct_class":
            "CT Class",

        "burden":
            "Burden",

        "core":
            "Core",

        # -------------------------------------------------
        # NUMERICAL RELAY
        # -------------------------------------------------

        "vt_ratio":
            "VT Ratio",

        "firmware":
            "Firmware",

        # -------------------------------------------------
        # AUXILIARY RELAY
        # -------------------------------------------------

        "coil_voltage":
            "Coil Voltage",

        "contact_configuration":
            "Contact Configuration",

        # -------------------------------------------------
        # METER
        # -------------------------------------------------

        "meter_type":
            "Meter Type",

        "meter_functions":
            "Meter Functions",

        "accuracy_class":
            "Accuracy Class",

        # -------------------------------------------------
        # PROTECTION
        # -------------------------------------------------

        "protection_functions":
            "Protection Functions",
    }

    # =====================================================
    # DEFAULT SELECTIONS
    # =====================================================

    # Values that normally differ from panel to panel.
    # These are intentionally unchecked by default.

    PANEL_DEFAULT_EXCLUDED = {
        "equipment_name",
        "equipment_type",
    }

    COMPONENT_DEFAULT_EXCLUDED = {
        "serial_number",
        "description",
    }

    # Component names are NEVER copied as configuration
    # because the new panel must retain its own generated
    # CT-01 / REL-01 / AUX-01 / M-01 structure.
    #
    # The name isn't included in COMPONENT_ATTRIBUTES
    # deliberately.

    # =====================================================
    # GET PANEL CONFIGURATION
    # =====================================================

    @classmethod
    def get_panel_configuration(
        cls,
        panel,
    ):

        return {

            "equipment_name":
                getattr(
                    panel,
                    "equipment_name",
                    ""
                ),

            "equipment_type":
                getattr(
                    panel,
                    "equipment_type",
                    ""
                ),

            "ct_count":
                cls._safe_int(
                    getattr(
                        panel,
                        "ct_count",
                        0
                    )
                ),

            "relay_count":
                cls._safe_int(
                    getattr(
                        panel,
                        "relay_count",
                        0
                    )
                ),

            "aux_count":
                cls._safe_int(
                    getattr(
                        panel,
                        "aux_count",
                        0
                    )
                ),

            "meter_count":
                cls._safe_int(
                    getattr(
                        panel,
                        "meter_count",
                        0
                    )
                ),
        }

    # =====================================================
    # GET COMPONENT CONFIGURATION
    # =====================================================

    @classmethod
    def get_component_configuration(
        cls,
        component,
    ):

        result = {}

        for field in cls.COMPONENT_ATTRIBUTES:

            value = getattr(
                component,
                field,
                ""
            )

            if isinstance(
                value,
                (list, tuple, set)
            ):

                value = list(
                    value
                )

            result[field] = deepcopy(
                value
            )

        return result

    # =====================================================
    # GET SOURCE PANEL SUMMARY
    # =====================================================

    @classmethod
    def get_source_summary(
        cls,
        panel,
        component_manager,
    ):

        components = (
            component_manager
            .get_panel_components(
                panel.node_id
            )
        )

        counts = {
            "CT": 0,
            "NUMERICAL_RELAY": 0,
            "AUXILIARY_RELAY": 0,
            "METER": 0,
        }

        for component in components:

            component_type = (
                str(
                    getattr(
                        component,
                        "component_type",
                        ""
                    )
                )
                .strip()
                .upper()
            )

            if component_type in (
                "CT",
                "CURRENT TRANSFORMER",
            ):

                counts["CT"] += 1

            elif component_type in (
                "NUMERICAL_RELAY",
                "NUMERICAL RELAY",
            ):

                counts[
                    "NUMERICAL_RELAY"
                ] += 1

            elif component_type in (
                "AUXILIARY_RELAY",
                "AUX RELAY",
                "AUXILIARY RELAY",
            ):

                counts[
                    "AUXILIARY_RELAY"
                ] += 1

            elif component_type in (
                "METER",
                "AMMETER",
                "VOLTMETER",
                "MULTIFUNCTION_METER",
                "MULTIFUNCTION METER",
            ):

                counts[
                    "METER"
                ] += 1

        return {

            "panel":
                panel,

            "components":
                components,

            "counts":
                counts,

            "panel_configuration":
                cls.get_panel_configuration(
                    panel
                ),
        }

    # =====================================================
    # APPLY CONFIGURATION
    # =====================================================

    @classmethod
    def apply_configuration(
        cls,
        source_panel,
        target_panel,
        source_components,
        target_component_manager,
        panel_fields=None,
        component_fields=None,
    ):
        """
        Apply selected configuration from source to target.

        Existing target components are replaced.

        This method is intended primarily for a newly-created
        panel. It never copies IDs or test history.
        """

        panel_fields = set(
            panel_fields
            or []
        )

        component_fields = set(
            component_fields
            or []
        )

        # -------------------------------------------------
        # PANEL CONFIGURATION
        # -------------------------------------------------

        panel_configuration = (
            cls.get_panel_configuration(
                source_panel
            )
        )

        selected_panel_configuration = {}

        for field in panel_fields:

            if field not in cls.PANEL_ATTRIBUTES:

                continue

            selected_panel_configuration[
                field
            ] = deepcopy(
                panel_configuration.get(
                    field,
                    ""
                )
            )

        # -------------------------------------------------
        # COMPONENT DATA
        # -------------------------------------------------

        component_data = []

        for source_component in (
            source_components
            or []
        ):

            data = {

                "component_type":
                    getattr(
                        source_component,
                        "component_type",
                        ""
                    ),

                # Keep source name.
                # The caller can regenerate names later
                # according to the target structure.
                "name":
                    getattr(
                        source_component,
                        "name",
                        ""
                    ),
            }

            for field in component_fields:

                if field not in (
                    cls.COMPONENT_ATTRIBUTES
                ):

                    continue

                value = getattr(
                    source_component,
                    field,
                    ""
                )

                if isinstance(
                    value,
                    (list, tuple, set)
                ):

                    value = list(
                        value
                    )

                data[field] = deepcopy(
                    value
                )

            component_data.append(
                data
            )

        # -------------------------------------------------
        # APPLY PANEL
        # -------------------------------------------------

        if selected_panel_configuration:

            cls._apply_panel_values(
                target_panel,
                selected_panel_configuration,
            )

        # -------------------------------------------------
        # REBUILD COMPONENTS
        # -------------------------------------------------

        target_components = (
            cls._build_target_components(
                source_components,
                component_fields,
                target_panel.node_id,
            )
        )

        # -------------------------------------------------
        # Replace target components
        # -------------------------------------------------

        cls._replace_components(
            target_component_manager,
            target_panel.node_id,
            target_components,
        )

        return {

            "panel_configuration":
                selected_panel_configuration,

            "components_created":
                len(
                    target_components
                ),
        }

    # =====================================================
    # APPLY PANEL VALUES
    # =====================================================

    @staticmethod
    def _apply_panel_values(
        target_panel,
        values,
    ):

        for field, value in (
            values.items()
        ):

            setattr(
                target_panel,
                field,
                value
            )

    # =====================================================
    # BUILD TARGET COMPONENTS
    # =====================================================

    @classmethod
    def _build_target_components(
        cls,
        source_components,
        selected_fields,
        target_panel_id,
    ):

        result = []

        for source_component in (
            source_components
            or []
        ):

            data = {

                "component_type":
                    getattr(
                        source_component,
                        "component_type",
                        ""
                    ),

                "name":
                    getattr(
                        source_component,
                        "name",
                        ""
                    ),
            }

            for field in selected_fields:

                if field not in (
                    cls.COMPONENT_ATTRIBUTES
                ):

                    continue

                value = getattr(
                    source_component,
                    field,
                    ""
                )

                if isinstance(
                    value,
                    (list, tuple, set)
                ):

                    value = list(
                        value
                    )

                data[field] = deepcopy(
                    value
                )

            result.append(
                data
            )

        return result

    # =====================================================
    # REPLACE COMPONENTS
    # =====================================================

    @staticmethod
    def _replace_components(
        component_manager,
        panel_id,
        component_data,
    ):

        # We deliberately use clone_panel_components()
        # because it generates NEW component IDs.

        component_manager.clone_panel_components(
            panel_id,
            component_data,
        )

    # =====================================================
    # SAFE INTEGER
    # =====================================================

    @staticmethod
    def _safe_int(
        value,
    ):

        try:

            return int(
                value or 0
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0