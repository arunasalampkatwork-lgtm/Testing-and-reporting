from pathlib import Path

from app.config.settings import PROJECTS_DIR
from app.services.asset_manager import AssetManager
from app.services.component_manager import ComponentManager
from app.services.asset_library_manager import AssetLibraryManager


class GlobalAssetService:
    """
    Global view of assets across all projects.

    IMPORTANT CONCEPT
    -----------------
    A physical asset and a project node are NOT the same thing.

    Example:

        Project A
        └── REF-3 SS-1
                asset_id = ASSET-123

        Project B
        └── REF-3 SS-1
                asset_id = ASSET-123

    These are TWO project nodes but ONE physical asset.

    Therefore:

        get_all_nodes()
            -> returns project occurrences

        get_unique_assets()
            -> returns physical assets

        get_asset_counts()
            -> counts physical assets, NOT project occurrences

    This prevents linked substations, switchboards and panels from
    appearing as newly created assets in the Dashboard / Asset Manager.
    """

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(self, projects_dir=None):

        self.projects_dir = Path(
            projects_dir or PROJECTS_DIR
        )

        self.projects = []

        # -----------------------------------------------------
        # GLOBAL PHYSICAL ASSET LIBRARY
        # -----------------------------------------------------

        self.asset_library = AssetLibraryManager()

        self.refresh()

    # =========================================================
    # REFRESH
    # =========================================================

    def refresh(self):

        self.projects = []

        # Reload the global library first.
        #
        # This is important because another AssetManager instance
        # may have created or linked an asset since this service
        # was instantiated.
        try:
            self.asset_library.load()
        except Exception as error:
            print(
                "[GlobalAssetService] "
                f"Unable to reload global asset library: {error}"
            )

        if not self.projects_dir.exists():
            return

        for project_folder in sorted(
            self.projects_dir.iterdir(),
            key=lambda p: p.name.lower()
        ):

            if not project_folder.is_dir():
                continue

            try:

                asset_manager = AssetManager(
                    project_folder
                )

                component_manager = ComponentManager(
                    project_folder
                )

                self.projects.append(
                    {
                        "name":
                            project_folder.name,

                        "folder":
                            project_folder,

                        "asset_manager":
                            asset_manager,

                        "component_manager":
                            component_manager,
                    }
                )

            except Exception as error:

                print(
                    "[GlobalAssetService] "
                    f"Skipping {project_folder.name}: "
                    f"{error}"
                )

    # =========================================================
    # PROJECTS
    # =========================================================

    def get_projects(self):

        return list(
            self.projects
        )

    # =========================================================
    # GET PROJECT
    # =========================================================

    def get_project(
        self,
        project_name
    ):

        for project in self.projects:

            if (
                project["name"]
                == project_name
            ):

                return project

        return None

    # =========================================================
    # PROJECT HIERARCHY
    # =========================================================

    def get_project_hierarchy(self):

        result = []

        for project in self.projects:

            manager = project[
                "asset_manager"
            ]

            try:

                roots = manager.get_children(
                    None
                )

            except Exception:

                roots = []

            result.append(
                {
                    "project":
                        project["name"],

                    "folder":
                        project["folder"],

                    "asset_manager":
                        manager,

                    "component_manager":
                        project[
                            "component_manager"
                        ],

                    "roots":
                        roots,
                }
            )

        return result

    # =========================================================
    # ALL PROJECT NODES
    # =========================================================

    def get_all_nodes(self):

        """
        Return every occurrence of every node in every project.

        DO NOT use this method for physical asset counts.

        This intentionally includes linked assets because the Asset
        Explorer needs to know that an asset occurs in a particular
        project.
        """

        result = []

        for project in self.projects:

            manager = project[
                "asset_manager"
            ]

            try:

                nodes = manager.nodes.values()

            except Exception:

                nodes = []

            for node in nodes:

                result.append(
                    {
                        "project":
                            project["name"],

                        "folder":
                            project["folder"],

                        "node":
                            node,

                        "asset_manager":
                            manager,

                        "component_manager":
                            project[
                                "component_manager"
                            ],
                    }
                )

        return result

    # =========================================================
    # UNIQUE PHYSICAL ASSETS
    # =========================================================

    def get_unique_assets(
        self,
        asset_type=None
    ):

        """
        Return unique physical assets from the global asset library.

        This is the correct source for:

            - Dashboard inventory
            - Asset Manager inventory
            - Asset Register
            - Physical asset counts

        A linked project occurrence does NOT create another physical
        asset here because both occurrences share the same asset_id.
        """

        try:

            self.asset_library.load()

        except Exception as error:

            print(
                "[GlobalAssetService] "
                f"Unable to reload asset library: {error}"
            )

        return self.asset_library.get_all_assets(
            asset_type=asset_type
        )

    # =========================================================
    # UNIQUE PHYSICAL ASSET IDS
    # =========================================================

    def get_unique_asset_ids(
        self,
        asset_type=None
    ):

        assets = self.get_unique_assets(
            asset_type=asset_type
        )

        return {
            asset.get("asset_id")
            for asset in assets
            if asset.get("asset_id")
        }

    # =========================================================
    # FIND PHYSICAL ASSET
    # =========================================================

    def get_unique_asset(
        self,
        asset_id
    ):

        if not asset_id:
            return None

        try:
            self.asset_library.load()
        except Exception:
            pass

        return self.asset_library.get_asset(
            asset_id
        )

    # =========================================================
    # GET ALL COMPONENTS
    # =========================================================

    def get_all_components(self):

        """
        Return components associated with project panels.

        Components remain project/test records rather than global
        physical assets in the current architecture.

        Therefore this method intentionally walks project panels.
        """

        result = []

        for project in self.projects:

            asset_manager = project[
                "asset_manager"
            ]

            component_manager = project[
                "component_manager"
            ]

            try:

                nodes = asset_manager.nodes.values()

            except Exception:

                nodes = []

            for panel in nodes:

                if str(
                    getattr(
                        panel,
                        "node_type",
                        ""
                    )
                ).upper() != "PANEL":

                    continue

                try:

                    components = (
                        component_manager
                        .get_panel_components(
                            panel.node_id
                        )
                    )

                except Exception:

                    components = []

                for component in components:

                    result.append(
                        {
                            "project":
                                project["name"],

                            "folder":
                                project["folder"],

                            "panel":
                                panel,

                            "component":
                                component,

                            "asset_manager":
                                asset_manager,

                            "component_manager":
                                component_manager,
                        }
                    )

        return result

    # =========================================================
    # UNIQUE COMPONENTS BY PHYSICAL ID
    # =========================================================

    def get_unique_components(self):

        """
        Return unique components where a stable component/asset ID
        exists.

        If a component does not have a global physical ID, it is
        retained as a project-level component.

        This method is deliberately conservative so we do not
        accidentally merge two different CTs merely because their
        names happen to be identical.
        """

        all_components = (
            self.get_all_components()
        )

        result = []

        seen_ids = set()

        for entry in all_components:

            component = entry[
                "component"
            ]

            component_id = getattr(
                component,
                "asset_id",
                None
            )

            if not component_id:

                component_id = getattr(
                    component,
                    "component_id",
                    None
                )

            # -------------------------------------------------
            # If there is no usable ID, retain the component.
            # -------------------------------------------------

            if not component_id:

                result.append(
                    entry
                )

                continue

            # -------------------------------------------------
            # Prevent duplicate physical components.
            # -------------------------------------------------

            if component_id in seen_ids:

                continue

            seen_ids.add(
                component_id
            )

            result.append(
                entry
            )

        return result

    # =========================================================
    # ASSET COUNTS
    # =========================================================

    def get_asset_counts(self):

        """
        Return inventory counts of UNIQUE PHYSICAL ASSETS.

        IMPORTANT:

        Do NOT count project nodes here.

        A linked substation may occur in:

            Project A
            Project B
            Project C

        but if all three nodes contain:

            asset_id = ASSET-123

        the dashboard must show:

            SUBSTATIONS = 1

        rather than:

            SUBSTATIONS = 3
        """

        counts = {
            "projects":
                len(self.projects),

            "substations":
                0,

            "switchboards":
                0,

            "panels":
                0,

            "cts":
                0,

            "relays":
                0,

            "aux":
                0,

            "meters":
                0,
        }

        # =====================================================
        # PHYSICAL ASSETS
        # =====================================================

        unique_assets = (
            self.get_unique_assets()
        )

        for asset in unique_assets:

            asset_type = str(
                asset.get(
                    "asset_type",
                    ""
                )
            ).strip().upper()

            if asset_type == "SUBSTATION":

                counts[
                    "substations"
                ] += 1

            elif asset_type == "SWITCHBOARD":

                counts[
                    "switchboards"
                ] += 1

            elif asset_type == "PANEL":

                counts[
                    "panels"
                ] += 1

        # =====================================================
        # COMPONENT COUNTS
        # =====================================================
        #
        # Components are currently stored under projects rather
        # than in the global physical asset library.
        #
        # Use unique component IDs where available.
        #
        # =====================================================

        components = (
            self.get_unique_components()
        )

        for entry in components:

            component = entry[
                "component"
            ]

            component_type = str(
                getattr(
                    component,
                    "component_type",
                    ""
                )
            ).strip().upper()

            if component_type in (
                "CT",
                "CURRENT TRANSFORMER",
            ):

                counts[
                    "cts"
                ] += 1

            elif component_type in (
                "NUMERICAL_RELAY",
                "NUMERICAL RELAY",
            ):

                counts[
                    "relays"
                ] += 1

            elif component_type in (
                "AUXILIARY_RELAY",
                "AUX RELAY",
                "AUXILIARY RELAY",
            ):

                counts[
                    "aux"
                ] += 1

            elif component_type in (
                "METER",
                "AMMETER",
                "VOLTMETER",
                "MULTIFUNCTION_METER",
                "MULTIFUNCTION METER",
            ):

                counts[
                    "meters"
                ] += 1

        return counts

    # =========================================================
    # ASSET OCCURRENCES
    # =========================================================

    def get_asset_occurrences(
        self,
        asset_id
    ):

        """
        Return every project occurrence of a physical asset.

        Useful for Asset Explorer.

        Example:

            ASSET-123

            Project A -> REF-3 SS-1
            Project B -> REF-3 SS-1
        """

        if not asset_id:

            return []

        result = []

        for entry in self.get_all_nodes():

            node = entry[
                "node"
            ]

            node_asset_id = getattr(
                node,
                "asset_id",
                None
            )

            if node_asset_id == asset_id:

                result.append(
                    entry
                )

        return result

    # =========================================================
    # GET OCCURRENCE COUNT
    # =========================================================

    def get_asset_occurrence_count(
        self,
        asset_id
    ):

        return len(
            self.get_asset_occurrences(
                asset_id
            )
        )

    # =========================================================
    # CHECK WHETHER ASSET IS LINKED
    # =========================================================

    def is_asset_linked(
        self,
        asset_id
    ):

        occurrences = (
            self.get_asset_occurrences(
                asset_id
            )
        )

        return len(
            occurrences
        ) > 1

    # =========================================================
    # GET PROJECTS CONTAINING ASSET
    # =========================================================

    def get_projects_for_asset(
        self,
        asset_id
    ):

        occurrences = (
            self.get_asset_occurrences(
                asset_id
            )
        )

        projects = []

        seen = set()

        for occurrence in occurrences:

            project_name = occurrence[
                "project"
            ]

            if project_name in seen:
                continue

            seen.add(
                project_name
            )

            projects.append(
                project_name
            )

        return projects