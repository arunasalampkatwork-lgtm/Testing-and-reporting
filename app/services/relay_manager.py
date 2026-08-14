import json
from pathlib import Path

from app.models.relay import Relay


class RelayManager:

    FILE_NAME = "relays.json"

    def __init__(self, project_folder):

        self.project_folder = Path(
            project_folder
        )

        self.file = (
            self.project_folder /
            self.FILE_NAME
        )

        self.relays = {}

        self.load()

    # =====================================================
    # LOAD
    # =====================================================

    def load(self):

        if not self.file.exists():

            self.relays = {}

            return

        with open(
            self.file,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        self.relays = {}

        for relay_id, values in data.items():

            self.relays[relay_id] = Relay(
                relay_id=relay_id,
                **values
            )

    # =====================================================
    # SAVE
    # =====================================================

    def save(self):

        data = {}

        for relay_id, relay in self.relays.items():

            data[relay_id] = {
                "relay_tag":
                    relay.relay_tag,

                "manufacturer":
                    relay.manufacturer,

                "model":
                    relay.model,

                "serial_number":
                    relay.serial_number,

                "protection_functions":
                    relay.protection_functions,
            }

        with open(
            self.file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    # =====================================================
    # ADD / UPDATE
    # =====================================================

    def save_relay(self, relay):

        self.relays[
            relay.relay_id
        ] = relay

        self.save()

    # =====================================================
    # GET
    # =====================================================

    def get_relay(self, relay_id):

        return self.relays.get(
            relay_id
        )

    # =====================================================
    # GET ALL
    # =====================================================

    def get_all(self):

        return list(
            self.relays.values()
        )   