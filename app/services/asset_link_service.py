from pathlib import Path
import json
from uuid import uuid4
from datetime import datetime

from app.models.asset_link import AssetLink


class AssetLinkService:

    def __init__(self, project_folder: Path):

        self.project_folder = project_folder

        self.links_file = (
            project_folder / "asset_links.json"
        )

        self.links = {}

        self.load_links()

    # =========================================================
    # ID
    # =========================================================

    def _generate_id(self):

        return (
            f"LINK-{uuid4().hex[:8].upper()}"
        )

    # =========================================================
    # CREATE LINK
    # =========================================================

    def create_link(
        self,
        source_project_id,
        source_panel_id,
        target_project_id,
        target_panel_id,
        source_panel_name=""
    ):

        # Prevent duplicate link

        for link in self.links.values():

            if (
                link.source_panel_id
                == source_panel_id
                and
                link.target_panel_id
                == target_panel_id
            ):

                return link

        link = AssetLink(

            link_id=self._generate_id(),

            source_project_id=source_project_id,

            source_panel_id=source_panel_id,

            target_project_id=target_project_id,

            target_panel_id=target_panel_id,

            source_panel_name=source_panel_name,

            linked_at=datetime.now().isoformat(
                timespec="seconds"
            )
        )

        self.links[
            link.link_id
        ] = link

        self.save_links()

        return link

    # =========================================================
    # GET LINK
    # =========================================================

    def get_link(
        self,
        target_panel_id
    ):

        for link in self.links.values():

            if (
                link.target_panel_id
                == target_panel_id
            ):

                return link

        return None

    # =========================================================
    # GET ALL LINKS
    # =========================================================

    def get_all_links(self):

        return list(
            self.links.values()
        )

    # =========================================================
    # REMOVE LINK
    # =========================================================

    def remove_link(
        self,
        target_panel_id
    ):

        remove_id = None

        for link_id, link in self.links.items():

            if (
                link.target_panel_id
                == target_panel_id
            ):

                remove_id = link_id
                break

        if remove_id is None:

            return False

        del self.links[
            remove_id
        ]

        self.save_links()

        return True

    # =========================================================
    # SAVE
    # =========================================================

    def save_links(self):

        data = []

        for link in self.links.values():

            data.append({

                "link_id":
                    link.link_id,

                "source_project_id":
                    link.source_project_id,

                "source_panel_id":
                    link.source_panel_id,

                "target_project_id":
                    link.target_project_id,

                "target_panel_id":
                    link.target_panel_id,

                "source_panel_name":
                    link.source_panel_name,

                "linked_at":
                    link.linked_at
            })

        self.links_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.links_file,
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

    def load_links(self):

        if not self.links_file.exists():

            return

        try:

            with open(
                self.links_file,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            for item in data:

                link = AssetLink(

                    link_id=item["link_id"],

                    source_project_id=
                        item["source_project_id"],

                    source_panel_id=
                        item["source_panel_id"],

                    target_project_id=
                        item["target_project_id"],

                    target_panel_id=
                        item["target_panel_id"],

                    source_panel_name=
                        item.get(
                            "source_panel_name",
                            ""
                        ),

                    linked_at=
                        item.get(
                            "linked_at",
                            ""
                        )
                )

                self.links[
                    link.link_id
                ] = link

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError
        ):

            raise ValueError(
                "asset_links.json is corrupted "
                "or invalid."
            )