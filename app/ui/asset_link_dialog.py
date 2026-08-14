from PySide6.QtCore import Qt
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
        assets,
        asset_type="PANEL",
        parent=None
    ):

        super().__init__(parent)

        self.assets = assets or []
        self.asset_type = str(
            asset_type or "PANEL"
        ).strip().upper()
        self.selected_asset = None

        label = self.asset_type.replace(
            "_", " "
        ).title()

        self.setWindowTitle(
            f"Link Existing {label}"
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

        label = self.asset_type.replace(
            "_", " "
        ).title()

        title = QLabel(
            f"Select an Existing {label}"
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

        self.asset_list = QListWidget()

        layout.addWidget(
            self.asset_list
        )

        # -----------------------------------------------------
        # Populate panels
        # -----------------------------------------------------

        for asset in self.assets:

            name = str(asset.get("name", ""))
            asset_tag = str(asset.get("asset_tag", ""))
            serial_number = str(asset.get("serial_number", ""))
            manufacturer = str(asset.get("manufacturer", ""))
            model = str(asset.get("model", ""))

            text = (
                f"{name} | "
                f"{asset_tag} | "
                f"{manufacturer} {model} | "
                f"{serial_number}"
            )

            item = QListWidgetItem(text)
            item.setData(
                Qt.ItemDataRole.UserRole,
                asset
            )
            self.asset_list.addItem(item)

        # -----------------------------------------------------
        # Buttons
        # -----------------------------------------------------

        buttons = QHBoxLayout()

        cancel_button = QPushButton(
            "Cancel"
        )

        label = self.asset_type.replace(
            "_", " "
        ).title()

        link_button = QPushButton(
            f"Link {label}"
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

        item = self.asset_list.currentItem()

        if item is None:

            QMessageBox.warning(
                self,
                "No Asset Selected",
                "Please select an asset.",
            )
            return

        self.selected_asset = item.data(
            Qt.ItemDataRole.UserRole
        )

        self.accept()

    def get_selected_asset(self):

        return self.selected_asset

    def get_selected_panel(self):

        return self.selected_asset
