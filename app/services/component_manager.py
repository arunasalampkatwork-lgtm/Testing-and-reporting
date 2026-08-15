from pathlib import Path
import json
from uuid import uuid4

from app.models.test_component import TestComponent

try:
    from app.services.asset_library_manager import (
        AssetLibraryManager
    )
except ImportError:
    AssetLibraryManager = None


class ComponentManager:

    def __init__(
        self,
        project_folder: Path
    ):

        self.project_folder = (
            project_folder
        )

        self.components_file = (
            project_folder
            /
            "components.json"
        )

        self.components = {}

        # -------------------------------------------------
        # GLOBAL ASSET LIBRARY
        # -------------------------------------------------

        self.asset_library = None

        if AssetLibraryManager is not None:

            try:

                self.asset_library = (
                    AssetLibraryManager()
                )

            except Exception:

                self.asset_library = None

        self.load_components()

    # =====================================================
    # ID
    # =====================================================

    def _generate_id(self):

        return (
            f"CMP-{uuid4().hex[:8].upper()}"
        )

    # =====================================================
    # GET COMPONENT
    # =====================================================

    def get_component(
        self,
        component_id
    ):

        return self.components.get(
            component_id
        )

    # =====================================================
    # CREATE COMPONENT
    # =====================================================

    def create_component(
        self,
        panel_id,
        component_type,
        name
    ):

        component = TestComponent(

            component_id=(
                self._generate_id()
            ),

            panel_id=panel_id,

            component_type=(
                component_type
            ),

            name=name
        )

        self.components[
            component.component_id
        ] = component

        self.save_components()

        return component

    # =====================================================
    # GET PANEL COMPONENTS
    # =====================================================

    def get_panel_components(
        self,
        panel_id
    ):

        return [

            component

            for component
            in self.components.values()

            if component.panel_id
            == panel_id

        ]

    # =====================================================
    # GET PANEL CTS
    # =====================================================

    def get_panel_cts(
        self,
        panel_id
    ):

        components = (
            self.get_panel_components(
                panel_id
            )
        )

        return [

            component

            for component
            in components

            if str(
                getattr(
                    component,
                    "component_type",
                    ""
                )
            ).strip().upper()
            in (
                "CT",
                "CURRENT TRANSFORMER",
            )

        ]

    # =====================================================
    # GENERATE PANEL COMPONENTS
    # =====================================================

    def generate_panel_components(
        self,
        panel_id,
        ct_count,
        relay_count,
        aux_count
    ):

        ct_count = int(
            ct_count or 0
        )

        relay_count = int(
            relay_count or 0
        )

        aux_count = int(
            aux_count or 0
        )

        # -------------------------------------------------
        # Existing components
        # -------------------------------------------------

        existing = (
            self.get_panel_components(
                panel_id
            )
        )

        # -------------------------------------------------
        # Maintain existing configured components
        # wherever possible.
        # -------------------------------------------------

        self._reconcile_component_type(
            panel_id,
            "CT",
            ct_count,
            "CT"
        )

        self._reconcile_component_type(
            panel_id,
            "NUMERICAL_RELAY",
            relay_count,
            "REL"
        )

        self._reconcile_component_type(
            panel_id,
            "AUXILIARY_RELAY",
            aux_count,
            "AUX"
        )

        self.save_components()

    # =====================================================
    # RECONCILE COMPONENT TYPE
    # =====================================================

    def _reconcile_component_type(
        self,
        panel_id,
        component_type,
        required_count,
        prefix
    ):

        components = [

            component

            for component
            in self.get_panel_components(
                panel_id
            )

            if str(
                component.component_type
            ).upper()
            == str(
                component_type
            ).upper()

        ]

        current_count = len(
            components
        )

        # -------------------------------------------------
        # CREATE MISSING
        # -------------------------------------------------

        if current_count < required_count:

            for index in range(
                current_count + 1,
                required_count + 1
            ):

                self.create_component(

                    panel_id,

                    component_type,

                    f"{prefix}-{index:02d}"
                )

        # -------------------------------------------------
        # REMOVE EXCESS
        # -------------------------------------------------

        elif current_count > required_count:

            excess = (
                current_count
                -
                required_count
            )

            components_sorted = sorted(

                components,

                key=lambda component:
                    self._component_number(
                        component.name
                    ),

                reverse=True
            )

            for component in (
                components_sorted[
                    :excess
                ]
            ):

                self.components.pop(
                    component.component_id,
                    None
                )

    # =====================================================
    # COMPONENT NUMBER
    # =====================================================

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

    # =====================================================
    # UPDATE COMPONENT CONFIGURATION
    # =====================================================

    def update_component_configuration(
        self,
        component_id,
        configuration
    ):

        component = (
            self.components.get(
                component_id
            )
        )

        if component is None:

            raise ValueError(
                "Component does not exist."
            )

        configuration = (
            configuration
            or {}
        )

        # =================================================
        # COMMON
        # =================================================

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

        # =================================================
        # CT PRIMARY
        # =================================================

        if (
            "ct_primary"
            in configuration
        ):

            component.ct_primary = (
                self._safe_float(
                    configuration[
                        "ct_primary"
                    ]
                )
            )

        # =================================================
        # CT SECONDARY
        # =================================================

        if (
            "ct_secondary"
            in configuration
        ):

            component.ct_secondary = (
                self._safe_float(
                    configuration[
                        "ct_secondary"
                    ]
                )
            )

        # =================================================
        # CT RATIO
        # =================================================

        if (
            "ct_ratio"
            in configuration
        ):

            component.ct_ratio = (
                str(
                    configuration[
                        "ct_ratio"
                    ]
                    or ""
                ).strip()
            )

        # Automatically regenerate ratio when both
        # numerical values are available.

        if (
            component.ct_primary > 0
            and component.ct_secondary > 0
        ):

            component.ct_ratio = (
                f"{component.ct_primary:g}/"
                f"{component.ct_secondary:g}"
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

        # =================================================
        # NUMERICAL RELAY
        # =================================================

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

        # =================================================
        # AUXILIARY RELAY
        # =================================================

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

        # =================================================
        # PROTECTION FUNCTIONS
        # =================================================

        if (
            "protection_functions"
            in configuration
        ):

            component.protection_functions = (
                list(
                    configuration[
                        "protection_functions"
                    ]
                    or []
                )
            )

        self.save_components()

        self._sync_panel_components_to_global(
            component.panel_id
        )

    # =====================================================
    # UPDATE PROTECTION FUNCTIONS
    # =====================================================

    def update_protection_functions(
        self,
        component_id,
        protection_functions
    ):

        component = (
            self.components.get(
                component_id
            )
        )

        if component is None:

            raise ValueError(
                "Component does not exist."
            )

        component.protection_functions = (
            list(
                protection_functions
                or []
            )
        )

        self.save_components()

        self._sync_panel_components_to_global(
            component.panel_id
        )

    # =====================================================
    # SAFE FLOAT
    # =====================================================

    @staticmethod
    def _safe_float(
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
    # SERIALIZE PANEL COMPONENTS
    # =====================================================

    def serialize_panel_components(
        self,
        panel_id
    ):

        result = []

        for component in (
            self.get_panel_components(
                panel_id
            )
        ):

            result.append({

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

                # -----------------------------------------
                # CT
                # -----------------------------------------

                "ct_primary":
                    getattr(
                        component,
                        "ct_primary",
                        0
                    ),

                "ct_secondary":
                    getattr(
                        component,
                        "ct_secondary",
                        0
                    ),

                "ct_ratio":
                    component.ct_ratio,

                "ct_class":
                    component.ct_class,

                "burden":
                    component.burden,

                "core":
                    component.core,

                # -----------------------------------------
                # RELAY
                # -----------------------------------------

                "vt_ratio":
                    component.vt_ratio,

                "firmware":
                    component.firmware,

                # -----------------------------------------
                # AUX RELAY
                # -----------------------------------------

                "coil_voltage":
                    component.coil_voltage,

                "contact_configuration":
                    component.contact_configuration,

                # -----------------------------------------
                # PROTECTION
                # -----------------------------------------

                "protection_functions":
                    list(
                        component.protection_functions
                        or []
                    ),
            })

        return result

    # =====================================================
    # CLONE PANEL COMPONENTS
    # =====================================================

    def clone_panel_components(
        self,
        panel_id,
        component_data
    ):

        existing_ids = [

            component_id

            for component_id,
            component
            in self.components.items()

            if component.panel_id
            == panel_id

        ]

        for component_id in existing_ids:

            del self.components[
                component_id
            ]

        for data in (
            component_data
            or []
        ):

            component = TestComponent(

                component_id=(
                    self._generate_id()
                ),

                panel_id=panel_id,

                component_type=(
                    data.get(
                        "component_type",
                        ""
                    )
                ),

                name=(
                    data.get(
                        "name",
                        ""
                    )
                ),

                manufacturer=(
                    data.get(
                        "manufacturer",
                        ""
                    )
                ),

                model=(
                    data.get(
                        "model",
                        ""
                    )
                ),

                serial_number=(
                    data.get(
                        "serial_number",
                        ""
                    )
                ),

                description=(
                    data.get(
                        "description",
                        ""
                    )
                ),

                ct_primary=(
                    data.get(
                        "ct_primary",
                        0
                    )
                ),

                ct_secondary=(
                    data.get(
                        "ct_secondary",
                        0
                    )
                ),

                ct_ratio=(
                    data.get(
                        "ct_ratio",
                        ""
                    )
                ),

                ct_class=(
                    data.get(
                        "ct_class",
                        ""
                    )
                ),

                burden=(
                    data.get(
                        "burden",
                        ""
                    )
                ),

                core=(
                    data.get(
                        "core",
                        ""
                    )
                ),

                vt_ratio=(
                    data.get(
                        "vt_ratio",
                        ""
                    )
                ),

                firmware=(
                    data.get(
                        "firmware",
                        ""
                    )
                ),

                coil_voltage=(
                    data.get(
                        "coil_voltage",
                        ""
                    )
                ),

                contact_configuration=(
                    data.get(
                        "contact_configuration",
                        ""
                    )
                ),

                protection_functions=(
                    data.get(
                        "protection_functions",
                        []
                    )
                )
            )

            self.components[
                component.component_id
            ] = component

        self.save_components()

        return (
            self.get_panel_components(
                panel_id
            )
        )

    # =====================================================
    # GLOBAL SYNC
    # =====================================================

    def _get_global_panel_id(
        self,
        panel_id
    ):

        assets_file = (
            self.project_folder
            /
            "assets.json"
        )

        if not assets_file.exists():

            return None

        try:

            with open(
                assets_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            for item in data:

                if (
                    item.get("node_id")
                    == panel_id
                    and str(
                        item.get(
                            "node_type",
                            ""
                        )
                    ).upper()
                    == "PANEL"
                ):

                    return item.get(
                        "asset_id"
                    )

        except (
            json.JSONDecodeError,
            TypeError,
            OSError
        ):

            return None

        return None

    def _sync_panel_components_to_global(
        self,
        panel_id
    ):

        if self.asset_library is None:

            return

        global_asset_id = (
            self._get_global_panel_id(
                panel_id
            )
        )

        if not global_asset_id:

            return

        try:

            self.asset_library.load()

            asset = (
                self.asset_library.get_asset(
                    global_asset_id
                )
            )

            if asset is None:

                return

            metadata = dict(
                asset.get(
                    "metadata"
                )
                or {}
            )

            metadata[
                "components"
            ] = (
                self.serialize_panel_components(
                    panel_id
                )
            )

            self.asset_library.update_asset(
                global_asset_id,
                {
                    "metadata": metadata
                }
            )

        except Exception:

            # Global synchronization should never prevent
            # local project operation.
            pass

    # =====================================================
    # SAVE
    # =====================================================

    def save_components(self):

        data = []

        for component in (
            self.components.values()
        ):

            data.append({

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

                # -----------------------------------------
                # CT
                # -----------------------------------------

                "ct_primary":
                    getattr(
                        component,
                        "ct_primary",
                        0
                    ),

                "ct_secondary":
                    getattr(
                        component,
                        "ct_secondary",
                        0
                    ),

                "ct_ratio":
                    component.ct_ratio,

                "ct_class":
                    component.ct_class,

                "burden":
                    component.burden,

                "core":
                    component.core,

                # -----------------------------------------
                # RELAY
                # -----------------------------------------

                "vt_ratio":
                    component.vt_ratio,

                "firmware":
                    component.firmware,

                # -----------------------------------------
                # AUX RELAY
                # -----------------------------------------

                "coil_voltage":
                    component.coil_voltage,

                "contact_configuration":
                    component.contact_configuration,

                # -----------------------------------------
                # PROTECTION
                # -----------------------------------------

                "protection_functions":
                    list(
                        component.protection_functions
                        or []
                    ),
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

    # =====================================================
    # LOAD
    # =====================================================

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

                    component_id=(
                        item[
                            "component_id"
                        ]
                    ),

                    panel_id=(
                        item[
                            "panel_id"
                        ]
                    ),

                    component_type=(
                        item[
                            "component_type"
                        ]
                    ),

                    name=(
                        item[
                            "name"
                        ]
                    ),

                    manufacturer=(
                        item.get(
                            "manufacturer",
                            ""
                        )
                    ),

                    model=(
                        item.get(
                            "model",
                            ""
                        )
                    ),

                    serial_number=(
                        item.get(
                            "serial_number",
                            ""
                        )
                    ),

                    description=(
                        item.get(
                            "description",
                            ""
                        )
                    ),

                    ct_primary=(
                        item.get(
                            "ct_primary",
                            0
                        )
                    ),

                    ct_secondary=(
                        item.get(
                            "ct_secondary",
                            0
                        )
                    ),

                    ct_ratio=(
                        item.get(
                            "ct_ratio",
                            ""
                        )
                    ),

                    ct_class=(
                        item.get(
                            "ct_class",
                            ""
                        )
                    ),

                    burden=(
                        item.get(
                            "burden",
                            ""
                        )
                    ),

                    core=(
                        item.get(
                            "core",
                            ""
                        )
                    ),

                    vt_ratio=(
                        item.get(
                            "vt_ratio",
                            ""
                        )
                    ),

                    firmware=(
                        item.get(
                            "firmware",
                            ""
                        )
                    ),

                    coil_voltage=(
                        item.get(
                            "coil_voltage",
                            ""
                        )
                    ),

                    contact_configuration=(
                        item.get(
                            "contact_configuration",
                            ""
                        )
                    ),

                    protection_functions=(
                        item.get(
                            "protection_functions",
                            []
                        )
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
    # GET CTS FOR PANEL
    # =========================================================

    def get_panel_cts(
        self,
        panel_id
    ):

        components = (
            self.get_panel_components(
                panel_id
            )
        )

        return [

            component

            for component in components

            if str(
                getattr(
                    component,
                    "component_type",
                    ""
                )
            ).strip().upper()
            in (
                "CT",
                "CURRENT TRANSFORMER",
            )

        ]