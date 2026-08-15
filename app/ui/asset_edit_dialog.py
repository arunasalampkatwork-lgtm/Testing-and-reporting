from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
    QMessageBox,
    QLabel,
)


class AssetEditDialog(QDialog):

    def __init__(
        self,
        node,
        global_asset=None,
        parent=None,
    ):

        super().__init__(parent)

        self.node = node

        self.global_asset = (
            global_asset
            if isinstance(global_asset, dict)
            else {}
        )

        node_type = str(
            getattr(
                node,
                "node_type",
                "ASSET",
            )
        ).upper()

        label = (
            node_type
            .replace("_", " ")
            .title()
        )

        self.setWindowTitle(
            f"Edit {label}"
        )

        self.setModal(True)

        self.resize(
            500,
            350,
        )

        # =================================================
        # LAYOUT
        # =================================================

        layout = QVBoxLayout(
            self
        )

        title = QLabel(
            f"Edit {label}"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
                padding: 5px;
            }
            """
        )

        layout.addWidget(
            title
        )

        form = QFormLayout()

        # =================================================
        # NAME
        # =================================================

        self.name_edit = QLineEdit()

        self.name_edit.setText(
            str(
                getattr(
                    node,
                    "name",
                    "",
                )
            )
        )

        form.addRow(
            "Name:",
            self.name_edit,
        )

        # =================================================
        # ASSET TAG
        # =================================================

        asset_tag = (
            self.global_asset.get(
                "asset_tag",
                "",
            )
        )

        if not asset_tag:

            asset_tag = getattr(
                node,
                "name",
                "",
            )

        self.asset_tag_edit = QLineEdit()

        self.asset_tag_edit.setText(
            str(
                asset_tag
            )
        )

        form.addRow(
            "Asset Tag:",
            self.asset_tag_edit,
        )

        # =================================================
        # MANUFACTURER
        # =================================================

        self.manufacturer_edit = QLineEdit()

        self.manufacturer_edit.setText(
            str(
                self.global_asset.get(
                    "manufacturer",
                    "",
                )
            )
        )

        form.addRow(
            "Manufacturer:",
            self.manufacturer_edit,
        )

        # =================================================
        # MODEL
        # =================================================

        self.model_edit = QLineEdit()

        self.model_edit.setText(
            str(
                self.global_asset.get(
                    "model",
                    "",
                )
            )
        )

        form.addRow(
            "Model:",
            self.model_edit,
        )

        # =================================================
        # SERIAL NUMBER
        # =================================================

        self.serial_number_edit = QLineEdit()

        self.serial_number_edit.setText(
            str(
                self.global_asset.get(
                    "serial_number",
                    "",
                )
            )
        )

        form.addRow(
            "Serial Number:",
            self.serial_number_edit,
        )

        layout.addLayout(
            form
        )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
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

        self.name_edit.setFocus()

    # =====================================================
    # VALIDATION
    # =====================================================

    def accept(self):

        name = (
            self.name_edit
            .text()
            .strip()
        )

        asset_tag = (
            self.asset_tag_edit
            .text()
            .strip()
        )

        if not name:

            QMessageBox.warning(
                self,
                "Missing Name",
                "Asset name cannot be empty.",
            )

            self.name_edit.setFocus()

            return

        if not asset_tag:

            # For compatibility with your new-panel
            # behaviour, use the asset name as the tag.
            asset_tag = name

            self.asset_tag_edit.setText(
                asset_tag
            )

        super().accept()

    # =====================================================
    # VALUES
    # =====================================================

    def get_values(self):

        return {
            "name": (
                self.name_edit
                .text()
                .strip()
            ),

            "asset_tag": (
                self.asset_tag_edit
                .text()
                .strip()
            ),

            "manufacturer": (
                self.manufacturer_edit
                .text()
                .strip()
            ),

            "model": (
                self.model_edit
                .text()
                .strip()
            ),

            "serial_number": (
                self.serial_number_edit
                .text()
                .strip()
            ),
        }