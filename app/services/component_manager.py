from pathlib import Path
import json
from uuid import uuid4

from app.models.test_component import TestComponent


class ComponentManager:

    def __init__(
        self,
        project_folder: Path
    ):

        self.project_folder = project_folder

        self.components_file = (
            project_folder / "components.json"
        )

        self.components = {}

        self.load_components()

    # =========================================================
    # ID
    # =========================================================

    def _generate_id(self):

        return (
            f"CMP-{uuid4().hex[:8].upper()}"
        )

    # =========================================================
    # CREATE COMPONENT
    # =========================================================

    def create_component(
        self,
        panel_id: str,
        component_type: str,
        name: str
    ):

        component_id = (
            self._generate_id()
        )

        component = TestComponent(

            component_id=component_id,

            panel_id=panel_id,

            component_type=component_type,

            name=name
        )

        self.components[
            component_id
        ] = component

        self.save_components()

        return component

    # =========================================================
    # GET COMPONENT
    # =========================================================

    def get_component(
        self,
        component_id
    ):

        return self.components.get(
            component_id
        )

    # =========================================================
    # GET COMPONENTS FOR PANEL
    # =========================================================

    def get_panel_components(
        self,
        panel_id: str
    ):

        return [

            component

            for component
            in self.components.values()

            if component.panel_id == panel_id

        ]

    # =========================================================
    # GENERATE / RECONCILE COMPONENTS
    # =========================================================

    def generate_panel_components(
        self,
        panel_id: str,
        ct_count: int,
        relay_count: int,
        aux_count: int
    ):

        ct_count = max(
            0,
            int(ct_count or 0)
        )

        relay_count = max(
            0,
            int(relay_count or 0)
        )

        aux_count = max(
            0,
            int(aux_count or 0)
        )

        existing = (
            self.get_panel_components(
                panel_id
            )
        )

        # =====================================================
        # RECONCILE EACH COMPONENT TYPE
        # =====================================================

        self._reconcile_component_type(
            panel_id,
            "CT",
            "CT",
            ct_count,
            existing
        )

        self._reconcile_component_type(
            panel_id,
            "NUMERICAL_RELAY",
            "REL",
            relay_count,
            existing
        )

        self._reconcile_component_type(
            panel_id,
            "AUXILIARY_RELAY",
            "AUX",
            aux_count,
            existing
        )

        self.save_components()

    # =========================================================
    # RECONCILE COMPONENT TYPE
    # =========================================================

    def _reconcile_component_type(
        self,
        panel_id,
        component_type,
        prefix,
        required_count,
        existing
    ):

        components = [

            component

            for component in existing

            if component.component_type
            == component_type

        ]

        # -----------------------------------------------------
        # Create missing components
        # -----------------------------------------------------

        current_count = len(
            components
        )

        if current_count < required_count:

            for index in range(
                current_count + 1,
                required_count + 1
            ):

                name = (
                    f"{prefix}-{index:02d}"
                )

                self.create_component(
                    panel_id,
                    component_type,
                    name
                )

        # -----------------------------------------------------
        # Remove excess components
        #
        # Remove highest-numbered/generated components first.
        #
        # Existing configured components are therefore retained
        # as much as possible.
        # -----------------------------------------------------

        elif current_count > required_count:

            excess = (
                current_count
                - required_count
            )

            # Sort by component name
            # descending so REL-05 is removed
            # before REL-01.
            components_sorted = sorted(

                components,

                key=lambda component:
                    self._component_number(
                        component.name
                    ),

                reverse=True
            )

            for component in (
                components_sorted[:excess]
            ):

                self.components.pop(
                    component.component_id,
                    None
                )

    # =========================================================
    # COMPONENT NUMBER
    # =========================================================

    @staticmethod
    def _component_number(
        name
    ):

        try:

            return int(
                str(name)
                .split("-")[-1]
            )

        except (
            ValueError,
            IndexError
        ):

            return 0

    # =========================================================
    # UPDATE COMPONENT CONFIGURATION
    # =========================================================

    def update_component_configuration(
        self,
        component_id,
        configuration
    ):

        component = self.components.get(
            component_id
        )

        if component is None:

            raise ValueError(
                "Component does not exist."
            )

        configuration = (
            configuration or {}
        )

        # -----------------------------------------------------
        # Common fields
        # -----------------------------------------------------

        component.manufacturer = (
            configuration.get(
                "manufacturer",
                component.manufacturer
            )
        )

        component.model = (
            configuration.get(
                "model",
                component.model
            )
        )

        component.serial_number = (
            configuration.get(
                "serial_number",
                component.serial_number
            )
        )

        component.description = (
            configuration.get(
                "description",
                component.description
            )
        )

        # -----------------------------------------------------
        # CT
        # -----------------------------------------------------

        component.ct_ratio = (
            configuration.get(
                "ct_ratio",
                component.ct_ratio
            )
        )

        component.ct_class = (
            configuration.get(
                "ct_class",
                component.ct_class
            )
        )

        component.burden = (
            configuration.get(
                "burden",
                component.burden
            )
        )

        component.core = (
            configuration.get(
                "core",
                component.core
            )
        )

        # -----------------------------------------------------
        # Numerical relay
        # -----------------------------------------------------

        component.vt_ratio = (
            configuration.get(
                "vt_ratio",
                component.vt_ratio
            )
        )

        component.firmware = (
            configuration.get(
                "firmware",
                component.firmware
            )
        )

        # -----------------------------------------------------
        # Auxiliary relay
        # -----------------------------------------------------

        component.coil_voltage = (
            configuration.get(
                "coil_voltage",
                component.coil_voltage
            )
        )

        component.contact_configuration = (
            configuration.get(
                "contact_configuration",
                component.contact_configuration
            )
        )

        # -----------------------------------------------------
        # Protection functions
        #
        # IMPORTANT:
        # Do not overwrite these unless explicitly provided.
        # -----------------------------------------------------

        if (
            "protection_functions"
            in configuration
        ):

            component.protection_functions = (
                configuration[
                    "protection_functions"
                ]
            )

        self.save_components()

    # =========================================================
    # UPDATE PROTECTION FUNCTIONS
    # =========================================================

    def update_protection_functions(
        self,
        component_id,
        protection_functions
    ):

        component = self.components.get(
            component_id
        )

        if component is None:

            raise ValueError(
                "Component does not exist."
            )

        component.protection_functions = (
            protection_functions or []
        )

        self.save_components()

    # =========================================================
    # SAVE
    # =========================================================

    def save_components(self):

        data = []

        for component in (
            self.components.values()
        ):

            data.append({

                # -------------------------------------------------
                # Basic
                # -------------------------------------------------

                "component_id":
                    component.component_id,

                "panel_id":
                    component.panel_id,

                "component_type":
                    component.component_type,

                "name":
                    component.name,

                "manufacturer":
                    component.manufacturer,

                "model":
                    component.model,

                "serial_number":
                    component.serial_number,

                "description":
                    component.description,

                # -------------------------------------------------
                # CT
                # -------------------------------------------------

                "ct_ratio":
                    component.ct_ratio,

                "ct_class":
                    component.ct_class,

                "burden":
                    component.burden,

                "core":
                    component.core,

                # -------------------------------------------------
                # Numerical relay
                # -------------------------------------------------

                "vt_ratio":
                    component.vt_ratio,

                "firmware":
                    component.firmware,

                # -------------------------------------------------
                # Auxiliary relay
                # -------------------------------------------------

                "coil_voltage":
                    component.coil_voltage,

                "contact_configuration":
                    component.contact_configuration,

                # -------------------------------------------------
                # Protection functions
                # -------------------------------------------------

                "protection_functions":
                    component.protection_functions
            })

        self.components_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.components_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    # =========================================================
    # LOAD
    # =========================================================

    def load_components(self):

        self.components.clear()

        if not self.components_file.exists():
            return

        try:

            with open(
                self.components_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            if not isinstance(
                data,
                list
            ):

                raise ValueError(
                    "components.json must contain a list."
                )

            for item in data:

                component = TestComponent(

                    component_id=
                        item["component_id"],

                    panel_id=
                        item["panel_id"],

                    component_type=
                        item["component_type"],

                    name=
                        item["name"],

                    manufacturer=
                        item.get(
                            "manufacturer",
                            ""
                        ),

                    model=
                        item.get(
                            "model",
                            ""
                        ),

                    serial_number=
                        item.get(
                            "serial_number",
                            ""
                        ),

                    description=
                        item.get(
                            "description",
                            ""
                        ),

                    ct_ratio=
                        item.get(
                            "ct_ratio",
                            ""
                        ),

                    ct_class=
                        item.get(
                            "ct_class",
                            ""
                        ),

                    burden=
                        item.get(
                            "burden",
                            ""
                        ),

                    core=
                        item.get(
                            "core",
                            ""
                        ),

                    vt_ratio=
                        item.get(
                            "vt_ratio",
                            ""
                        ),

                    firmware=
                        item.get(
                            "firmware",
                            ""
                        ),

                    coil_voltage=
                        item.get(
                            "coil_voltage",
                            ""
                        ),

                    contact_configuration=
                        item.get(
                            "contact_configuration",
                            ""
                        ),

                    protection_functions=
                        item.get(
                            "protection_functions",
                            []
                        )
                )

                self.components[
                    component.component_id
                ] = component

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError
        ) as error:

            raise ValueError(
                "components.json is corrupted or invalid."
            ) from error
# =========================================================
# GET COMPONENTS FOR LINKED PANEL
# =========================================================

    def get_components_for_linked_panel(
        self,
        panel_id,
        linked_panel_id
    ):

        # -----------------------------------------------------
        # First look for components belonging to the local
        # panel.
        # -----------------------------------------------------

        local_components = (
            self.get_panel_components(
                panel_id
            )
        )

        if local_components:

            return local_components

        # -----------------------------------------------------
        # Then look for components belonging to the original
        # linked panel.
        # -----------------------------------------------------

        return (
            self.get_panel_components(
                linked_panel_id
            )
        )