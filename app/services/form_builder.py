from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QGroupBox,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
)


class ProtectionFormBuilder:

    def __init__(self, definition):

        self.definition = definition

        self.setting_widgets = {}

        self.measurement_widgets = {}

    # =====================================================
    # BUILD COMPLETE FORM
    # =====================================================

    def build(self):

        widget = QWidget()

        layout = QVBoxLayout(widget)

        # -------------------------------------------------
        # SETTINGS
        # -------------------------------------------------

        settings_box = QGroupBox(
            "Settings"
        )

        settings_layout = QFormLayout()

        for setting in self.definition["settings"]:

            line_edit = QLineEdit()

            unit = setting.get(
                "unit",
                ""
            )

            if unit:

                row = QHBoxLayout()

                row.addWidget(
                    line_edit
                )

                row.addWidget(
                    QLabel(unit)
                )

                settings_layout.addRow(
                    setting["label"],
                    row
                )

            else:

                settings_layout.addRow(
                    setting["label"],
                    line_edit
                )

            self.setting_widgets[
                setting["key"]
            ] = line_edit

        settings_box.setLayout(
            settings_layout
        )

        layout.addWidget(
            settings_box
        )

        # -------------------------------------------------
        # MEASUREMENTS
        # -------------------------------------------------

        measurement_box = QGroupBox(
            "Measurement"
        )

        measurement_layout = QVBoxLayout()

        measurement_definition = (
            self.definition["measurements"]
        )

        phases = measurement_definition[
            "phases"
        ]

        fields = measurement_definition[
            "fields"
        ]

        table = QTableWidget()

        table.setRowCount(
            len(phases)
        )

        table.setColumnCount(
            1 + len(fields)
        )

        headers = ["Phase"]

        for field in fields:

            unit = field.get(
                "unit",
                ""
            )

            if unit:

                headers.append(
                    f'{field["label"]} ({unit})'
                )

            else:

                headers.append(
                    field["label"]
                )

        table.setHorizontalHeaderLabels(
            headers
        )

        for row, phase in enumerate(phases):

            table.setItem(
                row,
                0,
                QTableWidgetItem(
                    phase
                )
            )

            self.measurement_widgets[
                phase
            ] = {}

            for column, field in enumerate(fields, start=1):

                edit = QLineEdit()

                table.setCellWidget(
                    row,
                    column,
                    edit
                )

                self.measurement_widgets[
                    phase
                ][
                    field["key"]
                ] = edit

        table.resizeColumnsToContents()

        measurement_layout.addWidget(
            table
        )

        measurement_box.setLayout(
            measurement_layout
        )

        layout.addWidget(
            measurement_box
        )

        return widget

    # =====================================================
    # READ FORM DATA
    # =====================================================

    def get_data(self):

        settings = {}

        for key, widget in self.setting_widgets.items():

            settings[key] = (
                widget.text()
            )

        measurements = {}

        for phase, fields in (
            self.measurement_widgets.items()
        ):

            measurements[phase] = {}

            for key, widget in fields.items():

                measurements[phase][key] = (
                    widget.text()
                )

        return {
            "settings": settings,
            "measurements": measurements,
        }