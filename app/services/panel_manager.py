import json
from pathlib import Path

from app.models.panel import Panel


class PanelManager:

    FILE_NAME = "panel_data.json"

    def __init__(self, project_folder):

        self.project_folder = Path(project_folder)

        self.file = (
            self.project_folder /
            self.FILE_NAME
        )

        self.panels = {}

        self.load()

    # =====================================================
    # LOAD
    # =====================================================

    def load(self):

        if not self.file.exists():

            self.panels = {}

            return

        with open(
            self.file,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        self.panels = {}

        for node_id, values in data.items():

            self.panels[node_id] = Panel(
                node_id=node_id,
                **values
            )

    # =====================================================
    # SAVE
    # =====================================================

    def save(self):

        data = {}

        for node_id, panel in self.panels.items():

            data[node_id] = {
                "equipment_tag":
                    panel.equipment_tag,

                "equipment_type":
                    panel.equipment_type,

                "description":
                    panel.description,

                "rated_voltage":
                    panel.rated_voltage,

                "rated_power":
                    panel.rated_power,

                "number_of_cts":
                    panel.number_of_cts,

                "number_of_numerical_relays":
                    panel.number_of_numerical_relays,

                "number_of_auxiliary_relays":
                    panel.number_of_auxiliary_relays,
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
    # GET PANEL
    # =====================================================

    def get_panel(self, node_id):

        return self.panels.get(node_id)

    # =====================================================
    # CREATE / UPDATE PANEL
    # =====================================================

    def save_panel(self, panel):

        self.panels[panel.node_id] = panel

        self.save()