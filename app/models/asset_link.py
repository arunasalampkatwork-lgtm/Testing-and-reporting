from dataclasses import dataclass


@dataclass
class AssetLink:

    link_id: str

    source_project_id: str

    source_panel_id: str

    target_project_id: str

    target_panel_id: str

    source_panel_name: str = ""

    linked_at: str = ""