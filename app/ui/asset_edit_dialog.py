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
        ).strip().upper()

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

        self.build_ui()

        # IMPORTANT:
        # Populate the fields AFTER the widgets exist.
        self.populate_existing_values()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        layout = QVBoxLayout(
            self
        )

        node_type = str(
            getattr(
                self.node,
                "node_type",
                "ASSET",
            )
        ).strip().upper()

        label = (
            node_type
            .replace("_", " ")
            .title()
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

        # =================================================
        # FORM
        # =================================================

        form = QFormLayout()

        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        self.name_edit = QLineEdit()

        form.addRow(
            "Name:",
            self.name_edit
        )

        # -------------------------------------------------
        # ASSET TAG
        # -------------------------------------------------

        self.asset_tag_edit = QLineEdit()

        form.addRow(
            "Asset Tag:",
            self.asset_tag_edit
        )

        # -------------------------------------------------
        # MANUFACTURER
        # -------------------------------------------------

        self.manufacturer_edit = QLineEdit()

        form.addRow(
            "Manufacturer:",
            self.manufacturer_edit
        )

        # -------------------------------------------------
        # MODEL
        # -------------------------------------------------

        self.model_edit = QLineEdit()

        form.addRow(
            "Model:",
            self.model_edit
        )

        # -------------------------------------------------
        # SERIAL NUMBER
        # -------------------------------------------------

        self.serial_number_edit = QLineEdit()

        form.addRow(
            "Serial Number:",
            self.serial_number_edit
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

    # =====================================================
    # POPULATE EXISTING VALUES
    # =====================================================

    def populate_existing_values(self):

        node = self.node

        asset = self.global_asset

        # -------------------------------------------------
        # NAME
        #
        # Project node is the authoritative displayed name.
        # -------------------------------------------------

        name = getattr(
            node,
            "name",
            ""
        )

        if not name:

            name = asset.get(
                "name",
                ""
            )

        # -------------------------------------------------
        # ASSET TAG
        # -------------------------------------------------

        asset_tag = asset.get(
            "asset_tag",
            ""
        )

        if not asset_tag:

            asset_tag = getattr(
                node,
                "asset_tag",
                ""
            )

        if not asset_tag:

            asset_tag = name

        # -------------------------------------------------
        # MANUFACTURER
        # -------------------------------------------------

        manufacturer = asset.get(
            "manufacturer",
            ""
        )

        if not manufacturer:

            manufacturer = getattr(
                node,
                "manufacturer",
                ""
            )

        # -------------------------------------------------
        # MODEL
        # -------------------------------------------------

        model = asset.get(
            "model",
            ""
        )

        if not model:

            model = getattr(
                node,
                "model",
                ""
            )

        # -------------------------------------------------
        # SERIAL NUMBER
        # -------------------------------------------------

        serial_number = asset.get(
            "serial_number",
            ""
        )

        if not serial_number:

            serial_number = getattr(
                node,
                "serial_number",
                ""
            )

        # -------------------------------------------------
        # PUT VALUES INTO UI
        # -------------------------------------------------

        self.name_edit.setText(
            str(name or "")
        )

        self.asset_tag_edit.setText(
            str(asset_tag or "")
        )

        self.manufacturer_edit.setText(
            str(manufacturer or "")
        )

        self.model_edit.setText(
            str(model or "")
        )

        self.serial_number_edit.setText(
            str(serial_number or "")
        )

        # Put cursor in the name field.
        self.name_edit.setFocus()

        self.name_edit.selectAll()

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
                "Asset name cannot be empty."
            )

            self.name_edit.setFocus()

            return

        # Asset tag is retained internally for existing
        # assets. If it is blank, use the asset name.
        if not asset_tag:

            asset_tag = name

            self.asset_tag_edit.setText(
                asset_tag
            )

        super().accept()

    # =====================================================
    # GET VALUES
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