from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QComboBox,
    QGroupBox,
    QLabel,
)

from app.services.thermal_template_service import (
    ThermalTemplateService,
)

from app.models.thermal_template import (
    ThermalCurvePoint,
)


class ThermalTemplateDialog(QDialog):

    def __init__(
        self,
        database,
        manufacturer="",
        model="",
        parent=None
    ):

        super().__init__(
            parent
        )

        self.database = database

        self.service = (
            ThermalTemplateService(
                database
            )
        )

        self.manufacturer_value = (
            manufacturer
        )

        self.model_value = (
            model
        )

        self.setWindowTitle(
            "Thermal Test Template"
        )

        self.setMinimumSize(
            850,
            650
        )

        self.template_id = None

        self.build_ui()

    # =====================================================
    # UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )

        # =================================================
        # BASIC INFORMATION
        # =================================================

        basic_group = QGroupBox(
            "Relay / Template"
        )

        basic_layout = QFormLayout()

        self.protection_function = (
            QLineEdit("49")
        )

        self.protection_function.setReadOnly(
            True
        )

        self.manufacturer = (
            QLineEdit(
                self.manufacturer_value
            )
        )

        self.model = (
            QLineEdit(
                self.model_value
            )
        )

        self.template_name = QLineEdit()

        self.curve_type = QComboBox()

        self.curve_type.addItems(
            [
                "POINT_TABLE",
                "EXPONENTIAL",
            ]
        )

        basic_layout.addRow(
            "Protection Function",
            self.protection_function
        )

        basic_layout.addRow(
            "Manufacturer",
            self.manufacturer
        )

        basic_layout.addRow(
            "Relay Model",
            self.model
        )

        basic_layout.addRow(
            "Template Name",
            self.template_name
        )

        basic_layout.addRow(
            "Curve Type",
            self.curve_type
        )

        basic_group.setLayout(
            basic_layout
        )

        layout.addWidget(
            basic_group
        )

        # =================================================
        # PARAMETERS
        # =================================================

        parameter_group = QGroupBox(
            "Thermal Parameters"
        )

        parameter_layout = QFormLayout()

        self.rated_current = (
            QLineEdit()
        )

        self.pickup_current = (
            QLineEdit("1.0")
        )

        self.thermal_constant = (
            QLineEdit()
        )

        self.cooling_constant = (
            QLineEdit()
        )

        parameter_layout.addRow(
            "Rated Current (A)",
            self.rated_current
        )

        parameter_layout.addRow(
            "Pickup (xIn)",
            self.pickup_current
        )

        parameter_layout.addRow(
            "Thermal Constant (s)",
            self.thermal_constant
        )

        parameter_layout.addRow(
            "Cooling Constant (s)",
            self.cooling_constant
        )

        parameter_group.setLayout(
            parameter_layout
        )

        layout.addWidget(
            parameter_group
        )

        # =================================================
        # CURVE TABLE
        # =================================================

        curve_group = QGroupBox(
            "Thermal Curve"
        )

        curve_layout = QVBoxLayout()

        self.curve_table = QTableWidget()

        self.curve_table.setColumnCount(
            2
        )

        self.curve_table.setHorizontalHeaderLabels(
            [
                "Current (xIn)",
                "Operating Time (s)"
            ]
        )

        curve_layout.addWidget(
            self.curve_table
        )

        # =================================================
        # TABLE BUTTONS
        # =================================================

        table_buttons = QHBoxLayout()

        self.add_point_button = (
            QPushButton(
                "Add Point"
            )
        )

        self.remove_point_button = (
            QPushButton(
                "Remove Point"
            )
        )

        table_buttons.addWidget(
            self.add_point_button
        )

        table_buttons.addWidget(
            self.remove_point_button
        )

        table_buttons.addStretch()

        curve_layout.addLayout(
            table_buttons
        )

        curve_group.setLayout(
            curve_layout
        )

        layout.addWidget(
            curve_group
        )

        # =================================================
        # NOTES
        # =================================================

        self.notes = QLineEdit()

        self.notes.setPlaceholderText(
            "Optional notes / relay documentation reference"
        )

        layout.addWidget(
            QLabel("Notes")

        )

        layout.addWidget(
            self.notes
        )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        buttons.addStretch()

        self.save_button = (
            QPushButton(
                "Save Template"
            )
        )

        self.cancel_button = (
            QPushButton(
                "Cancel"
            )
        )

        buttons.addWidget(
            self.save_button
        )

        buttons.addWidget(
            self.cancel_button
        )

        layout.addLayout(
            buttons
        )

        # =================================================
        # SIGNALS
        # =================================================

        self.add_point_button.clicked.connect(
            self.add_curve_point
        )

        self.remove_point_button.clicked.connect(
            self.remove_curve_point
        )

        self.save_button.clicked.connect(
            self.save_template
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

    # =====================================================
    # ADD POINT
    # =====================================================

    def add_curve_point(self):

        row = (
            self.curve_table.rowCount()
        )

        self.curve_table.insertRow(
            row
        )

        self.curve_table.setItem(
            row,
            0,
            QTableWidgetItem("")
        )

        self.curve_table.setItem(
            row,
            1,
            QTableWidgetItem("")
        )

    # =====================================================
    # REMOVE POINT
    # =====================================================

    def remove_curve_point(self):

        row = (
            self.curve_table.currentRow()
        )

        if row < 0:

            QMessageBox.warning(
                self,
                "Thermal Curve",
                "Select a curve point first."
            )

            return

        self.curve_table.removeRow(
            row
        )

    # =====================================================
    # READ CURVE
    # =====================================================

    def get_curve_points(self):

        points = []

        for row in range(
            self.curve_table.rowCount()
        ):

            current_item = (
                self.curve_table.item(
                    row,
                    0
                )
            )

            time_item = (
                self.curve_table.item(
                    row,
                    1
                )
            )

            if (
                current_item is None
                or
                time_item is None
            ):

                continue

            current_text = (
                current_item.text().strip()
            )

            time_text = (
                time_item.text().strip()
            )

            if (
                not current_text
                and
                not time_text
            ):

                continue

            if (
                not current_text
                or
                not time_text
            ):

                raise ValueError(
                    f"Curve row {row + 1} "
                    "is incomplete."
                )

            current = float(
                current_text
            )

            operating_time = float(
                time_text
            )

            if current <= 0:

                raise ValueError(
                    f"Current in curve row "
                    f"{row + 1} must be greater than zero."
                )

            if operating_time <= 0:

                raise ValueError(
                    f"Operating time in curve row "
                    f"{row + 1} must be greater than zero."
                )

            points.append(
                ThermalCurvePoint(

                    current_multiple=current,

                    operating_time=operating_time
                )
            )

        # -------------------------------------------------
        # Sort
        # -------------------------------------------------

        points.sort(
            key=lambda point:
                point.current_multiple
        )

        # -------------------------------------------------
        # Duplicate current values
        # -------------------------------------------------

        for first, second in zip(
            points,
            points[1:]
        ):

            if (
                first.current_multiple
                ==
                second.current_multiple
            ):

                raise ValueError(
                    "Duplicate current multiples "
                    "are not allowed."
                )

        return points

    # =====================================================
    # SAVE
    # =====================================================

    def save_template(self):

        protection_function = (
            self.protection_function
            .text()
            .strip()
        )

        manufacturer = (
            self.manufacturer
            .text()
            .strip()
        )

        model = (
            self.model
            .text()
            .strip()
        )

        name = (
            self.template_name
            .text()
            .strip()
        )

        if not manufacturer:

            QMessageBox.warning(
                self,
                "Validation",
                "Manufacturer is required."
            )

            return

        if not model:

            QMessageBox.warning(
                self,
                "Validation",
                "Relay model is required."
            )

            return

        if not name:

            QMessageBox.warning(
                self,
                "Validation",
                "Template name is required."
            )

            return

        try:

            rated_current = float(
                self.rated_current
                .text()
                or
                0
            )

            pickup_current = float(
                self.pickup_current
                .text()
                or
                1
            )

            thermal_constant = float(
                self.thermal_constant
                .text()
                or
                0
            )

            cooling_constant = float(
                self.cooling_constant
                .text()
                or
                0
            )

            curve = (
                self.get_curve_points()
            )

        except ValueError as exc:

            QMessageBox.warning(
                self,
                "Validation",
                str(exc)
            )

            return

        curve_type = (
            self.curve_type
            .currentText()
        )

        if (
            curve_type
            ==
            "POINT_TABLE"
            and
            not curve
        ):

            QMessageBox.warning(
                self,
                "Validation",
                "At least one thermal "
                "curve point is required."
            )

            return

        try:

            self.template_id = (
                self.service.create_template(

                    protection_function=(
                        protection_function
                    ),

                    manufacturer=(
                        manufacturer
                    ),

                    model=model,

                    name=name,

                    curve_type=(
                        curve_type
                    ),

                    rated_current=(
                        rated_current
                    ),

                    pickup_current=(
                        pickup_current
                    ),

                    thermal_constant=(
                        thermal_constant
                    ),

                    cooling_constant=(
                        cooling_constant
                    ),

                    curves=curve,

                    notes=(
                        self.notes.text()
                    )
                )
            )

        except ValueError as exc:

            QMessageBox.warning(
                self,
                "Unable to Save",
                str(exc)
            )

            return

        QMessageBox.information(
            self,
            "Template Saved",
            (
                "Thermal template saved successfully.\n\n"
                f"Template ID: {self.template_id}"
            )
        )

        self.accept()