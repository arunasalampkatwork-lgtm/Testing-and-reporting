from pathlib import Path
import json
from uuid import uuid4


class DuplicateAssetError(ValueError):
    """
    Raised when an attempt is made to create an asset
    that already exists in the global asset library.
    """
    pass


class AssetLibraryManager:

    def __init__(self, library_file=None):

        # -------------------------------------------------
        # DEFAULT GLOBAL ASSET LIBRARY
        # -------------------------------------------------

        if library_file is None:

            project_root = Path(__file__).resolve().parents[2]

            library_file = (
                project_root
                / "resources"
                / "asset_library.json"
            )

        self.library_file = Path(library_file)

        self.assets = {}

        self.load()

    # =====================================================
    # ID GENERATION
    # =====================================================

    def _generate_asset_id(self):

        return (
            f"ASSET-{uuid4().hex[:10].upper()}"
        )

    # =====================================================
    # NORMALIZATION
    # =====================================================

    @staticmethod
    def _normalize(value):

        if value is None:
            return ""

        return str(value).strip().lower()

    # =====================================================
    # LOAD
    # =====================================================

    def load(self):

        self.assets.clear()

        if not self.library_file.exists():

            self.library_file.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            self.save()

            return

        try:

            with open(
                self.library_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            if not isinstance(data, list):

                raise ValueError(
                    "asset_library.json must contain a list."
                )

            for item in data:

                asset_id = item.get(
                    "asset_id"
                )

                if not asset_id:
                    continue

                self.assets[asset_id] = item

        except (
            json.JSONDecodeError,
            TypeError,
            ValueError
        ) as error:

            raise ValueError(
                "asset_library.json is corrupted or invalid."
            ) from error

    # =====================================================
    # SAVE
    # =====================================================

    def save(self):

        self.library_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = list(
            self.assets.values()
        )

        with open(
            self.library_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    # =====================================================
    # FIND BY ASSET ID
    # =====================================================

    def get_asset(
        self,
        asset_id
    ):

        if not asset_id:
            return None

        return self.assets.get(
            asset_id
        )

    # =====================================================
    # FIND DUPLICATE
    # =====================================================

    def find_duplicate(
        self,
        asset_type,
        asset_tag=None,
        serial_number=None
    ):

        asset_type = (
            str(asset_type)
            .strip()
            .upper()
        )

        normalized_tag = (
            self._normalize(asset_tag)
        )

        normalized_serial = (
            self._normalize(serial_number)
        )

        # -------------------------------------------------
        # SERIAL NUMBER HAS PRIORITY
        #
        # Particularly useful for relays and test equipment.
        # -------------------------------------------------

        if normalized_serial:

            for asset in self.assets.values():

                if (
                    str(
                        asset.get(
                            "asset_type",
                            ""
                        )
                    ).upper()
                    != asset_type
                ):
                    continue

                existing_serial = self._normalize(
                    asset.get(
                        "serial_number"
                    )
                )

                if (
                    existing_serial
                    and existing_serial
                    == normalized_serial
                ):

                    return asset

        # -------------------------------------------------
        # ASSET TAG
        # -------------------------------------------------

        if normalized_tag:

            for asset in self.assets.values():

                if (
                    str(
                        asset.get(
                            "asset_type",
                            ""
                        )
                    ).upper()
                    != asset_type
                ):
                    continue

                existing_tag = self._normalize(
                    asset.get(
                        "asset_tag"
                    )
                )

                if (
                    existing_tag
                    and existing_tag
                    == normalized_tag
                ):

                    return asset

        return None

    # =====================================================
    # CREATE ASSET
    # =====================================================

    def create_asset(
        self,
        asset_type,
        asset_tag,
        name="",
        description="",
        serial_number="",
        manufacturer="",
        model="",
        metadata=None
    ):

        asset_type = (
            str(asset_type)
            .strip()
            .upper()
        )

        asset_tag = (
            str(asset_tag or "")
            .strip()
        )

        if not asset_type:

            raise ValueError(
                "Asset type cannot be empty."
            )

        if not asset_tag:

            raise ValueError(
                "Asset tag cannot be empty."
            )

        # -------------------------------------------------
        # DUPLICATE CHECK
        # -------------------------------------------------

        duplicate = self.find_duplicate(
            asset_type=asset_type,
            asset_tag=asset_tag,
            serial_number=serial_number
        )

        if duplicate:

            raise DuplicateAssetError(
                f"Asset '{asset_tag}' already exists. "
                f"Asset ID: {duplicate['asset_id']}"
            )

        # -------------------------------------------------
        # CREATE GLOBAL ASSET
        # -------------------------------------------------

        asset_id = self._generate_asset_id()

        asset = {

            "asset_id":
                asset_id,

            "asset_type":
                asset_type,

            "asset_tag":
                asset_tag,

            "name":
                str(name or "").strip(),

            "description":
                str(description or "").strip(),

            "serial_number":
                str(serial_number or "").strip(),

            "manufacturer":
                str(manufacturer or "").strip(),

            "model":
                str(model or "").strip(),

            "metadata":
                metadata or {}
        }

        self.assets[
            asset_id
        ] = asset

        self.save()

        return asset

    # =====================================================
    # GET ALL ASSETS
    # =====================================================

    def get_all_assets(
        self,
        asset_type=None
    ):

        if asset_type is None:

            return list(
                self.assets.values()
            )

        asset_type = (
            str(asset_type)
            .strip()
            .upper()
        )

        return [

            asset

            for asset in self.assets.values()

            if str(
                asset.get(
                    "asset_type",
                    ""
                )
            ).upper()
            == asset_type
        ]

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        search_text="",
        asset_type=None
    ):

        search_text = (
            self._normalize(
                search_text
            )
        )

        results = []

        for asset in self.get_all_assets(
            asset_type=asset_type
        ):

            if not search_text:

                results.append(
                    asset
                )

                continue

            searchable = " ".join([

                str(
                    asset.get(
                        "asset_tag",
                        ""
                    )
                ),

                str(
                    asset.get(
                        "name",
                        ""
                    )
                ),

                str(
                    asset.get(
                        "description",
                        ""
                    )
                ),

                str(
                    asset.get(
                        "serial_number",
                        ""
                    )
                ),

                str(
                    asset.get(
                        "manufacturer",
                        ""
                    )
                ),

                str(
                    asset.get(
                        "model",
                        ""
                    )
                )
            ])

            if (
                search_text
                in self._normalize(
                    searchable
                )
            ):

                results.append(
                    asset
                )

        return results

    # =====================================================
    # UPDATE ASSET
    # =====================================================

    def update_asset(
        self,
        asset_id,
        updates
    ):

        asset = self.get_asset(
            asset_id
        )

        if asset is None:

            raise ValueError(
                "Asset does not exist."
            )

        updates = (
            updates or {}
        )

        # -------------------------------------------------
        # If tag or serial changes,
        # check for duplicates.
        # -------------------------------------------------

        new_type = updates.get(
            "asset_type",
            asset.get("asset_type")
        )

        new_tag = updates.get(
            "asset_tag",
            asset.get("asset_tag")
        )

        new_serial = updates.get(
            "serial_number",
            asset.get("serial_number")
        )

        for existing in self.assets.values():

            if existing["asset_id"] == asset_id:
                continue

            if (
                self._normalize(
                    existing.get(
                        "asset_type"
                    )
                )
                != self._normalize(
                    new_type
                )
            ):
                continue

            if (
                self._normalize(
                    existing.get(
                        "asset_tag"
                    )
                )
                == self._normalize(
                    new_tag
                )
            ):

                raise DuplicateAssetError(
                    f"Asset '{new_tag}' already exists."
                )

            if (
                new_serial
                and
                self._normalize(
                    existing.get(
                        "serial_number"
                    )
                )
                == self._normalize(
                    new_serial
                )
            ):

                raise DuplicateAssetError(
                    f"Serial number '{new_serial}' "
                    f"already exists."
                )

        asset.update(
            updates
        )

        self.save()

        return asset

    # =====================================================
    # DELETE ASSET
    # =====================================================

    def delete_asset(
        self,
        asset_id
    ):

        if asset_id not in self.assets:

            raise ValueError(
                "Asset does not exist."
            )

        del self.assets[
            asset_id
        ]

        self.save()