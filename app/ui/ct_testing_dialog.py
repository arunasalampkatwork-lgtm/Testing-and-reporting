from types import SimpleNamespace

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QScrollArea,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
class CTTestingDialog(QDialog):

    """
    CT testing dialog.

    Supports:

        - New CT test
        - Editing an existing CT test
        - Single-phase CT
        - Three-phase CT
        - Ratio calculation
        - Ratio error
        - Polarity
        - Insulation resistance
        - Winding resistance
        - Knee point
        - Burden
        - Historical CT test snapshots

    Three-phase ratio data is stored as:

        phase_tests = [
            {
                "phase": "R",
                "primary_current": "...",
                "secondary_current": "...",
                "measured_ratio": "...",
                "ratio_error": "..."
            },
            ...
        ]
    """

    def __init__(
        self,
        project_id,
        panel_id,
        component=None,
        test_service=None,
        test_id=None,
        existing_test=None,
        parent=None,
    ):

        super().__init__(
            parent
        )

        self.project_id = (
            project_id
        )

        self.panel_id = (
            panel_id
        )

        self.component = (
            component
        )

        self.test_service = (
            test_service
        )

        self.test_id = (
            test_id
        )

        self.existing_test = (
            existing_test
        )

        self.fields = {}

        self.phase_rows = {}

        self.setWindowTitle(
            "CT Testing"
            if not test_id
            else "Edit CT Test"
        )

        self.resize(
            1050,
            850
        )

        # -------------------------------------------------
        # HISTORICAL COMPONENT SNAPSHOT
        # -------------------------------------------------

        if (
            self.component is None
            and existing_test is not None
        ):

            measurements = (
                existing_test.get(
                    "measurements",
                    {}
                )
                or {}
            )

            self.component = (
                SimpleNamespace(

                    name=measurements.get(
                        "ct_name",
                        existing_test.get(
                            "component_id",
                            ""
                        )
                    ),

                    ct_primary=measurements.get(
                        "ct_primary",
                        ""
                    ),

                    ct_secondary=measurements.get(
                        "ct_secondary",
                        ""
                    ),

                    ct_ratio=measurements.get(
                        "ct_ratio",
                        ""
                    ),

                    core=measurements.get(
                        "core",
                        ""
                    ),

                    ct_class=measurements.get(
                        "ct_class",
                        ""
                    ),

                    burden=measurements.get(
                        "burden",
                        ""
                    ),

                    manufacturer=measurements.get(
                        "manufacturer",
                        ""
                    ),

                    model=measurements.get(
                        "model",
                        ""
                    ),

                    serial_number=measurements.get(
                        "serial_number",
                        ""
                    ),
                )
            )

        self.build_ui()

        if self.existing_test:

            self.populate_existing_test()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(
        self
    ):

        main_layout = QVBoxLayout(
            self
        )

        # =================================================
        # HEADER
        # =================================================

        header = QLabel(
            "CURRENT TRANSFORMER TESTING"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 21px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )

        main_layout.addWidget(
            header
        )

        # =================================================
        # SCROLL
        # =================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(
            True
        )

        container = QDialog()

        container_layout = QVBoxLayout(
            container
        )

        # =================================================
        # CT IDENTIFICATION
        # =================================================

        identification = QGroupBox(
            "CT Identification"
        )

        identification_layout = QFormLayout()

        self.add_field(
            identification_layout,
            "ct_primary",
            "CT Primary",
            getattr(
                self.component,
                "ct_primary",
                ""
            ),
            "A"
        )

        self.add_field(
            identification_layout,
            "ct_secondary",
            "CT Secondary",
            getattr(
                self.component,
                "ct_secondary",
                ""
            ),
            "A"
        )

        self.add_readonly(
            identification_layout,
            "nominal_current",
            "Nominal Current (In)",
            "A"
        )

        self.add_readonly(
            identification_layout,
            "ct_ratio",
            "CT Ratio"
        )

        self.add_field(
            identification_layout,
            "core",
            "Core",
            getattr(
                self.component,
                "core",
                ""
            )
        )

        self.add_field(
            identification_layout,
            "ct_class",
            "CT Class",
            getattr(
                self.component,
                "ct_class",
                ""
            )
        )

        self.add_field(
            identification_layout,
            "burden",
            "Rated Burden",
            getattr(
                self.component,
                "burden",
                ""
            )
        )

        self.add_field(
            identification_layout,
            "manufacturer",
            "Manufacturer",
            getattr(
                self.component,
                "manufacturer",
                ""
            )
        )

        self.add_field(
            identification_layout,
            "model",
            "Model",
            getattr(
                self.component,
                "model",
                ""
            )
        )

        self.add_field(
            identification_layout,
            "serial_number",
            "Serial Number",
            getattr(
                self.component,
                "serial_number",
                ""
            )
        )

        identification.setLayout(
            identification_layout
        )

        container_layout.addWidget(
            identification
        )

        # =================================================
        # THREE PHASE SELECTION
        # =================================================

        phase_group = QGroupBox(
            "CT Phase Configuration"
        )

        phase_layout = QFormLayout()

        self.three_phase_selector = QComboBox()

        self.three_phase_selector.addItems(
            [
                "No",
                "Yes"
            ]
        )

        phase_layout.addRow(
            "Is this a 3-Phase CT?",
            self.three_phase_selector
        )

        phase_group.setLayout(
            phase_layout
        )

        container_layout.addWidget(
            phase_group
        )

        # =================================================
        # RATIO TEST
        # =================================================
        # Keep the ratio test in its original position:
        # CT Identification -> Phase Configuration -> Ratio Test.
        # Only the table dimensions are enlarged.

        self.ratio_group = QGroupBox(
            "CT Ratio Test"
        )

        ratio_layout = QVBoxLayout(
            self.ratio_group
        )

        ratio_layout.setContentsMargins(
            12,
            16,
            12,
            12
        )

        ratio_layout.setSpacing(
            10
        )

        ratio_help = QLabel(
            "Inject the specified primary current and record the "
            "corresponding CT secondary current. Measured ratio "
            "and ratio error are calculated automatically."
        )

        ratio_help.setWordWrap(
            True
        )

        ratio_help.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                padding: 4px;
            }
            """
        )

        ratio_layout.addWidget(
            ratio_help
        )

        self.phase_table = QTableWidget()

        self.phase_table.setObjectName(
            "CTRatioTable"
        )

        self.phase_table.setColumnCount(
            6
        )

        self.phase_table.setHorizontalHeaderLabels(
            [
                "Phase",
                "Injected Primary (A)",
                "Recorded Secondary (A)",
                "Measured Ratio",
                "Ratio Error (%)",
                "Result",
            ]
        )

        self.phase_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.phase_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.phase_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.phase_table.setAlternatingRowColors(
            True
        )

        self.phase_table.setWordWrap(
            False
        )

        self.phase_table.setShowGrid(
            True
        )

        self.phase_table.setStyleSheet(
            """
            QTableWidget {
                font-size: 14px;
                alternate-background-color: #333333;
                background: #2b2b2b;
                gridline-color: #555555;
            }

            QTableWidget::item {
                padding: 8px;
            }

            QHeaderView::section {
                font-weight: bold;
                padding: 10px;
            }
            """
        )

        # -------------------------------------------------
        # TABLE HEADER
        # -------------------------------------------------

        table_header = (
            self.phase_table.horizontalHeader()
        )

        table_header.setMinimumHeight(
            52
        )

        table_header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        table_header.setStretchLastSection(
            False
        )

        table_header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Fixed
        )

        self.phase_table.setColumnWidth(
            0,
            90
        )

        for column in (1, 2, 3, 4):
            table_header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Stretch
            )

        table_header.setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.Fixed
        )

        self.phase_table.setColumnWidth(
            5,
            110
        )

        # -------------------------------------------------
        # ROW HEIGHT
        # -------------------------------------------------

        self.phase_table.verticalHeader().setDefaultSectionSize(
            62
        )

        self.phase_table.verticalHeader().setMinimumSectionSize(
            56
        )

        self.phase_table.verticalHeader().setVisible(
            False
        )

        # -------------------------------------------------
        # BIGGER TABLE, SAME POSITION
        # -------------------------------------------------

        self.phase_table.setMinimumHeight(
            150
        )

        self.phase_table.setMaximumHeight(
            380
        )

        ratio_layout.addWidget(
            self.phase_table
        )

        # Ratio group remains in the same place in the
        # scrolling content, immediately after phase configuration.
        container_layout.addWidget(
            self.ratio_group
        )

        # =================================================
        # POLARITY
        # =================================================

        polarity_group = QGroupBox(
            "Polarity Test"
        )

        polarity_layout = QFormLayout()

        self.add_combo(
            polarity_layout,
            "expected_polarity",
            "Expected Polarity",
            [
                "CORRECT",
                "REVERSE"
            ]
        )

        self.add_combo(
            polarity_layout,
            "observed_polarity",
            "Observed Polarity",
            [
                "CORRECT",
                "REVERSE"
            ]
        )

        self.add_readonly(
            polarity_layout,
            "polarity_result",
            "Polarity Result"
        )

        polarity_group.setLayout(
            polarity_layout
        )

        container_layout.addWidget(
            polarity_group
        )

        self.fields[
            "expected_polarity"
        ].currentTextChanged.connect(
            self.calculate_polarity
        )

        self.fields[
            "observed_polarity"
        ].currentTextChanged.connect(
            self.calculate_polarity
        )

        # =================================================
        # INSULATION RESISTANCE
        # =================================================

        ir_group = QGroupBox(
            "Insulation Resistance"
        )

        ir_layout = QFormLayout()

        self.add_field(
            ir_layout,
            "ir_primary_earth",
            "Primary - Earth",
            "",
            "MΩ"
        )

        self.add_field(
            ir_layout,
            "ir_secondary_earth",
            "Secondary - Earth",
            "",
            "MΩ"
        )

        self.add_field(
            ir_layout,
            "ir_primary_secondary",
            "Primary - Secondary",
            "",
            "MΩ"
        )

        self.add_field(
            ir_layout,
            "ir_test_voltage",
            "Test Voltage",
            "",
            "V"
        )

        self.add_field(
            ir_layout,
            "ir_test_duration",
            "Test Duration",
            "",
            "s"
        )

        ir_group.setLayout(
            ir_layout
        )

        container_layout.addWidget(
            ir_group
        )

        # =================================================
        # WINDING RESISTANCE
        # =================================================

        winding_group = QGroupBox(
            "Winding Resistance"
        )

        winding_layout = QFormLayout()

        self.add_field(
            winding_layout,
            "resistance_phase_a",
            "Phase A",
            "",
            "Ω"
        )

        self.add_field(
            winding_layout,
            "resistance_phase_b",
            "Phase B",
            "",
            "Ω"
        )

        self.add_field(
            winding_layout,
            "resistance_phase_c",
            "Phase C",
            "",
            "Ω"
        )

        winding_group.setLayout(
            winding_layout
        )

        container_layout.addWidget(
            winding_group
        )

        # =================================================
        # KNEE POINT
        # =================================================

        knee_group = QGroupBox(
            "Knee Point / Excitation"
        )

        knee_layout = QFormLayout()

        self.add_field(
            knee_layout,
            "knee_point_voltage",
            "Knee Point Voltage",
            "",
            "V"
        )

        self.add_field(
            knee_layout,
            "knee_point_current",
            "Knee Point Current",
            "",
            "A"
        )

        self.add_field(
            knee_layout,
            "excitation_test_voltage",
            "Excitation Test Voltage",
            "",
            "V"
        )

        self.add_field(
            knee_layout,
            "excitation_test_current",
            "Excitation Test Current",
            "",
            "A"
        )

        knee_group.setLayout(
            knee_layout
        )

        container_layout.addWidget(
            knee_group
        )

        # =================================================
        # BURDEN
        # =================================================

        burden_group = QGroupBox(
            "Burden Test"
        )

        burden_layout = QFormLayout()

        self.add_field(
            burden_layout,
            "burden_test_current",
            "Burden Test Current",
            "",
            "A"
        )

        self.add_field(
            burden_layout,
            "measured_burden",
            "Measured Burden",
            "",
            "VA"
        )

        self.add_readonly(
            burden_layout,
            "burden_error",
            "Burden Error",
            "%"
        )

        burden_group.setLayout(
            burden_layout
        )

        container_layout.addWidget(
            burden_group
        )

        self.fields[
            "measured_burden"
        ].textChanged.connect(
            self.calculate_burden
        )

        # =================================================
        # TOLERANCE
        # =================================================

        self.add_field(
            container_layout,
            "tolerance_percent",
            "Tolerance",
            "5",
            "%"
        )

        # =================================================
        # RESULT
        # =================================================

        self.add_readonly(
            container_layout,
            "result",
            "Overall Result"
        )

        # =================================================
        # REMARKS
        # =================================================

        self.add_field(
            container_layout,
            "remarks",
            "Remarks",
            ""
        )

        scroll.setWidget(
            container
        )

        main_layout.addWidget(
            scroll
        )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        self.clear_button = QPushButton(
            "Clear"
        )

        self.save_button = QPushButton(
            "Update Test"
            if self.test_id
            else
            "Save Test"
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.clear_button.clicked.connect(
            self.clear_fields
        )

        self.save_button.clicked.connect(
            self.save_test
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        buttons.addWidget(
            self.clear_button
        )

        buttons.addWidget(
            self.save_button
        )

        buttons.addStretch()

        buttons.addWidget(
            self.cancel_button
        )

        main_layout.addLayout(
            buttons
        )

        # =================================================
        # PHASE SELECTOR
        # =================================================

        self.three_phase_selector.currentTextChanged.connect(
            self.on_phase_mode_changed
        )

        # Build initial phase rows.

        self.on_phase_mode_changed(
            self.three_phase_selector.currentText()
        )

        self.calculate_polarity()
        self.calculate_burden()

    # =====================================================
    # FIELD HELPERS
    # =====================================================

    def add_field(
        self,
        layout,
        field_id,
        label,
        default="",
        unit=""
    ):

        widget = QLineEdit()

        widget.setText(
            str(
                default
                if default is not None
                else ""
            )
        )

        self.fields[
            field_id
        ] = widget

        # -------------------------------------------------
        # QFormLayout
        # -------------------------------------------------

        if isinstance(
            layout,
            QFormLayout
        ):

            if unit:

                layout.addRow(
                    f"{label} ({unit})",
                    widget
                )

            else:

                layout.addRow(
                    label,
                    widget
                )

            return

        # -------------------------------------------------
        # QVBoxLayout / Other Layout
        # -------------------------------------------------

        row_layout = QHBoxLayout()

        label_widget = QLabel(
            f"{label}"
            + (
                f" ({unit})"
                if unit
                else ""
            )
        )

        label_widget.setMinimumWidth(
            220
        )

        row_layout.addWidget(
            label_widget
        )

        row_layout.addWidget(
            widget
        )

        layout.addLayout(
            row_layout
        )


    def add_readonly(
        self,
        layout,
        field_id,
        label,
        unit=""
    ):

        widget = QLineEdit()

        widget.setReadOnly(
            True
        )

        self.fields[
            field_id
        ] = widget

        # -------------------------------------------------
        # QFormLayout
        # -------------------------------------------------

        if isinstance(
            layout,
            QFormLayout
        ):

            if unit:

                layout.addRow(
                    f"{label} ({unit})",
                    widget
                )

            else:

                layout.addRow(
                    label,
                    widget
                )

            return

        # -------------------------------------------------
        # QVBoxLayout / Other Layout
        # -------------------------------------------------

        row_layout = QHBoxLayout()

        label_widget = QLabel(
            f"{label}"
            + (
                f" ({unit})"
                if unit
                else ""
            )
        )

        label_widget.setMinimumWidth(
            220
        )

        row_layout.addWidget(
            label_widget
        )

        row_layout.addWidget(
            widget
        )

        layout.addLayout(
            row_layout
        )


    def add_combo(
        self,
        layout,
        field_id,
        label,
        options
    ):

        widget = QComboBox()

        widget.addItems(
            options
        )

        self.fields[
            field_id
        ] = widget

        # -------------------------------------------------
        # QFormLayout
        # -------------------------------------------------

        if isinstance(
            layout,
            QFormLayout
        ):

            layout.addRow(
                label,
                widget
            )

            return

        # -------------------------------------------------
        # QVBoxLayout / Other Layout
        # -------------------------------------------------

        row_layout = QHBoxLayout()

        label_widget = QLabel(
            label
        )

        label_widget.setMinimumWidth(
            220
        )

        row_layout.addWidget(
            label_widget
        )

        row_layout.addWidget(
            widget
        )

        layout.addLayout(
            row_layout
        )

    # =====================================================
    # CT RATIO
    # =====================================================

    def _get_float(
        self,
        value
    ):

        try:

            return float(
                str(
                    value
                ).strip()
            )

        except (
            ValueError,
            TypeError
        ):

            return None

    def get_ct_primary(
        self
    ):

        value = self._get_float(
            self.fields[
                "ct_primary"
            ].text()
        )

        return value or 0.0

    def get_ct_secondary(
        self
    ):

        value = self._get_float(
            self.fields[
                "ct_secondary"
            ].text()
        )

        return value or 0.0

    def update_ct_information(
        self
    ):

        primary = (
            self.get_ct_primary()
        )

        secondary = (
            self.get_ct_secondary()
        )

        if (
            primary > 0
            and secondary > 0
        ):

            self.fields[
                "ct_ratio"
            ].setText(
                f"{primary:g}/{secondary:g}"
            )

            self.fields[
                "nominal_current"
            ].setText(
                f"{secondary:g}"
            )

        else:

            self.fields[
                "ct_ratio"
            ].clear()

            self.fields[
                "nominal_current"
            ].clear()

    # =====================================================
    # PHASE MODE
    # =====================================================

    def on_phase_mode_changed(
        self,
        text
    ):

        is_three_phase = (
            str(text).strip().lower()
            == "yes"
        )

        phases = (
            ["R", "Y", "B"]
            if is_three_phase
            else
            ["R"]
        )

        self.phase_table.setRowCount(
            0
        )

        self.phase_rows = {}

        for phase in phases:

            row = (
                self.phase_table.rowCount()
            )

            self.phase_table.insertRow(
                row
            )

            phase_item = (
                QTableWidgetItem(
                    phase
                )
            )

            phase_item.setFlags(
                phase_item.flags()
                &
                ~Qt.ItemFlag.ItemIsEditable
            )

            self.phase_table.setItem(
                row,
                0,
                phase_item
            )

            primary = QLineEdit()
            primary.setMinimumHeight(48)
            primary.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            secondary = QLineEdit()
            secondary.setMinimumHeight(48)
            secondary.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            ratio = QLineEdit()
            ratio.setMinimumHeight(48)
            ratio.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            ratio.setReadOnly(
                True
            )

            error = QLineEdit()
            error.setMinimumHeight(48)

            error.setReadOnly(
                True
            )

            error.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            result = QLineEdit()
            result.setMinimumHeight(48)

            result.setReadOnly(
                True
            )

            result.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.phase_table.setCellWidget(
                row,
                1,
                primary
            )

            self.phase_table.setCellWidget(
                row,
                2,
                secondary
            )

            self.phase_table.setCellWidget(
                row,
                3,
                ratio
            )

            self.phase_table.setCellWidget(
                row,
                4,
                error
            )

            self.phase_table.setCellWidget(
                row,
                5,
                result
            )

            self.phase_rows[
                phase
            ] = {

                "primary":
                    primary,

                "secondary":
                    secondary,

                "ratio":
                    ratio,

                "error":
                    error,

                "result":
                    result,
            }

            primary.textChanged.connect(
                lambda _, p=phase:
                self.calculate_phase_ratio(p)
            )

            secondary.textChanged.connect(
                lambda _, p=phase:
                self.calculate_phase_ratio(p)
            )

        self.update_ct_information()

    # =====================================================
    # PHASE CALCULATION
    # =====================================================

    def calculate_phase_ratio(
        self,
        phase
    ):

        row = self.phase_rows.get(
            phase
        )

        if row is None:
            return

        primary = self._get_float(
            row[
                "primary"
            ].text()
        )

        secondary = self._get_float(
            row[
                "secondary"
            ].text()
        )

        if (
            primary is None
            or secondary is None
            or secondary == 0
        ):

            row[
                "ratio"
            ].clear()

            row[
                "error"
            ].clear()

            row[
                "result"
            ].clear()

            self.update_overall_result()

            return

        measured_ratio = (
            primary /
            secondary
        )

        row[
            "ratio"
        ].setText(
            f"{measured_ratio:.4f}"
        )

        configured_primary = (
            self.get_ct_primary()
        )

        configured_secondary = (
            self.get_ct_secondary()
        )

        if (
            configured_primary <= 0
            or configured_secondary <= 0
        ):

            row[
                "error"
            ].clear()

            row[
                "result"
            ].clear()

            self.update_overall_result()

            return

        expected_ratio = (
            configured_primary /
            configured_secondary
        )

        error = (
            (
                measured_ratio
                -
                expected_ratio
            )
            /
            expected_ratio
        ) * 100.0

        row[
            "error"
        ].setText(
            f"{error:.2f}"
        )

        tolerance = self._get_float(
            self.fields[
                "tolerance_percent"
            ].text()
        )

        if tolerance is None:
            tolerance = 5.0

        row["result"].setText(
            "PASS"
            if abs(error) <= tolerance
            else "FAIL"
        )

        self.update_overall_result()

    # =====================================================
    # POLARITY
    # =====================================================

    def calculate_polarity(
        self
    ):

        expected = (
            self.fields[
                "expected_polarity"
            ].currentText()
        )

        observed = (
            self.fields[
                "observed_polarity"
            ].currentText()
        )

        result = (
            "PASS"
            if expected == observed
            else
            "FAIL"
        )

        self.fields[
            "polarity_result"
        ].setText(
            result
        )

        self.update_overall_result()

    # =====================================================
    # BURDEN
    # =====================================================

    def calculate_burden(
        self
    ):

        measured = self._get_float(
            self.fields[
                "measured_burden"
            ].text()
        )

        rated_text = (
            self.fields[
                "burden"
            ].text()
        )

        rated = self._get_float(
            str(
                rated_text
            ).lower()
            .replace(
                "va",
                ""
            )
            .strip()
        )

        if (
            measured is None
            or rated is None
            or rated == 0
        ):

            self.fields[
                "burden_error"
            ].clear()

            self.update_overall_result()

            return

        error = (
            (
                measured
                -
                rated
            )
            /
            rated
        ) * 100.0

        self.fields[
            "burden_error"
        ].setText(
            f"{error:.2f}"
        )

        self.update_overall_result()

    # =====================================================
    # OVERALL RESULT
    # =====================================================

    def update_overall_result(
        self
    ):

        failures = []

        # -------------------------------------------------
        # POLARITY
        # -------------------------------------------------

        polarity = (
            self.fields[
                "polarity_result"
            ].text()
        )

        if polarity == "FAIL":

            failures.append(
                "Polarity"
            )

        # -------------------------------------------------
        # RATIO
        # -------------------------------------------------

        tolerance = self._get_float(
            self.fields[
                "tolerance_percent"
            ].text()
        )

        if tolerance is None:

            tolerance = 5.0

        for phase, row in (
            self.phase_rows.items()
        ):

            error = self._get_float(
                row[
                    "error"
                ].text()
            )

            if error is None:

                continue

            if abs(error) > tolerance:

                failures.append(
                    f"Ratio {phase}"
                )

        # -------------------------------------------------
        # BURDEN
        # -------------------------------------------------

        burden_error = self._get_float(
            self.fields[
                "burden_error"
            ].text()
        )

        if (
            burden_error is not None
            and
            abs(
                burden_error
            ) > tolerance
        ):

            failures.append(
                "Burden"
            )

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        self.fields[
            "result"
        ].setText(
            "FAIL"
            if failures
            else
            "PASS"
        )

    # =====================================================
    # GET PHASE DATA
    # =====================================================

    def get_phase_data(
        self
    ):

        result = []

        for phase, row in (
            self.phase_rows.items()
        ):

            result.append(
                {

                    "phase":
                        phase,

                    "primary_current":
                        row[
                            "primary"
                        ].text().strip(),

                    "secondary_current":
                        row[
                            "secondary"
                        ].text().strip(),

                    "measured_ratio":
                        row[
                            "ratio"
                        ].text().strip(),

                    "ratio_error":
                        row[
                            "error"
                        ].text().strip(),
                }
            )

        return result

    # =====================================================
    # GET FIELD VALUES
    # =====================================================

    def get_field_values(
        self
    ):

        values = {}

        for field_id, widget in (
            self.fields.items()
        ):

            if isinstance(
                widget,
                QLineEdit
            ):

                values[
                    field_id
                ] = (
                    widget
                    .text()
                    .strip()
                )

            elif isinstance(
                widget,
                QComboBox
            ):

                values[
                    field_id
                ] = (
                    widget
                    .currentText()
                )

        values[
            "is_three_phase"
        ] = (
            self.three_phase_selector
            .currentText()
            == "Yes"
        )

        values[
            "phase_tests"
        ] = (
            self.get_phase_data()
        )

        # Keep single-phase compatibility.

        if len(
            values[
                "phase_tests"
            ]
        ) == 1:

            phase = values[
                "phase_tests"
            ][0]

            values[
                "primary_current"
            ] = phase[
                "primary_current"
            ]

            values[
                "secondary_current"
            ] = phase[
                "secondary_current"
            ]

            values[
                "measured_ratio"
            ] = phase[
                "measured_ratio"
            ]

            values[
                "ratio_error"
            ] = phase[
                "ratio_error"
            ]

        values[
            "ct_name"
        ] = getattr(
            self.component,
            "name",
            ""
        )

        return values

    # =====================================================
    # SAVE / UPDATE
    # =====================================================

    def save_test(
        self
    ):

        if self.test_service is None:

            QMessageBox.warning(
                self,
                "Save Failed",
                "Test service is not available."
            )

            return

        self.update_ct_information()

        self.update_overall_result()

        values = (
            self.get_field_values()
        )

        result = values.get(
            "result",
            "NOT TESTED"
        )

        remarks = values.get(
            "remarks",
            ""
        )

        try:

            # ---------------------------------------------
            # UPDATE EXISTING
            # ---------------------------------------------

            if self.test_id:

                self.test_service.update_component_test(
                    test_id=self.test_id,
                    measurements=values,
                    result=result,
                    remarks=remarks
                )

                QMessageBox.information(
                    self,
                    "Test Updated",
                    (
                        "CT test updated successfully.\n\n"
                        f"Test ID: {self.test_id}"
                    )
                )

                self.accept()

                return

            # ---------------------------------------------
            # NEW TEST
            # ---------------------------------------------

            test_id = (
                self.test_service
                .save_component_test(
                    project_id=(
                        self.project_id
                    ),

                    panel_id=(
                        self.panel_id
                    ),

                    component_id=(
                        self.component.component_id
                    ),

                    test_type="CT",

                    measurements=values,

                    result=result,

                    remarks=remarks
                )
            )

            QMessageBox.information(
                self,
                "Test Saved",
                (
                    "CT test saved successfully.\n\n"
                    f"Test ID: {test_id}"
                )
            )

            self.accept()

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error)
            )

    # =====================================================
    # POPULATE EXISTING TEST
    # =====================================================

    def populate_existing_test(
        self
    ):

        values = (
            self.existing_test.get(
                "measurements",
                {}
            )
            or {}
        )

        # -------------------------------------------------
        # STANDARD FIELDS
        # -------------------------------------------------

        for field_id, widget in (
            self.fields.items()
        ):

            if field_id not in values:

                continue

            value = values.get(
                field_id
            )

            if isinstance(
                widget,
                QLineEdit
            ):

                widget.setText(
                    ""
                    if value is None
                    else str(value)
                )

            elif isinstance(
                widget,
                QComboBox
            ):

                index = widget.findText(
                    str(value)
                )

                if index >= 0:

                    widget.setCurrentIndex(
                        index
                    )

        # -------------------------------------------------
        # THREE PHASE
        # -------------------------------------------------

        is_three_phase = (
            values.get(
                "is_three_phase",
                False
            )
        )

        self.three_phase_selector.setCurrentText(
            "Yes"
            if is_three_phase
            else
            "No"
        )

        # on_phase_mode_changed() rebuilds rows.

        phase_tests = (
            values.get(
                "phase_tests",
                []
            )
            or []
        )

        # Legacy test.

        if not phase_tests:

            if (
                values.get(
                    "primary_current"
                )
                or
                values.get(
                    "secondary_current"
                )
            ):

                phase_tests = [
                    {

                        "phase":
                            "R",

                        "primary_current":
                            values.get(
                                "primary_current",
                                ""
                            ),

                        "secondary_current":
                            values.get(
                                "secondary_current",
                                ""
                            ),
                    }
                ]

        for phase_data in phase_tests:

            phase = str(
                phase_data.get(
                    "phase",
                    "R"
                )
            )

            row = self.phase_rows.get(
                phase
            )

            if row is None:

                continue

            row[
                "primary"
            ].setText(
                str(
                    phase_data.get(
                        "primary_current",
                        ""
                    )
                )
            )

            row[
                "secondary"
            ].setText(
                str(
                    phase_data.get(
                        "secondary_current",
                        ""
                    )
                )
            )

        self.calculate_polarity()

        self.calculate_burden()

        for phase in (
            self.phase_rows
        ):

            self.calculate_phase_ratio(
                phase
            )

        self.update_overall_result()

    # =====================================================
    # CLEAR
    # =====================================================

    def clear_fields(
        self
    ):

        for field_id, widget in (
            self.fields.items()
        ):

            if field_id in (
                "ct_primary",
                "ct_secondary",
                "core",
                "ct_class",
                "burden",
                "manufacturer",
                "model",
                "serial_number",
                "remarks",
                "ir_primary_earth",
                "ir_secondary_earth",
                "ir_primary_secondary",
                "ir_test_voltage",
                "ir_test_duration",
                "resistance_phase_a",
                "resistance_phase_b",
                "resistance_phase_c",
                "knee_point_voltage",
                "knee_point_current",
                "excitation_test_voltage",
                "excitation_test_current",
                "burden_test_current",
                "measured_burden",
            ):

                if isinstance(
                    widget,
                    QLineEdit
                ):

                    widget.clear()

        self.fields[
            "tolerance_percent"
        ].setText(
            "5"
        )

        self.three_phase_selector.setCurrentText(
            "No"
        )

        self.calculate_polarity()
        self.calculate_burden()
        self.update_ct_information()

    # =====================================================
    # CLOSE
    # =====================================================

    def reject(
        self
    ):

        super().reject()