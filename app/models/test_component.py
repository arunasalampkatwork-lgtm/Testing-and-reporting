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

        # CT
        ct_ratio="",
        ct_class="",
        burden="",
        core="",

        # Numerical relay
        vt_ratio="",
        firmware="",

        # Auxiliary relay
        coil_voltage="",
        contact_configuration="",

        # Protection functions
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

        self.ct_ratio = ct_ratio

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

        if protection_functions is None:
            protection_functions = []

        self.protection_functions = (
            protection_functions
        )

    def __repr__(self):

        return (
            f"TestComponent("
            f"id={self.component_id!r}, "
            f"name={self.name!r}, "
            f"type={self.component_type!r}, "
            f"panel={self.panel_id!r}"
            f")"
        )