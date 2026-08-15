from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QPushButton,
    QComboBox,
    QGroupBox,
    QFormLayout,
)

from app.ui.testing_view import TestingView

from app.config.protection_functions import (
    get_protection_function,
    normalize_protection_code,
    PROTECTION_FUNCTIONS,
)


class RelayTestingDialog(QDialog):

    def __init__(
        self,
        project_id,
        panel_id,
        relay_id,
        component,
        available_cts=None,
        test_service=None,
        parent=None,
    ):

        super().__init__(parent)

        self.project_id = project_id
        self.panel_id = panel_id
        self.relay_id = relay_id

        # Numerical relay being tested
        self.component = component

        # CTs belonging to the same panel
        self.available_cts = list(
            available_cts or []
        )

        self.test_service = test_service

        self.testing_views = []

        # Currently selected CT
        self.selected_ct = None

        self.setWindowTitle(
            "Relay Protection Testing - "
            f"{getattr(component, 'name', 'Relay')}"
        )

        self.resize(
            1150,
            850
        )

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )

        # =================================================
        # HEADER
        # =================================================

        header = QLabel(
            "Relay: "
            f"{getattr(self.component, 'name', '')}"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )

        layout.addWidget(
            header
        )

        # =================================================
        # CT REFERENCE
        # =================================================

        ct_group = QGroupBox(
            "Current Reference for Protection Testing"
        )

        ct_layout = QFormLayout()

        # -------------------------------------------------
        # CT SELECTOR
        # -------------------------------------------------

        self.ct_selector = QComboBox()

        self.populate_ct_selector()

        ct_layout.addRow(
            "Select CT:",
            self.ct_selector
        )

        # -------------------------------------------------
        # CT RATIO
        # -------------------------------------------------

        self.ct_ratio_display = QLabel(
            "NOT CONFIGURED"
        )

        ct_layout.addRow(
            "CT Ratio:",
            self.ct_ratio_display
        )

        # -------------------------------------------------
        # NOMINAL CURRENT
        # -------------------------------------------------

        self.nominal_current_display = QLabel(
            "NOT CONFIGURED"
        )

        ct_layout.addRow(
            "Relay Nominal Current (In):",
            self.nominal_current_display
        )

        ct_group.setLayout(
            ct_layout
        )

        layout.addWidget(
            ct_group
        )

        # =================================================
        # TABS
        # =================================================

        self.tabs = QTabWidget()

        layout.addWidget(
            self.tabs
        )

        # =================================================
        # SELECT FIRST CT BEFORE CREATING TESTING VIEWS
        # =================================================

        if (
            self.available_cts
            and self.ct_selector.count() > 0
        ):

            self.ct_selector.setCurrentIndex(
                0
            )

            self.selected_ct = (
                self.ct_selector.currentData()
            )

        # =================================================
        # PROTECTION FUNCTIONS
        # =================================================

        configured_functions = (
            getattr(
                self.component,
                "protection_functions",
                []
            )
            or []
        )

        unique_functions = []

        seen = set()

        for protection in (
            configured_functions
        ):

            code = (
                normalize_protection_code(
                    protection
                )
            )

            if not code:
                continue

            if code not in PROTECTION_FUNCTIONS:
                continue

            if code in seen:
                continue

            seen.add(
                code
            )

            unique_functions.append(
                code
            )

        # =================================================
        # NO FUNCTIONS
        # =================================================

        if not unique_functions:

            empty_label = QLabel(
                "No protection functions have been "
                "configured for this relay."
            )

            empty_label.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            self.tabs.addTab(
                empty_label,
                "No Functions"
            )

        # =================================================
        # CREATE TESTING VIEWS
        # =================================================

        for code in unique_functions:

            function_config = (
                get_protection_function(
                    code
                )
            )

            if function_config is None:
                continue

            testing_view = (
                self.create_testing_view(
                    code
                )
            )

            self.testing_views.append(
                testing_view
            )

            function_name = (
                function_config.get(
                    "name",
                    code
                )
            )

            self.tabs.addTab(
                testing_view,
                f"{code} - {function_name}"
            )

        # =================================================
        # CT SELECTION SIGNAL
        # =================================================

        self.ct_selector.currentIndexChanged.connect(
            self.on_ct_changed
        )

        # =================================================
        # DISPLAY INITIAL CT
        # =================================================

        self.update_selected_ct()

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        buttons.addStretch()

        close_button = QPushButton(
            "Close"
        )

        close_button.clicked.connect(
            self.accept
        )

        buttons.addWidget(
            close_button
        )

        layout.addLayout(
            buttons
        )

    # =====================================================
    # POPULATE CT SELECTOR
    # =====================================================

    def populate_ct_selector(self):

        self.ct_selector.clear()

        if not self.available_cts:

            self.ct_selector.addItem(
                "No CTs configured for this panel",
                None
            )

            self.ct_selector.setEnabled(
                False
            )

            return

        self.ct_selector.setEnabled(
            True
        )

        for ct in self.available_cts:

            name = str(
                getattr(
                    ct,
                    "name",
                    "CT"
                )
            )

            ratio = (
                self.get_ct_ratio(
                    ct
                )
            )

            if ratio:

                text = (
                    f"{name} | {ratio}"
                )

            else:

                text = (
                    f"{name} | "
                    "Ratio not configured"
                )

            self.ct_selector.addItem(
                text,
                ct
            )

    # =====================================================
    # CREATE TESTING VIEW
    # =====================================================

    def create_testing_view(
        self,
        protection_code
    ):

        return TestingView(

            project_id=self.project_id,

            panel_id=self.panel_id,

            relay_id=self.relay_id,

            protection_function=(
                protection_code
            ),

            test_service=self.test_service,

            # Numerical relay
            component=self.component,

            # Selected CT
            ct_component=self.selected_ct,

            parent=self.tabs
        )

    # =====================================================
    # CT CHANGED
    # =====================================================

    def on_ct_changed(
        self,
        index
    ):

        self.update_selected_ct()

    # =====================================================
    # UPDATE SELECTED CT
    # =====================================================

    def update_selected_ct(self):

        selected = (
            self.ct_selector.currentData()
        )

        self.selected_ct = selected

        if selected is None:

            self.ct_ratio_display.setText(
                "NOT CONFIGURED"
            )

            self.nominal_current_display.setText(
                "NOT CONFIGURED"
            )

        else:

            ratio = (
                self.get_ct_ratio(
                    selected
                )
            )

            self.ct_ratio_display.setText(
                ratio
                or
                "NOT CONFIGURED"
            )

            nominal = (
                self.get_nominal_current(
                    selected
                )
            )

            if nominal > 0:

                self.nominal_current_display.setText(
                    f"{nominal:g} A"
                )

            else:

                self.nominal_current_display.setText(
                    "NOT CONFIGURED"
                )

        # -------------------------------------------------
        # Tell every protection tab about the new CT.
        # -------------------------------------------------

        for view in self.testing_views:

            try:

                view.set_ct_context(
                    selected
                )

            except AttributeError:

                pass

    # =====================================================
    # GET CT RATIO
    # =====================================================

    @staticmethod
    def get_ct_ratio(
        ct
    ):

        if ct is None:
            return ""

        try:

            primary = float(
                getattr(
                    ct,
                    "ct_primary",
                    0
                )
                or 0
            )

            secondary = float(
                getattr(
                    ct,
                    "ct_secondary",
                    0
                )
                or 0
            )

            if (
                primary > 0
                and secondary > 0
            ):

                return (
                    f"{primary:g}/"
                    f"{secondary:g}"
                )

        except (
            TypeError,
            ValueError
        ):

            pass

        return str(
            getattr(
                ct,
                "ct_ratio",
                ""
            )
            or ""
        ).strip()

    # =====================================================
    # GET NOMINAL CURRENT
    # =====================================================

    @staticmethod
    def get_nominal_current(
        ct
    ):

        if ct is None:
            return 0.0

        try:

            secondary = float(
                getattr(
                    ct,
                    "ct_secondary",
                    0
                )
                or 0
            )

            if secondary > 0:
                return secondary

        except (
            TypeError,
            ValueError
        ):

            pass

        # Backward compatibility
        # 1000/5 -> 5
        # 1000/1 -> 1

        ratio = str(
            getattr(
                ct,
                "ct_ratio",
                ""
            )
            or ""
        ).strip()

        if "/" in ratio:

            try:

                return float(
                    ratio.split(
                        "/",
                        1
                    )[1].strip()
                )

            except (
                TypeError,
                ValueError,
                IndexError
            ):

                pass

        return 0.0

    # =====================================================
    # CLOSE
    # =====================================================

    def closeEvent(
        self,
        event
    ):

        self.testing_views.clear()

        event.accept()