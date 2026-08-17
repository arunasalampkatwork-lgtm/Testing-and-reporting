from pathlib import Path

from app.config.settings import PROJECTS_DIR
from app.services.asset_manager import AssetManager
from app.services.component_manager import ComponentManager


class GlobalAssetService:
    """
    Read-only aggregation of asset configuration across every project.

    Project-specific AssetManager / ComponentManager instances remain the
    source of truth. This service simply loads them all for universal
    browsing and inventory views.
    """

    def __init__(self, projects_dir=None):
        self.projects_dir = Path(
            projects_dir or PROJECTS_DIR
        )
        self.projects = []
        self.refresh()

    def refresh(self):
        self.projects = []

        if not self.projects_dir.exists():
            return

        for project_folder in sorted(
            self.projects_dir.iterdir(),
            key=lambda p: p.name.lower(),
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
                        "name": project_folder.name,
                        "folder": project_folder,
                        "asset_manager": asset_manager,
                        "component_manager": component_manager,
                    }
                )

            except Exception as error:
                print(
                    f"[GlobalAssetService] "
                    f"Skipping {project_folder.name}: {error}"
                )

    def get_projects(self):
        return list(self.projects)

    def get_project(self, project_name):
        for project in self.projects:
            if project["name"] == project_name:
                return project
        return None

    def get_project_hierarchy(self):
        result = []

        for project in self.projects:
            manager = project["asset_manager"]

            try:
                roots = manager.get_children(None)
            except Exception:
                roots = []

            result.append(
                {
                    "project": project["name"],
                    "folder": project["folder"],
                    "asset_manager": manager,
                    "component_manager": project[
                        "component_manager"
                    ],
                    "roots": roots,
                }
            )

        return result

    def get_all_nodes(self):
        result = []

        for project in self.projects:
            manager = project["asset_manager"]

            try:
                nodes = manager.nodes.values()
            except Exception:
                nodes = []

            for node in nodes:
                result.append(
                    {
                        "project": project["name"],
                        "folder": project["folder"],
                        "node": node,
                        "asset_manager": manager,
                        "component_manager": project[
                            "component_manager"
                        ],
                    }
                )

        return result

    def get_all_components(self):
        result = []

        for project in self.projects:
            asset_manager = project["asset_manager"]
            component_manager = project["component_manager"]

            try:
                nodes = asset_manager.nodes.values()
            except Exception:
                nodes = []

            for panel in nodes:
                if str(
                    getattr(panel, "node_type", "")
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
                            "project": project["name"],
                            "folder": project["folder"],
                            "panel": panel,
                            "component": component,
                            "asset_manager": asset_manager,
                            "component_manager": component_manager,
                        }
                    )

        return result

    def get_asset_counts(self):
        counts = {
            "projects": len(self.projects),
            "substations": 0,
            "switchboards": 0,
            "panels": 0,
            "cts": 0,
            "relays": 0,
            "aux": 0,
            "meters": 0,
        }

        for entry in self.get_all_nodes():
            node_type = str(
                getattr(
                    entry["node"],
                    "node_type",
                    "",
                )
            ).upper()

            if node_type == "SUBSTATION":
                counts["substations"] += 1

            elif node_type == "SWITCHBOARD":
                counts["switchboards"] += 1

            elif node_type == "PANEL":
                counts["panels"] += 1

        for entry in self.get_all_components():
            component_type = str(
                getattr(
                    entry["component"],
                    "component_type",
                    "",
                )
            ).upper()

            if component_type in (
                "CT",
                "CURRENT TRANSFORMER",
            ):
                counts["cts"] += 1

            elif component_type == "NUMERICAL_RELAY":
                counts["relays"] += 1

            elif component_type in (
                "AUXILIARY_RELAY",
                "AUX RELAY",
            ):
                counts["aux"] += 1

            elif component_type in (
                "METER",
                "AMMETER",
                "VOLTMETER",
                "MULTIFUNCTION_METER",
            ):
                counts["meters"] += 1

        return counts
