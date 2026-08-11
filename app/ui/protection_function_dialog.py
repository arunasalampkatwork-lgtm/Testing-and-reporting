from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QDialogButtonBox,
)

from app.config.protection_functions import (
    PROTECTION_FUNCTIONS,
    normalize_protection_code,
)


class ProtectionFunctionDialog(QDialog):
    """
    Dialog used to configure which protection functions
    are actually available in a numerical relay.

    Only canonical protection codes are stored in:

        component.protection_functions

    Example:

        ["50", "51", "50N"]
    """

    def __init__(self, component, parent=None):

        super().__init__(parent)

        self.component = component

        self.setWindowTitle(
            f"Protection Functions - {component.name}"
        )

        self.resize(500, 550)

        self.build_ui()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # DESCRIPTION
        # -------------------------------------------------

        description = QLabel(
            "Select the protection functions available "
            "in this relay:"
        )

        layout.addWidget(description)

        # -------------------------------------------------
        # FUNCTION LIST
        # -------------------------------------------------

        self.function_list = QListWidget()

        layout.addWidget(
            self.function_list
        )

        # -------------------------------------------------
        # EXISTING CONFIGURATION
        # -------------------------------------------------

        existing_functions = set()

        configured = (
            self.component.protection_functions
            or []
        )

        for function in configured:

            code = normalize_protection_code(
                function
            )

            if code in PROTECTION_FUNCTIONS:

                existing_functions.add(code)

        # -------------------------------------------------
        # POPULATE LIST
        # -------------------------------------------------

        for function_id, function_config in (
            PROTECTION_FUNCTIONS.items()
        ):

            name = function_config.get(
                "name",
                function_id
            )

            item = QListWidgetItem(
                f"{function_id} - {name}"
            )

            # Store canonical protection code
            item.setData(
                Qt.ItemDataRole.UserRole,
                function_id
            )

            if function_id in existing_functions:

                item.setCheckState(
                    Qt.CheckState.Checked
                )

            else:

                item.setCheckState(
                    Qt.CheckState.Unchecked
                )

            self.function_list.addItem(
                item
            )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            |
            QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(
            self.accept
        )

        buttons.rejected.connect(
            self.reject
        )

        layout.addWidget(
            buttons
        )

    # =====================================================
    # GET SELECTED FUNCTIONS
    # =====================================================

    def get_selected_functions(self):

        functions = []

        for index in range(
            self.function_list.count()
        ):

            item = self.function_list.item(
                index
            )

            if (
                item.checkState()
                != Qt.CheckState.Checked
            ):
                continue

            function_id = item.data(
                Qt.ItemDataRole.UserRole
            )

            function_id = normalize_protection_code(
                function_id
            )

            if (
                function_id
                and function_id in PROTECTION_FUNCTIONS
                and function_id not in functions
            ):

                functions.append(
                    function_id
                )

        return functions

    # =====================================================
    # ACCEPT
    # =====================================================

    def accept(self):

        selected_functions = (
            self.get_selected_functions()
        )

        # Store ONLY canonical protection codes
        self.component.protection_functions = (
            selected_functions
        )

        super().accept()