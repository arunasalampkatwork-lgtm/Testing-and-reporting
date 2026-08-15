class TestComponent:

    def __init__(
        self,
        component_id,
        panel_id,
        component_type,
        name,

        manufacturer="",
        model="",
        serial_number="",
        description="",

        # =================================================
        # CT
        # =================================================

        ct_primary=0.0,
        ct_secondary=0.0,
        ct_ratio="",
        ct_class="",
        burden="",
        core="",

        # =================================================
        # NUMERICAL RELAY
        # =================================================

        vt_ratio="",
        firmware="",

        # =================================================
        # AUXILIARY RELAY
        # =================================================

        coil_voltage="",
        contact_configuration="",

        # =================================================
        # PROTECTION FUNCTIONS
        # =================================================

        protection_functions=None
    ):

        self.component_id = component_id

        self.panel_id = panel_id

        self.component_type = component_type

        self.name = name

        # =================================================
        # COMMON
        # =================================================

        self.manufacturer = manufacturer

        self.model = model

        self.serial_number = serial_number

        self.description = description

        # =================================================
        # CT
        # =================================================

        self.ct_primary = (
            self._to_float(
                ct_primary
            )
        )

        self.ct_secondary = (
            self._to_float(
                ct_secondary
            )
        )

        self.ct_ratio = (
            str(
                ct_ratio
                or ""
            ).strip()
        )

        # Automatically construct ratio when possible.
        if (
            not self.ct_ratio
            and self.ct_primary > 0
            and self.ct_secondary > 0
        ):

            self.ct_ratio = (
                f"{self.ct_primary:g}/"
                f"{self.ct_secondary:g}"
            )

        self.ct_class = ct_class

        self.burden = burden

        self.core = core

        # =================================================
        # NUMERICAL RELAY
        # =================================================

        self.vt_ratio = vt_ratio

        self.firmware = firmware

        # =================================================
        # AUXILIARY RELAY
        # =================================================

        self.coil_voltage = coil_voltage

        self.contact_configuration = (
            contact_configuration
        )

        # =================================================
        # PROTECTION FUNCTIONS
        # =================================================

        self.protection_functions = (
            list(
                protection_functions
                or []
            )
        )

    # =====================================================
    # FLOAT CONVERSION
    # =====================================================

    @staticmethod
    def _to_float(
        value
    ):

        try:

            return float(
                value
                or 0
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0

    # =====================================================
    # NOMINAL CURRENT
    # =====================================================

    @property
    def nominal_current(self):

        """
        CT secondary current is the relay nominal current.

        Example:

            1000/5 → In = 5 A
            1000/1 → In = 1 A
        """

        return self.ct_secondary

    # =====================================================
    # CT RATIO DISPLAY
    # =====================================================

    def get_ct_ratio_display(self):

        if (
            self.ct_primary > 0
            and self.ct_secondary > 0
        ):

            return (
                f"{self.ct_primary:g}/"
                f"{self.ct_secondary:g}"
            )

        return self.ct_ratio

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):

        return (
            f"TestComponent("
            f"id={self.component_id!r}, "
            f"name={self.name!r}, "
            f"type={self.component_type!r}, "
            f"panel={self.panel_id!r}"
            f")"
        )