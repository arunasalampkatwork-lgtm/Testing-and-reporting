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
    Current Transformer Testing Dialog.

    Configuration is supplied by TestComponent:

        ct_primary
        ct_secondary
        ct_ratio
        ct_class
        burden
        core
        manufacturer
        model
        serial_number

    Test measurements are entered separately.

    Ratio test data is stored as:

        phase_tests = [
            {
                "phase": "R",
                "primary_current": "...",
                "secondary_current": "...",
                "measured_ratio": "...",
                "ratio_error": "...",
                "result": "PASS"
            }
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

        self.project_id = project_id
        self.panel_id = panel_id
        self.component = component
        self.test_service = test_service
        self.test_id = test_id
        self.existing_test = existing_test

        self.fields = {}
        self.phase_rows = {}

        self.setWindowTitle(
            "CT Testing"
            if not test_id
            else "Edit CT Test"
        )

        self.setModal(False)

        self.resize(
            1050,
            850
        )

        # =================================================
        # HISTORICAL TEST SNAPSHOT
        # =================================================

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

            self.component = SimpleNamespace(

                component_id=(
                    existing_test.get(
                        "component_id",
                        ""
                    )
                ),

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

        # -------------------------------------------------
        # SAFETY FALLBACK
        # -------------------------------------------------

        if self.component is None:

            self.component = SimpleNamespace(

                component_id="",

                name="CT",

                ct_primary=0,

                ct_secondary=0,

                ct_ratio="",

                core="",

                ct_class="",

                burden="",

                manufacturer="",

                model="",

                serial_number="",
            )

        self.build_ui()

        if self.existing_test:

            self.populate_existing_test()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            14,
            14,
            14,
            14
        )

        main_layout.setSpacing(
            10
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

        container_layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        container_layout.setSpacing(
            12
        )

        # =================================================
        # CT IDENTIFICATION
        # =================================================

        identification = QGroupBox(
            "CT Identification"
        )

        identification_layout = QFormLayout(
            identification
        )

        identification_layout.setSpacing(
            9
        )

        self.add_readonly(
            identification_layout,
            "ct_name",
            "CT",
            getattr(
                self.component,
                "name",
                ""
            )
        )

        self.add_readonly(
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

        self.add_readonly(
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
            "",
            "A"
        )

        self.add_readonly(
            identification_layout,
            "ct_ratio",
            "CT Ratio",
            ""
        )

        self.add_readonly(
            identification_layout,
            "core",
            "Core",
            getattr(
                self.component,
                "core",
                ""
            )
        )

        self.add_readonly(
            identification_layout,
            "ct_class",
            "CT Class",
            getattr(
                self.component,
                "ct_class",
                ""
            )
        )

        self.add_readonly(
            identification_layout,
            "burden",
            "Rated Burden",
            getattr(
                self.component,
                "burden",
                ""
            )
        )

        self.add_readonly(
            identification_layout,
            "manufacturer",
            "Manufacturer",
            getattr(
                self.component,
                "manufacturer",
                ""
            )
        )

        self.add_readonly(
            identification_layout,
            "model",
            "Model",
            getattr(
                self.component,
                "model",
                ""
            )
        )

        self.add_readonly(
            identification_layout,
            "serial_number",
            "Serial Number",
            getattr(
                self.component,
                "serial_number",
                ""
            )
        )

        container_layout.addWidget(
            identification
        )

        self.update_ct_information()

        # =================================================
        # PHASE CONFIGURATION
        # =================================================

        phase_group = QGroupBox(
            "CT Phase Configuration"
        )

        phase_layout = QFormLayout(
            phase_group
        )

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

        container_layout.addWidget(
            phase_group
        )

        # =================================================
        # RATIO TEST
        # =================================================

        self.ratio_group = QGroupBox(
            "CT Ratio Test"
        )

        ratio_layout = QVBoxLayout(
            self.ratio_group
        )

        ratio_help = QLabel(
            "Enter the injected primary current and the "
            "corresponding recorded secondary current. "
            "Measured ratio and ratio error are calculated "
            "against the configured CT ratio."
        )

        ratio_help.setWordWrap(
            True
        )

        ratio_help.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                color: #aaaaaa;
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

        header_view = (
            self.phase_table
            .horizontalHeader()
        )

        header_view.setMinimumHeight(
            52
        )

        header_view.setDefaultAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        header_view.setStretchLastSection(
            False
        )

        header_view.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Fixed
        )

        self.phase_table.setColumnWidth(
            0,
            80
        )

        for column in (
            1,
            2,
            3,
            4
        ):

            header_view.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Stretch
            )

        header_view.setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.Fixed
        )

        self.phase_table.setColumnWidth(
            5,
            100
        )

        self.phase_table.verticalHeader().setDefaultSectionSize(
            60
        )

        self.phase_table.verticalHeader().setVisible(
            False
        )

        self.phase_table.setMinimumHeight(
            150
        )

        self.phase_table.setMaximumHeight(
            520
        )

        ratio_layout.addWidget(
            self.phase_table
        )

        ratio_buttons = QHBoxLayout()

        self.add_ratio_row_button = QPushButton(
            "+ Add Test Row"
        )

        self.remove_ratio_row_button = QPushButton(
            "− Remove Selected Row"
        )

        self.add_ratio_row_button.clicked.connect(
            self.add_ratio_test_row
        )

        self.remove_ratio_row_button.clicked.connect(
            self.remove_ratio_test_row
        )

        ratio_buttons.addWidget(
            self.add_ratio_row_button
        )

        ratio_buttons.addWidget(
            self.remove_ratio_row_button
        )

        ratio_buttons.addStretch()

        ratio_layout.addLayout(
            ratio_buttons
        )

        container_layout.addWidget(
            self.ratio_group
        )

        # =================================================
        # POLARITY
        # =================================================

        polarity_group = QGroupBox(
            "Polarity Test"
        )

        polarity_layout = QFormLayout(
            polarity_group
        )

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

        ir_layout = QFormLayout(
            ir_group
        )

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

        container_layout.addWidget(
            ir_group
        )

        # =================================================
        # WINDING RESISTANCE
        # =================================================

        winding_group = QGroupBox(
            "Winding Resistance"
        )

        winding_layout = QFormLayout(
            winding_group
        )

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

        container_layout.addWidget(
            winding_group
        )

        # =================================================
        # KNEE POINT
        # =================================================

        knee_group = QGroupBox(
            "Knee Point / Excitation"
        )

        knee_layout = QFormLayout(
            knee_group
        )

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

        container_layout.addWidget(
            knee_group
        )

        # =================================================
        # BURDEN
        # =================================================

        burden_group = QGroupBox(
            "Burden Test"
        )

        burden_layout = QFormLayout(
            burden_group
        )

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

        container_layout.addStretch()

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
            "Clear Test Data"
        )

        self.save_button = QPushButton(
            "Update Test"
            if self.test_id
            else "Save Test"
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
        # PHASE SIGNAL
        # =================================================

        self.three_phase_selector.currentTextChanged.connect(
            self.on_phase_mode_changed
        )

        self.on_phase_mode_changed(
            self.three_phase_selector.currentText()
        )

        self.calculate_polarity()
        self.calculate_burden()

        self.setStyleSheet(
            """
            QDialog {
                background-color: #242424;
            }

            QGroupBox {
                font-weight: 600;
                border: 1px solid #414141;
                border-radius: 7px;
                margin-top: 10px;
                padding: 12px;
                background-color: #292929;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0px 5px;
                color: #dddddd;
            }

            QLineEdit,
            QComboBox {
                min-height: 32px;
                padding: 4px 8px;
                border: 1px solid #444444;
                border-radius: 5px;
                background-color: #202020;
                color: #eeeeee;
            }

            QLineEdit:read-only {
                background-color: #303030;
                color: #bbbbbb;
            }

            QPushButton {
                min-height: 35px;
                padding: 6px 12px;
                border-radius: 6px;
                border: 1px solid #444444;
                background-color: #333333;
                color: #eeeeee;
            }

            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #666666;
            }

            QTableWidget {
                background-color: #292929;
                alternate-background-color: #303030;
                border: 1px solid #444444;
                gridline-color: #505050;
            }

            QTableWidget::item {
                padding: 7px;
            }

            QHeaderView::section {
                font-weight: bold;
                padding: 9px;
            }
            """
        )

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
            ""
            if default is None
            else str(default)
        )

        self.fields[
            field_id
        ] = widget

        if isinstance(
            layout,
            QFormLayout
        ):

            display_label = (
                f"{label} ({unit})"
                if unit
                else label
            )

            layout.addRow(
                display_label,
                widget
            )

            return

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
        default="",
        unit=""
    ):

        widget = QLineEdit()

        widget.setReadOnly(
            True
        )

        if default is not None:

            widget.setText(
                str(default)
            )

        self.fields[
            field_id
        ] = widget

        if isinstance(
            layout,
            QFormLayout
        ):

            display_label = (
                f"{label} ({unit})"
                if unit
                else label
            )

            layout.addRow(
                display_label,
                widget
            )

            return

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

        layout.addRow(
            label,
            widget
        )

    # =====================================================
    # NUMBER
    # =====================================================

    @staticmethod
    def _get_float(
        value
    ):

        try:

            text = str(
                value
            ).strip()

            if not text:

                return None

            return float(
                text
            )

        except (
            ValueError,
            TypeError
        ):

            return None

    # =====================================================
    # CT CONFIGURATION
    # =====================================================

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

            # Preserve a legacy ratio if primary/secondary
            # are unavailable.
            legacy_ratio = str(
                getattr(
                    self.component,
                    "ct_ratio",
                    ""
                )
                or ""
            ).strip()

            self.fields[
                "ct_ratio"
            ].setText(
                legacy_ratio
            )

            self.fields[
                "nominal_current"
            ].clear()

    # =====================================================
    # PHASES
    # =====================================================

    def _current_phases(
        self
    ):

        if (
            self.three_phase_selector
            .currentText()
            .strip()
            .lower()
            == "yes"
        ):

            return [
                "R",
                "Y",
                "B"
            ]

        return [
            "R"
        ]

    # =====================================================
    # CREATE RATIO ROW
    # =====================================================

    def _create_ratio_row(
        self,
        phase,
        primary="",
        secondary=""
    ):

        row = (
            self.phase_table
            .rowCount()
        )

        self.phase_table.insertRow(
            row
        )

        phase_item = QTableWidgetItem(
            str(phase)
        )

        phase_item.setFlags(
            phase_item.flags()
            &
            ~Qt.ItemFlag.ItemIsEditable
        )

        phase_item.setTextAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.phase_table.setItem(
            row,
            0,
            phase_item
        )

        primary_widget = QLineEdit()

        primary_widget.setMinimumHeight(
            48
        )

        primary_widget.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        primary_widget.setText(
            ""
            if primary is None
            else str(primary)
        )

        secondary_widget = QLineEdit()

        secondary_widget.setMinimumHeight(
            48
        )

        secondary_widget.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        secondary_widget.setText(
            ""
            if secondary is None
            else str(secondary)
        )

        ratio_widget = QLineEdit()

        ratio_widget.setMinimumHeight(
            48
        )

        ratio_widget.setReadOnly(
            True
        )

        ratio_widget.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        error_widget = QLineEdit()

        error_widget.setMinimumHeight(
            48
        )

        error_widget.setReadOnly(
            True
        )

        error_widget.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        result_widget = QLineEdit()

        result_widget.setMinimumHeight(
            48
        )

        result_widget.setReadOnly(
            True
        )

        result_widget.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.phase_table.setCellWidget(
            row,
            1,
            primary_widget
        )

        self.phase_table.setCellWidget(
            row,
            2,
            secondary_widget
        )

        self.phase_table.setCellWidget(
            row,
            3,
            ratio_widget
        )

        self.phase_table.setCellWidget(
            row,
            4,
            error_widget
        )

        self.phase_table.setCellWidget(
            row,
            5,
            result_widget
        )

        row_data = {

            "phase":
                str(phase),

            "primary":
                primary_widget,

            "secondary":
                secondary_widget,

            "ratio":
                ratio_widget,

            "error":
                error_widget,

            "result":
                result_widget,
        }

        self.phase_rows.setdefault(
            str(phase),
            []
        ).append(
            row_data
        )

        primary_widget.textChanged.connect(
            lambda _,
            r=row_data:
            self.calculate_phase_ratio_row(r)
        )

        secondary_widget.textChanged.connect(
            lambda _,
            r=row_data:
            self.calculate_phase_ratio_row(r)
        )

        self.calculate_phase_ratio_row(
            row_data
        )

        return row_data

    # =====================================================
    # SNAPSHOT
    # =====================================================

    def _snapshot_phase_rows(
        self
    ):

        snapshot = []

        for phase, rows in (
            self.phase_rows.items()
        ):

            for row_data in rows:

                snapshot.append({

                    "phase":
                        phase,

                    "primary_current":
                        row_data[
                            "primary"
                        ].text().strip(),

                    "secondary_current":
                        row_data[
                            "secondary"
                        ].text().strip(),
                })

        return snapshot

    # =====================================================
    # PHASE MODE
    # =====================================================

    def on_phase_mode_changed(
        self,
        text
    ):

        previous_rows = (
            self._snapshot_phase_rows()
        )

        is_three_phase = (
            str(text)
            .strip()
            .lower()
            == "yes"
        )

        phases = (
            [
                "R",
                "Y",
                "B"
            ]
            if is_three_phase
            else [
                "R"
            ]
        )

        self.phase_table.setRowCount(
            0
        )

        self.phase_rows = {}

        for phase in phases:

            matching = [

                item

                for item in previous_rows

                if item[
                    "phase"
                ] == phase
            ]

            if matching:

                for item in matching:

                    self._create_ratio_row(
                        phase,
                        item[
                            "primary_current"
                        ],
                        item[
                            "secondary_current"
                        ]
                    )

            else:

                self._create_ratio_row(
                    phase
                )

        self.update_ct_information()

        self.update_overall_result()

    # =====================================================
    # ADD ROW
    # =====================================================

    def add_ratio_test_row(
        self
    ):

        phases = self._current_phases()

        if not phases:
            return

        selected_row = (
            self.phase_table
            .currentRow()
        )

        phase = phases[0]

        if selected_row >= 0:

            item = (
                self.phase_table.item(
                    selected_row,
                    0
                )
            )

            if item is not None:

                selected_phase = (
                    item.text().strip()
                )

                if selected_phase in phases:

                    phase = selected_phase

        row_data = (
            self._create_ratio_row(
                phase
            )
        )

        new_row = (
            self.phase_table
            .rowCount()
            - 1
        )

        self.phase_table.selectRow(
            new_row
        )

        row_data[
            "primary"
        ].setFocus()

        self.update_overall_result()

    # =====================================================
    # REMOVE ROW
    # =====================================================

    def remove_ratio_test_row(
        self
    ):

        row = (
            self.phase_table
            .currentRow()
        )

        if row < 0:

            QMessageBox.information(
                self,
                "Remove Test Row",
                "Select a CT ratio test row first."
            )

            return

        phase_item = (
            self.phase_table.item(
                row,
                0
            )
        )

        if phase_item is None:
            return

        phase = (
            phase_item
            .text()
            .strip()
        )

        phase_rows = (
            self.phase_rows.get(
                phase,
                []
            )
        )

        if len(phase_rows) <= 1:

            QMessageBox.information(
                self,
                "Cannot Remove Row",
                (
                    f"At least one ratio test row "
                    f"must remain for phase {phase}."
                )
            )

            return

        row_data = None

        for candidate in phase_rows:

            widget = candidate[
                "primary"
            ]

            index = (
                self.phase_table
                .indexAt(
                    widget.pos()
                )
            )

            if index.row() == row:

                row_data = candidate

                break

        if row_data is not None:

            phase_rows.remove(
                row_data
            )

        self.phase_table.removeRow(
            row
        )

        self.update_overall_result()

    # =====================================================
    # RATIO CALCULATION
    # =====================================================

    def calculate_phase_ratio_row(
        self,
        row
    ):

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

        row[
            "result"
        ].setText(
            "PASS"
            if abs(error) <= tolerance
            else "FAIL"
        )

        self.update_overall_result()

    def calculate_phase_ratio(
        self,
        phase
    ):

        for row in (
            self.phase_rows.get(
                phase,
                []
            )
        ):

            self.calculate_phase_ratio_row(
                row
            )

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
            else "FAIL"
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
            )
            .lower()
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

        for phase, rows in (
            self.phase_rows.items()
        ):

            for test_number, row in enumerate(
                rows,
                start=1
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
                        f"Ratio {phase} "
                        f"Test {test_number}"
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
            else "PASS"
        )

    # =====================================================
    # PHASE DATA
    # =====================================================

    def get_phase_data(
        self
    ):

        result = []

        for phase, rows in (
            self.phase_rows.items()
        ):

            for test_number, row in enumerate(
                rows,
                start=1
            ):

                result.append({

                    "phase":
                        phase,

                    "test_no":
                        test_number,

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

                    "result":
                        row[
                            "result"
                        ].text().strip(),
                })

        return result

    # =====================================================
    # FIELD VALUES
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

        # -------------------------------------------------
        # LEGACY SINGLE PHASE
        # -------------------------------------------------

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
    # SAVE
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

            # -------------------------------------------------
            # UPDATE
            # -------------------------------------------------

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

            # -------------------------------------------------
            # NEW
            # -------------------------------------------------

            component_id = getattr(
                self.component,
                "component_id",
                ""
            )

            if not component_id:

                QMessageBox.warning(
                    self,
                    "Component Error",
                    "Unable to determine CT component ID."
                )

                return

            test_id = (
                self.test_service
                .save_component_test(

                    project_id=self.project_id,

                    panel_id=self.panel_id,

                    component_id=component_id,

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

                index = (
                    widget.findText(
                        str(value)
                    )
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
            else "No"
        )

        # -------------------------------------------------
        # PHASE DATA
        # -------------------------------------------------

        phase_tests = (
            values.get(
                "phase_tests",
                []
            )
            or []
        )

        # Legacy format.

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

        valid_phases = set(
            self._current_phases()
        )

        self.phase_table.setRowCount(
            0
        )

        self.phase_rows = {}

        grouped = {}

        for phase_data in phase_tests:

            phase = str(
                phase_data.get(
                    "phase",
                    "R"
                )
            ).strip()

            if phase not in valid_phases:
                continue

            grouped.setdefault(
                phase,
                []
            ).append(
                phase_data
            )

        for phase in self._current_phases():

            saved_rows = grouped.get(
                phase,
                []
            )

            if not saved_rows:

                self._create_ratio_row(
                    phase
                )

                continue

            for phase_data in saved_rows:

                self._create_ratio_row(

                    phase,

                    phase_data.get(
                        "primary_current",
                        ""
                    ),

                    phase_data.get(
                        "secondary_current",
                        ""
                    )
                )

        self.update_ct_information()

        self.calculate_polarity()
        self.calculate_burden()

        for phase in self.phase_rows:

            self.calculate_phase_ratio(
                phase
            )

        self.update_overall_result()

    # =====================================================
    # CLEAR TEST DATA
    # =====================================================

    def clear_fields(
        self
    ):

        # -------------------------------------------------
        # IMPORTANT
        #
        # Configuration fields are NOT cleared:
        #
        # ct_primary
        # ct_secondary
        # ct_ratio
        # core
        # ct_class
        # burden
        # manufacturer
        # model
        # serial_number
        #
        # "Clear" means clear the test measurements.
        # -------------------------------------------------

        fields_to_clear = (

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

            "remarks",
        )

        for field_id in fields_to_clear:

            widget = self.fields.get(
                field_id
            )

            if isinstance(
                widget,
                QLineEdit
            ):

                widget.clear()

        # -------------------------------------------------
        # TOLERANCE
        # -------------------------------------------------

        self.fields[
            "tolerance_percent"
        ].setText(
            "5"
        )

        # -------------------------------------------------
        # POLARITY
        # -------------------------------------------------

        self.fields[
            "expected_polarity"
        ].setCurrentText(
            "CORRECT"
        )

        self.fields[
            "observed_polarity"
        ].setCurrentText(
            "CORRECT"
        )

        # -------------------------------------------------
        # PHASE MODE
        # -------------------------------------------------

        self.three_phase_selector.setCurrentText(
            "No"
        )

        # -------------------------------------------------
        # RATIO TEST ROW
        # -------------------------------------------------

        self.phase_table.setRowCount(
            0
        )

        self.phase_rows = {}

        for phase in (
            self._current_phases()
        ):

            self._create_ratio_row(
                phase
            )

        # -------------------------------------------------
        # RECALCULATE
        # -------------------------------------------------

        self.update_ct_information()

        self.calculate_polarity()

        self.calculate_burden()

        self.update_overall_result()

    # =====================================================
    # CLOSE
    # =====================================================

    def reject(
        self
    ):

        super().reject()