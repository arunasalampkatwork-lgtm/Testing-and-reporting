class AssetNode:

    def __init__(
        self,
        node_id,
        name,
        node_type,
        parent_id=None,

        # -------------------------------------------------
        # GLOBAL PHYSICAL ASSET ID
        # -------------------------------------------------
        asset_id=None,

        # -------------------------------------------------
        # BACKWARD COMPATIBILITY
        # -------------------------------------------------
        linked_asset_id=None,

        # -------------------------------------------------
        # PANEL CONFIGURATION
        # -------------------------------------------------
        equipment_name="",
        equipment_type="",
        ct_count=0,
        relay_count=0,
        aux_count=0
    ):

        self.node_id = node_id
        self.name = name
        self.node_type = node_type
        self.parent_id = parent_id

        # -------------------------------------------------
        # GLOBAL PHYSICAL ASSET
        #
        # asset_id identifies the actual physical equipment.
        #
        # node_id identifies this occurrence of that asset
        # inside the current project.
        # -------------------------------------------------
        self.asset_id = asset_id

        # -------------------------------------------------
        # OLD LINK FIELD
        #
        # Kept temporarily so existing projects do not break.
        # New code should use asset_id.
        # -------------------------------------------------
        self.linked_asset_id = linked_asset_id

        # -------------------------------------------------
        # PANEL CONFIGURATION
        # -------------------------------------------------
        self.equipment_name = equipment_name
        self.equipment_type = equipment_type

        self.ct_count = ct_count
        self.relay_count = relay_count
        self.aux_count = aux_count

    # =====================================================
    # ASSET TYPE
    # =====================================================

    @property
    def is_panel(self):
        return self.node_type.upper() == "PANEL"

    # =====================================================
    # LINK STATUS
    # =====================================================

    @property
    def is_linked(self):

        return bool(
            self.asset_id
            and self.linked_asset_id
        )