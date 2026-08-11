from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QMessageBox,
)


class AssetLinkDialog(QDialog):

    def __init__(
        self,
        panels,
        parent=None
    ):

        super().__init__(parent)

        self.panels = panels

        self.selected_panel = None

        self.setWindowTitle(
            "Link Existing Panel"
        )

        self.resize(
            600,
            450
        )

        self.build_ui()

    # =========================================================
    # BUILD UI
    # =========================================================

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            "Select an Existing Panel"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            title
        )

        self.panel_list = QListWidget()

        layout.addWidget(
            self.panel_list
        )

        # -----------------------------------------------------
        # Populate panels
        # -----------------------------------------------------

        for panel in self.panels:

            item = QListWidgetItem(

                f"{panel.name} | "
                f"{getattr(panel, 'equipment_name', '')}"
            )

            item.setData(
                256,
                panel
            )

            self.panel_list.addItem(
                item
            )

        # -----------------------------------------------------
        # Buttons
        # -----------------------------------------------------

        buttons = QHBoxLayout()

        cancel_button = QPushButton(
            "Cancel"
        )

        link_button = QPushButton(
            "Link Panel"
        )

        cancel_button.clicked.connect(
            self.reject
        )

        link_button.clicked.connect(
            self.accept_selection
        )

        buttons.addStretch()

        buttons.addWidget(
            cancel_button
        )

        buttons.addWidget(
            link_button
        )

        layout.addLayout(
            buttons
        )

    # =========================================================
    # ACCEPT
    # =========================================================

    def accept_selection(self):

        item = (
            self.panel_list.currentItem()
        )

        if item is None:

            QMessageBox.warning(
                self,
                "No Panel Selected",
                "Please select a panel."
            )

            return

        self.selected_panel = item.data(
            256
        )

        self.accept()

    # =========================================================
    # GET PANEL
    # =========================================================

    def get_selected_panel(self):

        return self.selected_panel