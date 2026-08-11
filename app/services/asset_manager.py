from pathlib import Path
import json
from uuid import uuid4

from app.models.asset_node import AssetNode
from app.services.asset_library_manager import (
    AssetLibraryManager,
    DuplicateAssetError
)


class AssetManager:

    def __init__(
        self,
        project_folder: Path
    ):

        self.project_folder = project_folder

        self.assets_file = (
            project_folder / "assets.json"
        )

        # -------------------------------------------------
        # GLOBAL ASSET LIBRARY
        # -------------------------------------------------

        self.asset_library = (
            AssetLibraryManager()
        )

        self.nodes = {}

        self.load_assets()

    # =========================================================
    # ID
    # =========================================================

    def _generate_id(self):

        return (
            f"AST-{uuid4().hex[:8].upper()}"
        )

    # =========================================================
    # CREATE NODE
    # =========================================================

    def create_node(
        self,
        name: str,
        node_type: str,
        parent_id: str | None = None,
        asset_tag: str | None = None,
        serial_number: str | None = None,
        manufacturer: str | None = None,
        model: str | None = None
    ):

        name = str(
            name
        ).strip()

        node_type = str(
            node_type
        ).strip().upper()

        if not name:

            raise ValueError(
                "Name cannot be empty."
            )

        if not node_type:

            raise ValueError(
                "Node type cannot be empty."
            )

        # -------------------------------------------------
        # VALIDATE PARENT
        # -------------------------------------------------

        if parent_id is not None:

            if parent_id not in self.nodes:

                raise ValueError(
                    "Parent asset does not exist."
                )

        # -------------------------------------------------
        # PROJECT-LOCAL DUPLICATE
        # -------------------------------------------------

        for node in self.nodes.values():

            if (
                node.parent_id == parent_id
                and
                node.name.lower()
                == name.lower()
                and
                node.node_type.upper()
                == node_type
            ):

                raise ValueError(
                    f"{node_type.replace('_', ' ').title()} "
                    f"'{name}' already exists "
                    f"in this project."
                )

        # -------------------------------------------------
        # GLOBAL ASSET
        #
        # Only physical equipment types should be entered
        # into the global library.
        #
        # For now PANEL is the first one.
        # -------------------------------------------------

        asset_id = None

        if node_type == "PANEL":

            if not asset_tag:

                raise ValueError(
                    "Asset tag is required for a panel."
                )

            asset = (
                self.asset_library.create_asset(
                    asset_type="PANEL",
                    asset_tag=asset_tag,
                    name=name,
                    serial_number=serial_number,
                    manufacturer=manufacturer,
                    model=model
                )
            )

            asset_id = asset[
                "asset_id"
            ]

        # -------------------------------------------------
        # CREATE PROJECT NODE
        # -------------------------------------------------

        node_id = self._generate_id()

        node = AssetNode(

            node_id=node_id,

            name=name,

            node_type=node_type,

            parent_id=parent_id,

            asset_id=asset_id
        )

        self.nodes[
            node_id
        ] = node

        # -------------------------------------------------
        # CREATE PROJECT FOLDER
        # -------------------------------------------------

        self._create_folder(
            node
        )

        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        self.save_assets()

        return node
    def link_asset(
        self,
        asset_id,
        parent_id=None,
        name=None
    ):

        # -------------------------------------------------
        # GET GLOBAL ASSET
        # -------------------------------------------------

        asset = (
            self.asset_library.get_asset(
                asset_id
            )
        )

        if asset is None:

            raise ValueError(
                "Global asset does not exist."
            )

        # -------------------------------------------------
        # ONLY PANEL FOR NOW
        # -------------------------------------------------

        if (
            asset.get("asset_type", "")
            .upper()
            != "PANEL"
        ):

            raise ValueError(
                "Only panels can currently be linked."
            )

        # -------------------------------------------------
        # VALIDATE PARENT
        # -------------------------------------------------

        if parent_id is not None:

            if parent_id not in self.nodes:

                raise ValueError(
                    "Parent asset does not exist."
                )

        # -------------------------------------------------
        # DETERMINE DISPLAY NAME
        # -------------------------------------------------

        display_name = (
            str(
                name
                if name is not None
                else asset.get(
                    "name"
                )
                or asset.get(
                    "asset_tag"
                )
                or "Linked Panel"
            )
            .strip()
        )

        # -------------------------------------------------
        # PREVENT SAME ASSET FROM BEING LINKED TWICE
        # -------------------------------------------------

        for node in self.nodes.values():

            if (
                getattr(
                    node,
                    "asset_id",
                    None
                )
                == asset_id
            ):

                raise ValueError(
                    f"Asset "
                    f"'{asset.get('asset_tag', asset_id)}' "
                    f"already exists in this project."
                )

        # -------------------------------------------------
        # PREVENT SAME NODE
        # -------------------------------------------------

        for node in self.nodes.values():

            if (
                node.parent_id == parent_id
                and
                node.name.lower()
                == display_name.lower()
                and
                node.node_type.upper()
                == "PANEL"
            ):

                raise ValueError(
                    f"Panel '{display_name}' "
                    f"already exists in this project."
                )

        # -------------------------------------------------
        # CREATE PROJECT NODE
        # -------------------------------------------------

        node_id = self._generate_id()

        linked_node = AssetNode(

            node_id=node_id,

            name=display_name,

            node_type="PANEL",

            parent_id=parent_id,

            asset_id=asset_id,

            # Keep this temporarily so existing link UI
            # continues to understand that this is linked.
            linked_asset_id=asset_id,

            equipment_name=asset.get(
                "equipment_name",
                ""
            ),

            equipment_type=asset.get(
                "equipment_type",
                ""
            ),

            ct_count=asset.get(
                "ct_count",
                0
            ),

            relay_count=asset.get(
                "relay_count",
                0
            ),

            aux_count=asset.get(
                "aux_count",
                0
            )
        )

        self.nodes[
            node_id
        ] = linked_node

        self._create_folder(
            linked_node
        )

        self.save_assets()

        return linked_node
    # =========================================================
    # CREATE FOLDER
    # =========================================================

    def _create_folder(
        self,
        node
    ):

        hierarchy = []

        current = node

        while current is not None:

            hierarchy.insert(
                0,
                current.name
            )

            if current.parent_id is None:
                break

            current = self.nodes.get(
                current.parent_id
            )

        folder = self.project_folder

        for part in hierarchy:

            folder = folder / part

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

    # =========================================================
    # GET CHILDREN
    # =========================================================

    def get_children(
        self,
        parent_id=None
    ):

        return [
            node
            for node in self.nodes.values()
            if node.parent_id == parent_id
        ]

    # =========================================================
    # GET NODE
    # =========================================================

    def get_node(
        self,
        node_id
    ):

        return self.nodes.get(
            node_id
        )

    # =========================================================
    # FIND NODE BY NAME
    # =========================================================

    def find_node(
        self,
        name,
        node_type=None
    ):

        if name is None:
            return None

        name = str(name).strip().lower()

        if node_type is not None:

            node_type = (
                str(node_type)
                .strip()
                .upper()
            )

        for node in self.nodes.values():

            if node.name.strip().lower() != name:
                continue

            if (
                node_type is not None
                and node.node_type.upper()
                != node_type
            ):
                continue

            return node

        return None

    # =========================================================
    # UPDATE PANEL CONFIGURATION
    # =========================================================

    def update_panel_configuration(
        self,
        node_id,
        configuration
    ):

        node = self.nodes.get(
            node_id
        )

        if node is None:

            raise ValueError(
                "Panel does not exist."
            )

        if node.node_type.upper() != "PANEL":

            raise ValueError(
                "Selected asset is not a panel."
            )

        configuration = (
            configuration or {}
        )

        node.equipment_name = (
            configuration.get(
                "equipment_name",
                ""
            )
        )

        node.equipment_type = (
            configuration.get(
                "equipment_type",
                ""
            )
        )

        node.ct_count = int(
            configuration.get(
                "ct_count",
                0
            ) or 0
        )

        node.relay_count = int(
            configuration.get(
                "relay_count",
                0
            ) or 0
        )

        node.aux_count = int(
            configuration.get(
                "aux_count",
                0
            ) or 0
        )

        self.save_assets()

    # =========================================================
    # GET PANEL CONFIGURATION
    # =========================================================

    def get_panel_configuration(
        self,
        node_id
    ):

        node = self.nodes.get(
            node_id
        )

        if node is None:

            raise ValueError(
                "Panel does not exist."
            )

        if node.node_type.upper() != "PANEL":

            raise ValueError(
                "Selected asset is not a panel."
            )

        return {

            "panel_name":
                node.name,

            "equipment_name":
                getattr(
                    node,
                    "equipment_name",
                    ""
                ),

            "equipment_type":
                getattr(
                    node,
                    "equipment_type",
                    ""
                ),

            "ct_count":
                getattr(
                    node,
                    "ct_count",
                    0
                ),

            "relay_count":
                getattr(
                    node,
                    "relay_count",
                    0
                ),

            "aux_count":
                getattr(
                    node,
                    "aux_count",
                    0
                )
        }

    # =========================================================
    # SAVE ASSETS
    # =========================================================

    def save_assets(self):

        data = []

        for node in self.nodes.values():

            item = {

                "node_id":
                    node.node_id,

                "name":
                    node.name,

                "node_type":
                    node.node_type,

                "parent_id":
                    node.parent_id
            }

            # -------------------------------------------------
            # Panel configuration
            # -------------------------------------------------

            if node.node_type.upper() == "PANEL":

                item.update({

                    "equipment_name":
                        getattr(
                            node,
                            "equipment_name",
                            ""
                        ),

                    "equipment_type":
                        getattr(
                            node,
                            "equipment_type",
                            ""
                        ),

                    "ct_count":
                        getattr(
                            node,
                            "ct_count",
                            0
                        ),

                    "relay_count":
                        getattr(
                            node,
                            "relay_count",
                            0
                        ),

                    "aux_count":
                        getattr(
                            node,
                            "aux_count",
                            0
                        ),
                    "asset_id":
                        getattr(
                            node,
                            "asset_id",
                            None
                        ),

                    "linked_asset_id":
                        getattr(
                            node,
                            "linked_asset_id",
                            None
                        )
                })

            data.append(
                item
            )

        self.assets_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.assets_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    # =========================================================
    # LOAD ASSETS
    # =========================================================

    def load_assets(self):

        self.nodes.clear()

        if not self.assets_file.exists():
            return

        try:

            with open(
                self.assets_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            if not isinstance(data, list):

                raise ValueError(
                    "assets.json must contain a list."
                )

            for item in data:

                node = AssetNode(

                node_id=item["node_id"],

                name=item["name"],

                node_type=item["node_type"],

                parent_id=item["parent_id"],

                asset_id=item.get(
                    "asset_id"
                ),

                linked_asset_id=item.get(
                    "linked_asset_id"
                )
            )

                # -------------------------------------------------
                # Restore panel configuration
                # -------------------------------------------------

                if (
                    node.node_type.upper()
                    == "PANEL"
                ):

                    node.equipment_name = (
                        item.get(
                            "equipment_name",
                            ""
                        )
                    )

                    node.equipment_type = (
                        item.get(
                            "equipment_type",
                            ""
                        )
                    )

                    node.ct_count = int(
                        item.get(
                            "ct_count",
                            0
                        ) or 0
                    )

                    node.relay_count = int(
                        item.get(
                            "relay_count",
                            0
                        ) or 0
                    )

                    node.aux_count = int(
                        item.get(
                            "aux_count",
                            0
                        ) or 0
                    )

                self.nodes[
                    node.node_id
                ] = node

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError
        ) as error:

            raise ValueError(
                "assets.json is corrupted or invalid."
            ) from error

# =========================================================
# LINK EXISTING ASSET
# =========================================================

    def link_existing_asset(
        self,
        existing_asset,
        name=None,
        parent_id=None
    ):

        if existing_asset is None:

            raise ValueError(
                "Existing asset is invalid."
            )

        if existing_asset.node_type != "PANEL":

            raise ValueError(
                "Only panels can currently be linked."
            )

        # -----------------------------------------------------
        # Prevent linking the same asset to itself
        # -----------------------------------------------------

        if existing_asset.node_id in self.nodes:

            raise ValueError(
                "This asset already exists in the project."
            )

        # -----------------------------------------------------
        # Generate local node ID
        #
        # IMPORTANT:
        # linked_asset_id points to the original asset.
        # node_id belongs to this project.
        # -----------------------------------------------------

        node_id = self._generate_id()

        linked_node = AssetNode(

            node_id=node_id,

            name=(
                name.strip()
                if name
                else existing_asset.name
            ),

            node_type="PANEL",

            parent_id=parent_id,

            linked_asset_id=(
                existing_asset.node_id
            ),

            equipment_name=getattr(
                existing_asset,
                "equipment_name",
                ""
            ),

            equipment_type=getattr(
                existing_asset,
                "equipment_type",
                ""
            ),

            ct_count=getattr(
                existing_asset,
                "ct_count",
                0
            ),

            relay_count=getattr(
                existing_asset,
                "relay_count",
                0
            ),

            aux_count=getattr(
                existing_asset,
                "aux_count",
                0
            )
        )

        self.nodes[node_id] = linked_node

        self._create_folder(
            linked_node
        )

        self.save_assets()

        return linked_node


    # =========================================================
    # UNLINK ASSET
    # =========================================================

    def unlink_asset(
        self,
        node_id
    ):

        node = self.nodes.get(
            node_id
        )

        if node is None:

            raise ValueError(
                "Asset does not exist."
            )

        node.linked_asset_id = None

        self.save_assets()

        return node


    # =========================================================
    # CHECK LINK
    # =========================================================

    def is_asset_linked(
        self,
        node_id
    ):

        node = self.nodes.get(
            node_id
        )

        if node is None:
            return False

        return bool(
            getattr(
                node,
                "linked_asset_id",
                None
            )
        )


    # =========================================================
    # GET LINKED ASSET ID
    # =========================================================

    def get_linked_asset_id(
        self,
        node_id
    ):

        node = self.nodes.get(
            node_id
        )

        if node is None:
            return None

        return getattr(
            node,
            "linked_asset_id",
            None
        )
    def search_global_assets(
        self,
        search_text="",
        asset_type="PANEL"
    ):

        return (
            self.asset_library.search(
                search_text=search_text,
                asset_type=asset_type
            )
        )
    def get_global_asset(
        self,
        asset_id
    ):

        return (
            self.asset_library.get_asset(
                asset_id
            )
        )