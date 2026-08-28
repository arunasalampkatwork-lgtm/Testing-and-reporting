from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPainter, QPen, QFont
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QLabel,
    QAbstractItemView,
    QSplitter,
    QWidget,
    QHeaderView,
    QScrollArea,
    QStackedWidget,
)

from app.services.thermal_template_service import ThermalTemplateService
from app.services.thermal_calculator import ThermalCalculator
from app.models.thermal_template import ThermalCurvePoint, ThermalVariable


class ThermalCurvePlot(QWidget):
    """Lightweight curve preview supporting multiple curves."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.curves = []
        self.setMinimumSize(360, 300)

    def set_curves(self, curves):
        self.curves = list(curves or [])
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), self.palette().base())

        rect = self.rect().adjusted(58, 25, -24, -58)
        if rect.width() <= 10 or rect.height() <= 10:
            return

        painter.setPen(QPen(self.palette().mid().color(), 1))
        painter.drawRect(rect)

        valid = []
        for curve in self.curves:
            points = []
            for x, y in curve.get("points", []):
                try:
                    x = float(x)
                    y = float(y)
                except (TypeError, ValueError):
                    continue
                if x > 0 and y >= 0:
                    points.append((x, y))
            if len(points) >= 2:
                valid.append((str(curve.get("label", "Curve")), points))

        if not valid:
            painter.setPen(self.palette().text().color())
            painter.drawText(
                rect,
                Qt.AlignmentFlag.AlignCenter,
                "No curve to display",
            )
            return

        xmin = min(point[0] for _, points in valid for point in points)
        xmax = max(point[0] for _, points in valid for point in points)
        ymin = min(point[1] for _, points in valid for point in points)
        ymax = max(point[1] for _, points in valid for point in points)

        if xmax <= xmin:
            xmax = xmin + 1.0
        if ymax <= ymin:
            ymax = ymin + 1.0

        ymin = max(0.0, ymin)
        ymax = ymax * 1.08 if ymax > 0 else 1.0
        if ymax <= ymin:
            ymax = ymin + 1.0

        def px(x):
            return rect.left() + (x - xmin) / (xmax - xmin) * rect.width()

        def py(y):
            return rect.bottom() - (y - ymin) / (ymax - ymin) * rect.height()

        # Grid
        grid_pen = QPen(self.palette().mid().color(), 1)
        painter.setPen(grid_pen)
        for i in range(1, 5):
            y = rect.top() + i * rect.height() / 5
            painter.drawLine(rect.left(), int(y), rect.right(), int(y))
        for i in range(1, 5):
            x = rect.left() + i * rect.width() / 5
            painter.drawLine(int(x), rect.top(), int(x), rect.bottom())

        palette = [
            self.palette().highlight().color(),
            self.palette().link().color(),
            self.palette().text().color(),
            self.palette().dark().color(),
            self.palette().mid().color(),
        ]

        for index, (label, points) in enumerate(valid):
            color = palette[index % len(palette)]
            painter.setPen(QPen(color, 2))
            previous = None
            for x, y in points:
                current = (px(x), py(y))
                if previous is not None:
                    painter.drawLine(
                        int(previous[0]),
                        int(previous[1]),
                        int(current[0]),
                        int(current[1]),
                    )
                previous = current

        # Axis labels
        painter.setPen(self.palette().text().color())
        painter.setFont(QFont(self.font().family(), 8))
        painter.drawText(
            QRectF(0, rect.bottom() + 10, self.width(), 25),
            Qt.AlignmentFlag.AlignCenter,
            "Current / In",
        )

        painter.save()
        painter.translate(16, rect.center().y())
        painter.rotate(-90)
        painter.drawText(
            QRectF(-rect.height() / 2, -10, rect.height(), 20),
            Qt.AlignmentFlag.AlignCenter,
            "Operating time (s)",
        )
        painter.restore()

        # Legend
        legend_x = rect.left()
        legend_y = self.height() - 22
        painter.setFont(QFont(self.font().family(), 8))
        for index, (label, _) in enumerate(valid):
            color = palette[index % len(palette)]
            painter.setPen(QPen(color, 3))
            painter.drawLine(legend_x, legend_y, legend_x + 16, legend_y)
            painter.setPen(self.palette().text().color())
            painter.drawText(legend_x + 21, legend_y + 4, label[:24])
            legend_x += 145
            if legend_x > self.width() - 100:
                break


class ThermalTemplateEditorDialog(QDialog):
    """Create/edit a thermal template without overlapping controls.

    The left side is intentionally scrollable.  The active curve editor is
    placed in a QStackedWidget, so hidden curve editors never consume layout
    space and cannot overlap the visible controls.
    """

    def __init__(self, database, manufacturer="", model="", template=None, parent=None):
        super().__init__(parent)

        self.service = ThermalTemplateService(database)
        self.template = template
        self.template_id = getattr(template, "template_id", None) if template else None

        self.setWindowTitle(
            "Edit Thermal Template" if template else "Create Thermal Template"
        )
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowSystemMenuHint
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setMinimumSize(950, 650)
        self.resize(1200, 760)

        self.build_ui()

        if template:
            self.populate_template()
        else:
            self.manufacturer_edit.setText(manufacturer)
            self.model_edit.setText(model)
            self.curve_type_combo.setCurrentText("POINT_TABLE")
            self.add_variable(
                "I",
                "xIn",
                "Test current multiple",
                1.0,
                True,
            )

        self.update_mode(self.curve_type_combo.currentText())
        self.update_plot()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def build_ui(self):
        """Build a robust, scrollable editor.

        The three curve editors are ordinary widgets that are shown/hidden
        rather than placed in a stacked widget.  This avoids the geometry
        issue where the point-table page can receive zero usable height.
        """
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(8)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        # ==============================================================
        # LEFT: scrollable template editor
        # ==============================================================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        left_content = QWidget()
        left_content.setMinimumWidth(520)
        left_layout = QVBoxLayout(left_content)
        left_layout.setContentsMargins(8, 8, 12, 8)
        left_layout.setSpacing(10)

        # --------------------------------------------------------------
        # Relay / Template
        # --------------------------------------------------------------
        info = QGroupBox("Relay / Template")
        form = QFormLayout(info)
        form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setVerticalSpacing(8)

        self.protection_edit = QLineEdit("49")
        self.protection_edit.setReadOnly(True)

        self.manufacturer_edit = QLineEdit()
        self.model_edit = QLineEdit()
        self.name_edit = QLineEdit()

        self.curve_type_combo = QComboBox()
        self.curve_type_combo.addItems(
            ["POINT_TABLE", "EXPONENTIAL", "EQUATION"]
        )

        form.addRow("Protection Function:", self.protection_edit)
        form.addRow("Manufacturer:", self.manufacturer_edit)
        form.addRow("Relay Model:", self.model_edit)
        form.addRow("Template Name:", self.name_edit)
        form.addRow("Curve Type:", self.curve_type_combo)
        left_layout.addWidget(info)

        # --------------------------------------------------------------
        # Thermal Parameters
        # --------------------------------------------------------------
        params = QGroupBox("Thermal Parameters")
        pf = QFormLayout(params)
        pf.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        pf.setVerticalSpacing(8)

        self.rated_current_edit = QLineEdit()
        self.pickup_current_edit = QLineEdit("1.0")
        self.thermal_constant_edit = QLineEdit()
        self.cooling_constant_edit = QLineEdit()

        pf.addRow("Rated Current (A):", self.rated_current_edit)
        pf.addRow("Pickup (xIn):", self.pickup_current_edit)
        pf.addRow("Thermal Constant (s):", self.thermal_constant_edit)
        pf.addRow("Cooling Constant (s):", self.cooling_constant_edit)
        left_layout.addWidget(params)

        # ==============================================================
        # POINT TABLE EDITOR
        # ==============================================================
        self.point_page = QWidget()
        point_layout = QVBoxLayout(self.point_page)
        point_layout.setContentsMargins(0, 0, 0, 0)
        point_layout.setSpacing(6)

        self.point_group = QGroupBox("Point Table")
        point_group_layout = QVBoxLayout(self.point_group)
        point_group_layout.setContentsMargins(8, 14, 8, 8)
        point_group_layout.setSpacing(8)

        point_help = QLabel(
            "Enter the relay's current multiple and corresponding "
            "operating time. Add as many points as required."
        )
        point_help.setWordWrap(True)
        point_group_layout.addWidget(point_help)

        self.curve_table = QTableWidget(0, 2)
        self.curve_table.setMinimumHeight(260)
        self.curve_table.setSizePolicy(
            self.curve_table.sizePolicy().horizontalPolicy(),
            self.curve_table.sizePolicy().verticalPolicy(),
        )
        self.curve_table.setHorizontalHeaderLabels(
            ["Current (xIn)", "Operating Time (s)"]
        )
        self.curve_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.curve_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.curve_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.curve_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.curve_table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.curve_table.setAlternatingRowColors(True)
        point_group_layout.addWidget(self.curve_table, 1)

        point_buttons = QHBoxLayout()
        self.add_button = QPushButton("Add Point")
        self.remove_button = QPushButton("Remove Selected")
        self.clear_points_button = QPushButton("Clear All")

        point_buttons.addWidget(self.add_button)
        point_buttons.addWidget(self.remove_button)
        point_buttons.addWidget(self.clear_points_button)
        point_buttons.addStretch()
        point_group_layout.addLayout(point_buttons)

        point_layout.addWidget(self.point_group)
        left_layout.addWidget(self.point_page)

        # ==============================================================
        # EXPONENTIAL EDITOR
        # ==============================================================
        self.exponential_page = QWidget()
        exponential_layout = QVBoxLayout(self.exponential_page)
        exponential_layout.setContentsMargins(0, 0, 0, 0)
        exponential_layout.setSpacing(6)

        exp_group = QGroupBox("Exponential Thermal Characteristic")
        exp_form = QFormLayout(exp_group)
        exp_form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        exp_help = QLabel(
            "The exponential preview uses the configured pickup and "
            "thermal time constant."
        )
        exp_help.setWordWrap(True)
        exp_form.addRow(exp_help)

        self.exp_target_fraction_edit = QLineEdit("0.95")
        exp_form.addRow(
            "Target thermal fraction:",
            self.exp_target_fraction_edit,
        )

        exponential_layout.addWidget(exp_group)
        exponential_layout.addStretch(1)
        left_layout.addWidget(self.exponential_page)

        # ==============================================================
        # EQUATION BUILDER
        # ==============================================================
        self.equation_page = QWidget()
        equation_layout = QVBoxLayout(self.equation_page)
        equation_layout.setContentsMargins(0, 0, 0, 0)
        equation_layout.setSpacing(6)

        self.equation_group = QGroupBox("Equation Builder")
        eq_layout = QVBoxLayout(self.equation_group)
        eq_layout.setContentsMargins(8, 14, 8, 8)
        eq_layout.setSpacing(8)

        help_label = QLabel(
            "Define variables used by the equation. Use ^ for powers, "
            "e.g. K / ((I^2) - 1). Functions: sqrt, exp, log, ln, "
            "log10, abs, min, max, sin, cos, tan."
        )
        help_label.setWordWrap(True)
        eq_layout.addWidget(help_label)

        self.variables_table = QTableWidget(0, 5)
        self.variables_table.setMinimumHeight(220)
        self.variables_table.setHorizontalHeaderLabels(
            ["Variable", "Unit", "Description", "Default", "Input?"]
        )
        self.variables_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.variables_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.variables_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.variables_table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.variables_table.setAlternatingRowColors(True)
        eq_layout.addWidget(self.variables_table, 1)

        variable_buttons = QHBoxLayout()
        self.add_variable_button = QPushButton("Add Variable")
        self.remove_variable_button = QPushButton("Remove Selected")
        variable_buttons.addWidget(self.add_variable_button)
        variable_buttons.addWidget(self.remove_variable_button)
        variable_buttons.addStretch()
        eq_layout.addLayout(variable_buttons)

        eq_form = QFormLayout()
        eq_form.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow
        )
        eq_form.setVerticalSpacing(8)

        self.equation_edit = QLineEdit()
        self.equation_edit.setPlaceholderText(
            "Example: K / ((I^2) - 1)"
        )

        self.independent_edit = QLineEdit("I")
        self.dependent_edit = QLineEdit("T")
        self.x_min_edit = QLineEdit("1.05")
        self.x_max_edit = QLineEdit("20")

        eq_form.addRow("Equation:", self.equation_edit)
        eq_form.addRow("Independent variable:", self.independent_edit)
        eq_form.addRow("Dependent variable:", self.dependent_edit)
        eq_form.addRow("X minimum:", self.x_min_edit)
        eq_form.addRow("X maximum:", self.x_max_edit)
        eq_layout.addLayout(eq_form)

        eq_buttons = QHBoxLayout()
        self.validate_button = QPushButton("Validate & Plot")
        eq_buttons.addWidget(self.validate_button)
        eq_buttons.addStretch()
        eq_layout.addLayout(eq_buttons)

        equation_layout.addWidget(self.equation_group)
        left_layout.addWidget(self.equation_page)

        # Only one curve editor is visible at a time.
        self.point_page.setVisible(True)
        self.exponential_page.setVisible(False)
        self.equation_page.setVisible(False)

        # --------------------------------------------------------------
        # Notes
        # --------------------------------------------------------------
        notes = QGroupBox("Notes")
        nf = QVBoxLayout(notes)
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText(
            "Optional notes / manufacturer documentation reference"
        )
        nf.addWidget(self.notes_edit)
        left_layout.addWidget(notes)

        left_layout.addStretch(1)
        scroll.setWidget(left_content)

        # ==============================================================
        # RIGHT: preview
        # ==============================================================
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 8, 8, 8)
        right_layout.setSpacing(8)

        title = QLabel("Curve Preview")
        title.setStyleSheet("font-size: 15px; font-weight: 600;")
        right_layout.addWidget(title)

        self.plot = ThermalCurvePlot()
        right_layout.addWidget(self.plot, 1)

        self.preview_status = QLabel("Enter curve data to preview.")
        self.preview_status.setWordWrap(True)
        right_layout.addWidget(self.preview_status)

        splitter.addWidget(scroll)
        splitter.addWidget(right)
        splitter.setSizes([700, 500])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        outer.addWidget(splitter, 1)

        # --------------------------------------------------------------
        # Dialog buttons
        # --------------------------------------------------------------
        buttons = QHBoxLayout()
        buttons.addStretch()

        cancel = QPushButton("Cancel")
        save = QPushButton(
            "Update Template" if self.template else "Save Template"
        )

        buttons.addWidget(cancel)
        buttons.addWidget(save)
        outer.addLayout(buttons)

        # --------------------------------------------------------------
        # Signals
        # --------------------------------------------------------------
        self.add_button.clicked.connect(self.add_point)
        self.remove_button.clicked.connect(self.remove_point)
        self.clear_points_button.clicked.connect(self.clear_points)

        self.add_variable_button.clicked.connect(
            lambda: self.add_variable()
        )
        self.remove_variable_button.clicked.connect(
            self.remove_variable
        )

        self.curve_type_combo.currentTextChanged.connect(self.update_mode)
        self.curve_table.itemChanged.connect(
            lambda *_: self.update_plot()
        )
        self.variables_table.itemChanged.connect(
            lambda *_: self.update_plot()
        )
        self.equation_edit.textChanged.connect(
            lambda *_: self.update_plot()
        )
        self.independent_edit.textChanged.connect(
            lambda *_: self.update_plot()
        )
        self.x_min_edit.textChanged.connect(
            lambda *_: self.update_plot()
        )
        self.x_max_edit.textChanged.connect(
            lambda *_: self.update_plot()
        )
        self.pickup_current_edit.textChanged.connect(
            lambda *_: self.update_plot()
        )
        self.thermal_constant_edit.textChanged.connect(
            lambda *_: self.update_plot()
        )
        self.exp_target_fraction_edit.textChanged.connect(
            lambda *_: self.update_plot()
        )

        self.validate_button.clicked.connect(self.validate_equation)
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.save)

    # ------------------------------------------------------------------
    # Point-table helper
    # ------------------------------------------------------------------

    def clear_points(self):
        self.curve_table.setRowCount(0)
        self.update_plot()

    # ------------------------------------------------------------------
    # Mode handling
    # ------------------------------------------------------------------

    def update_mode(self, mode):
        # Show exactly one editor.  Hidden widgets are removed from the
        # layout, so they cannot steal vertical space from the active editor.
        self.point_page.setVisible(mode == "POINT_TABLE")
        self.exponential_page.setVisible(mode == "EXPONENTIAL")
        self.equation_page.setVisible(mode == "EQUATION")

        self.thermal_constant_edit.setEnabled(mode == "EXPONENTIAL")
        self.exp_target_fraction_edit.setEnabled(mode == "EXPONENTIAL")

        self.update_plot()

    # ------------------------------------------------------------------
    # Point table
    # ------------------------------------------------------------------

    def add_point(self, current="", operating_time=""):
        row = self.curve_table.rowCount()
        self.curve_table.insertRow(row)
        self.curve_table.setItem(row, 0, QTableWidgetItem(str(current)))
        self.curve_table.setItem(row, 1, QTableWidgetItem(str(operating_time)))
        self.curve_table.setCurrentCell(row, 0)

    def remove_point(self):
        row = self.curve_table.currentRow()
        if row >= 0:
            self.curve_table.removeRow(row)
            self.update_plot()

    def read_curve(self):
        points = []
        for row in range(self.curve_table.rowCount()):
            a = self.curve_table.item(row, 0)
            b = self.curve_table.item(row, 1)
            at = a.text().strip() if a else ""
            bt = b.text().strip() if b else ""

            if not at and not bt:
                continue
            if not at or not bt:
                raise ValueError(f"Curve row {row + 1} is incomplete.")

            try:
                x = float(at)
                y = float(bt)
            except ValueError as exc:
                raise ValueError(
                    f"Curve row {row + 1} contains an invalid number."
                ) from exc

            if x <= 0 or y <= 0:
                raise ValueError(
                    f"Curve row {row + 1} must contain positive values."
                )

            points.append(ThermalCurvePoint(x, y))

        points.sort(key=lambda p: p.current_multiple)

        if any(
            a.current_multiple == b.current_multiple
            for a, b in zip(points, points[1:])
        ):
            raise ValueError("Duplicate current multiples are not allowed.")

        return points

    # ------------------------------------------------------------------
    # Variables / equation
    # ------------------------------------------------------------------

    def add_variable(
        self,
        name="",
        unit="",
        description="",
        default=0.0,
        is_input=False,
    ):
        row = self.variables_table.rowCount()
        self.variables_table.insertRow(row)
        values = [
            name,
            unit,
            description,
            str(default),
            "1" if is_input else "0",
        ]
        for col, value in enumerate(values):
            self.variables_table.setItem(
                row,
                col,
                QTableWidgetItem(str(value)),
            )

    def remove_variable(self):
        row = self.variables_table.currentRow()
        if row >= 0:
            self.variables_table.removeRow(row)
            self.update_plot()

    def read_variables(self):
        variables = []
        names = set()

        for row in range(self.variables_table.rowCount()):
            name_item = self.variables_table.item(row, 0)
            name = name_item.text().strip() if name_item else ""
            if not name:
                continue

            if not name.replace("_", "").isalnum() or name[0].isdigit():
                raise ValueError(
                    f"Invalid variable name '{name}'. "
                    "Use letters, numbers and underscore, starting with a letter."
                )

            if name in names:
                raise ValueError(f"Duplicate variable name '{name}'.")
            names.add(name)

            unit_item = self.variables_table.item(row, 1)
            desc_item = self.variables_table.item(row, 2)
            default_item = self.variables_table.item(row, 3)
            input_item = self.variables_table.item(row, 4)

            unit = unit_item.text().strip() if unit_item else ""
            description = desc_item.text().strip() if desc_item else ""
            default_text = default_item.text().strip() if default_item else "0"
            input_text = input_item.text().strip().lower() if input_item else "0"

            try:
                default_value = float(default_text or 0)
            except ValueError as exc:
                raise ValueError(
                    f"Default value for variable '{name}' is invalid."
                ) from exc

            is_input = input_text in {"1", "yes", "true", "y"}

            variables.append(
                ThermalVariable(
                    name=name,
                    unit=unit,
                    description=description,
                    default_value=default_value,
                    is_input=is_input,
                )
            )

        return variables

    def equation_data(self):
        variables = self.read_variables()
        names = [v.name for v in variables]

        if not names:
            raise ValueError("Add at least one variable before defining the equation.")

        independent = self.independent_edit.text().strip() or "I"
        if independent not in names:
            raise ValueError(
                f"Independent variable '{independent}' must be defined in the variable table."
            )

        equation = ThermalCalculator.validate_equation(
            self.equation_edit.text(),
            names,
        )

        # Parameters are all non-independent variables.  If a variable is
        # marked Input?, its default value is still used for plotting.
        parameters = {
            variable.name: variable.default_value
            for variable in variables
            if variable.name != independent
        }

        try:
            x_min = float(self.x_min_edit.text())
            x_max = float(self.x_max_edit.text())
        except ValueError as exc:
            raise ValueError("X minimum and X maximum must be valid numbers.") from exc

        if x_min <= 0 or x_max <= x_min:
            raise ValueError("X range is invalid.")

        dependent = self.dependent_edit.text().strip() or "T"

        return (
            variables,
            equation,
            parameters,
            independent,
            dependent,
            x_min,
            x_max,
        )

    def validate_equation(self):
        try:
            self.equation_data()
            points = self._equation_points()
            if len(points) < 2:
                raise ValueError(
                    "The equation is valid, but it did not produce enough "
                    "finite points in the selected range."
                )
            self.preview_status.setText(
                f"Equation is valid. {len(points)} points plotted."
            )
            self.plot.set_curves(
                [{
                    "label": self.name_edit.text() or "Equation",
                    "points": points,
                }]
            )
        except Exception as exc:
            self.plot.set_curves([])
            self.preview_status.setText(str(exc))
            QMessageBox.warning(self, "Equation Validation", str(exc))

    def _equation_points(self):
        (
            variables,
            equation,
            parameters,
            independent,
            _dependent,
            x_min,
            x_max,
        ) = self.equation_data()

        template = type("EquationPreviewTemplate", (), {})()
        template.equation = equation
        template.parameters = parameters
        template.independent_variable = independent
        template.x_min = x_min
        template.x_max = x_max

        return ThermalCalculator.generate_equation_curve(template, 160)

    # ------------------------------------------------------------------
    # Preview
    # ------------------------------------------------------------------

    def update_plot(self):
        mode = self.curve_type_combo.currentText()

        try:
            if mode == "POINT_TABLE":
                points = [
                    (p.current_multiple, p.operating_time)
                    for p in self.read_curve()
                ]
                self.plot.set_curves([
                    {
                        "label": self.name_edit.text() or "Point table",
                        "points": points,
                    }
                ])
                self.preview_status.setText(
                    f"{len(points)} point(s) loaded."
                    if points
                    else "Enter curve points to preview."
                )

            elif mode == "EQUATION":
                try:
                    points = self._equation_points()
                except Exception:
                    self.plot.set_curves([])
                    self.preview_status.setText(
                        "Enter valid equation data to preview."
                    )
                    return

                self.plot.set_curves([
                    {
                        "label": self.name_edit.text() or "Equation",
                        "points": points,
                    }
                ])
                self.preview_status.setText(
                    f"{len(points)} equation point(s) plotted."
                    if points
                    else "Equation produced no plottable points."
                )

            else:
                pickup = float(self.pickup_current_edit.text() or 1)
                tau = float(self.thermal_constant_edit.text() or 0)
                target = float(self.exp_target_fraction_edit.text() or 0.95)

                if tau <= 0:
                    raise ValueError
                if not 0 < target < 1:
                    raise ValueError

                points = []
                upper = max(20.0, pickup + 0.01)
                for i in range(120):
                    x = pickup + (upper - pickup) * i / 119
                    y = ThermalCalculator.exponential_time(
                        x,
                        pickup,
                        tau,
                        target,
                    )
                    if y != float("inf") and y >= 0:
                        points.append((x, y))

                self.plot.set_curves([
                    {
                        "label": self.name_edit.text() or "Exponential",
                        "points": points,
                    }
                ])
                self.preview_status.setText(
                    f"{len(points)} exponential point(s) plotted."
                )

        except Exception:
            self.plot.set_curves([])
            self.preview_status.setText("Enter valid curve data to preview.")

    # ------------------------------------------------------------------
    # Populate existing template
    # ------------------------------------------------------------------

    def populate_template(self):
        t = self.template

        self.manufacturer_edit.setText(t.manufacturer)
        self.model_edit.setText(t.model)
        self.name_edit.setText(t.name)
        self.curve_type_combo.setCurrentText(t.curve_type)

        self.rated_current_edit.setText(f"{t.rated_current:g}")
        self.pickup_current_edit.setText(f"{t.pickup_current:g}")
        self.thermal_constant_edit.setText(f"{t.thermal_constant:g}")
        self.cooling_constant_edit.setText(f"{t.cooling_constant:g}")

        self.notes_edit.setText(t.notes)

        self.equation_edit.setText(t.equation)
        self.independent_edit.setText(t.independent_variable)
        self.dependent_edit.setText(t.dependent_variable)
        self.x_min_edit.setText(f"{t.x_min:g}")
        self.x_max_edit.setText(f"{t.x_max:g}")

        self.curve_table.setRowCount(0)
        for point in t.curves:
            self.add_point(
                point.current_multiple,
                point.operating_time,
            )

        self.variables_table.setRowCount(0)
        for variable in t.variables:
            self.add_variable(
                variable.name,
                variable.unit,
                variable.description,
                variable.default_value,
                variable.is_input,
            )

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save(self):
        try:
            manufacturer = self.manufacturer_edit.text().strip()
            model = self.model_edit.text().strip()
            name = self.name_edit.text().strip()

            if not manufacturer:
                raise ValueError("Manufacturer is required.")
            if not model:
                raise ValueError("Relay model is required.")
            if not name:
                raise ValueError("Template name is required.")

            try:
                rated = float(self.rated_current_edit.text() or 0)
                pickup = float(self.pickup_current_edit.text() or 1)
                tau = float(self.thermal_constant_edit.text() or 0)
                cooling = float(self.cooling_constant_edit.text() or 0)
            except ValueError as exc:
                raise ValueError(
                    "Rated current, pickup and thermal constants must be valid numbers."
                ) from exc

            mode = self.curve_type_combo.currentText()
            curve = []

            if mode == "POINT_TABLE":
                curve = self.read_curve()
                if len(curve) < 2:
                    raise ValueError(
                        "Point-table curves require at least two points."
                    )

            variables = []
            equation = ""
            parameters = {}
            independent = "I"
            dependent = "T"
            x_min = 1.0
            x_max = 20.0

            if mode == "EQUATION":
                (
                    variables,
                    equation,
                    parameters,
                    independent,
                    dependent,
                    x_min,
                    x_max,
                ) = self.equation_data()

                points = self._equation_points()
                if len(points) < 2:
                    raise ValueError(
                        "The equation does not produce enough finite curve points "
                        "in the selected range."
                    )

            if mode == "EXPONENTIAL":
                if tau <= 0:
                    raise ValueError(
                        "Thermal constant must be positive for exponential curves."
                    )
                try:
                    target = float(self.exp_target_fraction_edit.text() or 0.95)
                except ValueError as exc:
                    raise ValueError(
                        "Target thermal fraction must be a valid number."
                    ) from exc
                if not 0 < target < 1:
                    raise ValueError(
                        "Target thermal fraction must be between 0 and 1."
                    )

            data = dict(
                protection_function="49",
                manufacturer=manufacturer,
                model=model,
                name=name,
                curve_type=mode,
                rated_current=rated,
                pickup_current=pickup,
                thermal_constant=tau,
                cooling_constant=cooling,
                curves=curve,
                equation=equation,
                independent_variable=independent,
                dependent_variable=dependent,
                variables=variables,
                parameters=parameters,
                x_min=x_min,
                x_max=x_max,
                notes=self.notes_edit.text().strip(),
            )

            if self.template_id is None:
                self.template_id = self.service.create_template(**data)
            else:
                self.service.update_template(
                    self.template_id,
                    **data,
                )

        except Exception as exc:
            QMessageBox.warning(
                self,
                "Save Failed",
                str(exc),
            )
            return

        self.accept()


class ThermalTemplateManagerDialog(QDialog):
    """Manage all thermal templates for one relay and display all curves."""

    def __init__(self, database, manufacturer="", model="", parent=None):
        super().__init__(parent)

        self.database = database
        self.service = ThermalTemplateService(database)
        self.manufacturer = manufacturer
        self.model = model
        self.templates = []

        self.setWindowTitle(
            f"Thermal Templates - {manufacturer} {model}"
        )
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowSystemMenuHint
            | Qt.WindowType.WindowMinimizeButtonHint
            | Qt.WindowType.WindowMaximizeButtonHint
            | Qt.WindowType.WindowCloseButtonHint
        )
        self.setMinimumSize(950, 620)
        self.resize(1200, 720)

        self.build_ui()
        self.refresh()

    def build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        header = QLabel(
            f"Relay: {self.manufacturer} {self.model}\n"
            "Protection Function: 49 - Thermal Overload"
        )
        header.setStyleSheet(
            "font-size:16px; font-weight:700; padding:6px;"
        )
        layout.addWidget(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)

        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(4, 4, 4, 4)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            [
                "Template",
                "Curve Type",
                "Rated Current (A)",
                "Pickup (xIn)",
                "Thermal Constant (s)",
            ]
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        ll.addWidget(self.table, 1)

        bl = QHBoxLayout()
        self.new_button = QPushButton("New Template")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        bl.addWidget(self.new_button)
        bl.addWidget(self.edit_button)
        bl.addWidget(self.delete_button)
        bl.addStretch()
        ll.addLayout(bl)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(4, 4, 4, 4)

        curve_title = QLabel("All Configured Thermal Curves")
        curve_title.setStyleSheet("font-size:15px; font-weight:600;")
        rl.addWidget(curve_title)

        self.all_plot = ThermalCurvePlot()
        rl.addWidget(self.all_plot, 1)

        self.curve_status = QLabel()
        self.curve_status.setWordWrap(True)
        rl.addWidget(self.curve_status)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([650, 550])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter, 1)

        close = QPushButton("Close")
        cb = QHBoxLayout()
        cb.addStretch()
        cb.addWidget(close)
        layout.addLayout(cb)

        self.new_button.clicked.connect(self.create_template)
        self.edit_button.clicked.connect(self.edit_template)
        self.delete_button.clicked.connect(self.delete_template)
        close.clicked.connect(self.accept)
        self.table.itemSelectionChanged.connect(self.update_all_plot)
        self.table.itemDoubleClicked.connect(lambda *_: self.edit_template())

    def refresh(self):
        self.templates = self.service.get_templates_for_relay(
            self.manufacturer,
            self.model,
            "49",
        )

        self.table.setRowCount(0)

        for template in self.templates:
            row = self.table.rowCount()
            self.table.insertRow(row)

            values = [
                template.name,
                template.curve_type,
                f"{template.rated_current:g}",
                f"{template.pickup_current:g}",
                f"{template.thermal_constant:g}",
            ]

            for column, value in enumerate(values):
                self.table.setItem(
                    row,
                    column,
                    QTableWidgetItem(str(value)),
                )

        self.update_all_plot()

    def curve_points(self, template):
        if template.curve_type == "POINT_TABLE":
            return [
                (point.current_multiple, point.operating_time)
                for point in template.curves
            ]

        if template.curve_type == "EQUATION":
            try:
                return ThermalCalculator.generate_equation_curve(
                    template,
                    160,
                )
            except Exception:
                return []

        # EXPONENTIAL
        points = []
        try:
            target = 0.95
            for i in range(120):
                x = template.pickup_current + (
                    20.0 - template.pickup_current
                ) * i / 119
                y = ThermalCalculator.exponential_time(
                    x,
                    template.pickup_current,
                    template.thermal_constant,
                    target,
                )
                if y != float("inf") and y >= 0:
                    points.append((x, y))
        except Exception:
            return []

        return points

    def update_all_plot(self):
        curves = []
        for template in self.templates:
            points = self.curve_points(template)
            if len(points) >= 2:
                curves.append(
                    {
                        "label": template.name,
                        "points": points,
                    }
                )

        self.all_plot.set_curves(curves)
        self.curve_status.setText(
            f"{len(curves)} curve(s) displayed. "
            "All configured thermal templates for this relay are included."
        )

    def selected_template(self):
        row = self.table.currentRow()
        if 0 <= row < len(self.templates):
            return self.templates[row]
        return None

    def create_template(self):
        dialog = ThermalTemplateEditorDialog(
            self.database,
            self.manufacturer,
            self.model,
            parent=self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def edit_template(self):
        template = self.selected_template()
        if template is None:
            QMessageBox.warning(
                self,
                "No Template Selected",
                "Select a thermal template first.",
            )
            return

        dialog = ThermalTemplateEditorDialog(
            self.database,
            template=template,
            parent=self,
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh()

    def delete_template(self):
        template = self.selected_template()
        if template is None:
            QMessageBox.warning(
                self,
                "No Template Selected",
                "Select a thermal template first.",
            )
            return

        answer = QMessageBox.question(
            self,
            "Delete Thermal Template",
            f"Delete template '{template.name}'?\n\nThis cannot be undone.",
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:
            self.service.delete_template(template.template_id)
            self.refresh()
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Delete Failed",
                str(exc),
            )
