from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QPushButton,
)
from PySide6.QtCore import Qt

from app.ui.testing_view import TestingView

from app.config.protection_functions import (
    get_protection_function,
    normalize_protection_code,
    PROTECTION_FUNCTIONS,
)


class RelayTestingDialog(QDialog):
    """
    Main relay-testing popup.

    One tab is created for each protection function
    configured in component.protection_functions.

    Example:

        component.protection_functions = [
            "50",
            "51",
            "50N"
        ]

    produces:

        [50 - Instantaneous Overcurrent]
        [51 - Time Overcurrent]
        [50N - Instantaneous Earth Fault]
    """

    def __init__(
        self,
        project_id,
        panel_id,
        relay_id,
        component,
        test_service=None,
        parent=None,
    ):

        super().__init__(parent)

        self.project_id = project_id
        self.panel_id = panel_id
        self.relay_id = relay_id
        self.component = component
        self.test_service = test_service

        self.testing_views = []

        # -------------------------------------------------
        # WINDOW
        # -------------------------------------------------

        self.setWindowTitle(
            f"Relay Protection Testing - "
            f"{component.name}"
        )

        self.resize(
            1100,
            800
        )

        # -------------------------------------------------
        # BUILD
        # -------------------------------------------------

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header = QLabel(
            f"Relay: {self.component.name}"
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

        # -------------------------------------------------
        # TABS
        # -------------------------------------------------

        self.tabs = QTabWidget()

        layout.addWidget(
            self.tabs
        )

        # -------------------------------------------------
        # GET CONFIGURED FUNCTIONS
        # -------------------------------------------------

        configured_functions = (
            self.component.protection_functions
            or []
        )

        # -------------------------------------------------
        # NORMALIZE + REMOVE DUPLICATES
        # -------------------------------------------------

        unique_functions = []

        seen = set()

        for protection in configured_functions:

            code = normalize_protection_code(
                protection
            )

            if not code:
                continue

            # Ignore invalid protection codes
            if code not in PROTECTION_FUNCTIONS:
                continue

            # Remove duplicates
            if code in seen:
                continue

            seen.add(code)

            unique_functions.append(
                code
            )

        # -------------------------------------------------
        # NO CONFIGURED FUNCTIONS
        # -------------------------------------------------

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

        # -------------------------------------------------
        # CREATE TESTING TABS
        # -------------------------------------------------

        for code in unique_functions:

            function_config = (
                get_protection_function(
                    code
                )
            )

            if function_config is None:
                continue

            testing_view = TestingView(
                project_id=self.project_id,
                panel_id=self.panel_id,
                relay_id=self.relay_id,
                protection_function=code,
                test_service=self.test_service,
                parent=self.tabs,
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

            tab_name = (
                f"{code} - {function_name}"
            )

            self.tabs.addTab(
                testing_view,
                tab_name
            )

        # -------------------------------------------------
        # BOTTOM BUTTONS
        # -------------------------------------------------

        button_layout = QHBoxLayout()

        button_layout.addStretch()

        close_button = QPushButton(
            "Close"
        )

        close_button.clicked.connect(
            self.close
        )

        button_layout.addWidget(
            close_button
        )

        layout.addLayout(
            button_layout
        )

    # =====================================================
    # CLOSE EVENT
    # =====================================================

    def closeEvent(self, event):

        # Clear references to child testing views.
        #
        # This prevents us from accidentally retaining
        # old TestingView instances after the dialog closes.

        self.testing_views.clear()

        event.accept()