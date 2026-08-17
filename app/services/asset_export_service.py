from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from app.services.asset_manager import AssetManager
from app.services.component_manager import ComponentManager


class AssetExportService:
    """
    Exports the current project's configured asset database to Excel.

    SQLite remains the testing source of truth. This workbook is a
    structured asset-register snapshot for engineering / maintenance use.
    """

    def __init__(
        self,
        asset_manager: AssetManager,
        component_manager: ComponentManager,
    ):
        self.asset_manager = asset_manager
        self.component_manager = component_manager

    # =========================================================
    # PUBLIC
    # =========================================================

    def export_asset_register(self, output_path):
        output_path = Path(output_path)

        workbook = Workbook()
        default_sheet = workbook.active
        workbook.remove(default_sheet)

        panels = []
        components = []

        for substation in self.asset_manager.get_children(None):
            for switchboard in self.asset_manager.get_children(
                substation.node_id
            ):
                for panel in self.asset_manager.get_children(
                    switchboard.node_id
                ):
                    if str(
                        getattr(panel, "node_type", "")
                    ).upper() != "PANEL":
                        continue

                    panels.append(
                        (
                            substation,
                            switchboard,
                            panel,
                        )
                    )

                    try:
                        panel_components = (
                            self.component_manager.get_panel_components(
                                panel.node_id
                            )
                        )
                    except Exception:
                        panel_components = []

                    for component in panel_components:
                        components.append(
                            (
                                substation,
                                switchboard,
                                panel,
                                component,
                            )
                        )

        self._write_panel_register(workbook, panels)
        self._write_component_register(workbook, components)
        self._write_component_type_sheet(
            workbook,
            "CT Register",
            components,
            (
                "CT",
                "CURRENT TRANSFORMER",
            ),
        )
        self._write_component_type_sheet(
            workbook,
            "Numerical Relay Register",
            components,
            ("NUMERICAL_RELAY",),
        )
        self._write_component_type_sheet(
            workbook,
            "Auxiliary Relay Register",
            components,
            (
                "AUXILIARY_RELAY",
                "AUX RELAY",
            ),
        )
        self._write_component_type_sheet(
            workbook,
            "Meter Register",
            components,
            (
                "METER",
                "AMMETER",
                "VOLTMETER",
                "MULTIFUNCTION_METER",
            ),
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        workbook.save(output_path)
        return output_path

    # =========================================================
    # COMMON SHEET HELPERS
    # =========================================================

    def _new_sheet(self, workbook, title, headers):
        sheet = workbook.create_sheet(title)

        for column, header in enumerate(headers, start=1):
            cell = sheet.cell(
                row=1,
                column=column,
                value=header,
            )
            cell.font = Font(bold=True)
            cell.fill = PatternFill(
                "solid",
                fgColor="333333",
            )
            cell.alignment = Alignment(
                horizontal="center",
                vertical="center",
            )

        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = (
            f"A1:{get_column_letter(len(headers))}1"
        )

        return sheet

    def _finish_sheet(self, sheet):
        thin = Side(
            style="thin",
            color="444444",
        )

        for row in sheet.iter_rows():
            for cell in row:
                cell.border = Border(
                    bottom=thin,
                )
                cell.alignment = Alignment(
                    vertical="top",
                    wrap_text=True,
                )

        for column_cells in sheet.columns:
            max_length = 0

            for cell in column_cells:
                value = "" if cell.value is None else str(cell.value)
                max_length = max(
                    max_length,
                    len(value),
                )

            width = min(
                max(max_length + 2, 12),
                45,
            )

            sheet.column_dimensions[
                get_column_letter(
                    column_cells[0].column
                )
            ].width = width

        sheet.row_dimensions[1].height = 24

    # =========================================================
    # PANEL REGISTER
    # =========================================================

    def _write_panel_register(self, workbook, panels):
        headers = [
            "Substation",
            "Switchboard",
            "Panel",
            "Asset ID",
            "Asset Tag",
            "Feed Equipment",
            "Equipment Type",
            "CT Count",
            "Numerical Relay Count",
            "Auxiliary Relay Count",
            "Meter Count",
        ]

        sheet = self._new_sheet(
            workbook,
            "Panel Register",
            headers,
        )

        for substation, switchboard, panel in panels:
            global_asset = self._get_global_asset(panel)

            sheet.append(
                [
                    substation.name,
                    switchboard.name,
                    panel.name,
                    getattr(panel, "asset_id", ""),
                    (global_asset or {}).get(
                        "asset_tag",
                        "",
                    ),
                    getattr(panel, "equipment_name", ""),
                    getattr(panel, "equipment_type", ""),
                    getattr(panel, "ct_count", 0),
                    getattr(panel, "relay_count", 0),
                    getattr(panel, "aux_count", 0),
                    getattr(panel, "meter_count", 0),
                ]
            )

        self._finish_sheet(sheet)

    # =========================================================
    # COMPONENT REGISTER
    # =========================================================

    def _write_component_register(self, workbook, components):
        headers = [
            "Substation",
            "Switchboard",
            "Panel",
            "Component ID",
            "Component",
            "Component Type",
            "Manufacturer",
            "Model",
            "Serial Number",
            "Description",
        ]

        sheet = self._new_sheet(
            workbook,
            "Component Register",
            headers,
        )

        for substation, switchboard, panel, component in components:
            sheet.append(
                [
                    substation.name,
                    switchboard.name,
                    panel.name,
                    getattr(component, "component_id", ""),
                    getattr(component, "name", ""),
                    getattr(component, "component_type", ""),
                    getattr(component, "manufacturer", ""),
                    getattr(component, "model", ""),
                    getattr(component, "serial_number", ""),
                    getattr(component, "description", ""),
                ]
            )

        self._finish_sheet(sheet)

    # =========================================================
    # TYPE SHEETS
    # =========================================================

    def _write_component_type_sheet(
        self,
        workbook,
        title,
        components,
        allowed_types,
    ):
        normalized = {
            str(value).upper()
            for value in allowed_types
        }

        selected = [
            entry
            for entry in components
            if str(
                getattr(entry[3], "component_type", "")
            ).upper()
            in normalized
        ]

        if title == "CT Register":
            headers = [
                "Substation",
                "Switchboard",
                "Panel",
                "CT",
                "Manufacturer",
                "Model",
                "Serial Number",
                "Primary",
                "Secondary",
                "Ratio",
                "Class",
                "Burden",
                "Core",
            ]

        elif title == "Numerical Relay Register":
            headers = [
                "Substation",
                "Switchboard",
                "Panel",
                "Relay",
                "Manufacturer",
                "Model",
                "Serial Number",
                "Firmware",
                "VT Ratio",
                "Protection Functions",
            ]

        elif title == "Auxiliary Relay Register":
            headers = [
                "Substation",
                "Switchboard",
                "Panel",
                "Auxiliary Relay",
                "Manufacturer",
                "Model",
                "Serial Number",
                "Coil Voltage",
                "Contact Configuration",
            ]

        else:
            headers = [
                "Substation",
                "Switchboard",
                "Panel",
                "Meter",
                "Meter Type",
                "Manufacturer",
                "Model",
                "Serial Number",
                "Accuracy Class",
                "Functions",
            ]

        sheet = self._new_sheet(
            workbook,
            title,
            headers,
        )

        for substation, switchboard, panel, component in selected:
            component_type = str(
                getattr(component, "component_type", "")
            ).upper()

            if component_type in (
                "CT",
                "CURRENT TRANSFORMER",
            ):
                row = [
                    substation.name,
                    switchboard.name,
                    panel.name,
                    component.name,
                    getattr(component, "manufacturer", ""),
                    getattr(component, "model", ""),
                    getattr(component, "serial_number", ""),
                    getattr(component, "ct_primary", ""),
                    getattr(component, "ct_secondary", ""),
                    getattr(component, "ct_ratio", ""),
                    getattr(component, "ct_class", ""),
                    getattr(component, "burden", ""),
                    getattr(component, "core", ""),
                ]

            elif component_type == "NUMERICAL_RELAY":
                row = [
                    substation.name,
                    switchboard.name,
                    panel.name,
                    component.name,
                    getattr(component, "manufacturer", ""),
                    getattr(component, "model", ""),
                    getattr(component, "serial_number", ""),
                    getattr(component, "firmware", ""),
                    getattr(component, "vt_ratio", ""),
                    ", ".join(
                        map(
                            str,
                            getattr(
                                component,
                                "protection_functions",
                                [],
                            ),
                        )
                    ),
                ]

            elif component_type in (
                "AUXILIARY_RELAY",
                "AUX RELAY",
            ):
                row = [
                    substation.name,
                    switchboard.name,
                    panel.name,
                    component.name,
                    getattr(component, "manufacturer", ""),
                    getattr(component, "model", ""),
                    getattr(component, "serial_number", ""),
                    getattr(component, "coil_voltage", ""),
                    getattr(component, "contact_configuration", ""),
                ]

            else:
                row = [
                    substation.name,
                    switchboard.name,
                    panel.name,
                    component.name,
                    getattr(component, "meter_type", ""),
                    getattr(component, "manufacturer", ""),
                    getattr(component, "model", ""),
                    getattr(component, "serial_number", ""),
                    getattr(component, "accuracy_class", ""),
                    ", ".join(
                        map(
                            str,
                            getattr(
                                component,
                                "meter_functions",
                                [],
                            ),
                        )
                    ),
                ]

            sheet.append(row)

        self._finish_sheet(sheet)

    def _get_global_asset(self, node):
        asset_id = getattr(node, "asset_id", None)

        if not asset_id:
            return None

        try:
            return self.asset_manager.get_global_asset(asset_id)
        except Exception:
            return None
