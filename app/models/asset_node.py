class AssetNode:

    def __init__(
        self,
        node_id,
        name,
        node_type,
        parent_id=None,

        # -------------------------------------------------
        # Existing asset link
        # -------------------------------------------------

        linked_asset_id=None,

        # -------------------------------------------------
        # Panel configuration
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
        # LINK
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
    # LINK STATUS
    # =====================================================

    @property
    def is_linked(self):

        return bool(
            self.linked_asset_id
        )