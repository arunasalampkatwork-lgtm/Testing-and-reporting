from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout
)


class PanelConfigDialog(QDialog):

    def __init__(
        self,
        node,
        parent=None
    ):

        super().__init__(parent)

        self.node = node

        self.setWindowTitle(
            "Panel Configuration"
        )

        self.resize(
            450,
            350
        )

        layout = QVBoxLayout(self)

        form = QFormLayout()

        # ---------------------------------------------
        # PANEL
        # ---------------------------------------------

        self.panel_name = QLineEdit()

        self.panel_name.setText(
            node.name
        )

        self.panel_name.setReadOnly(
            True
        )

        form.addRow(
            "Panel:",
            self.panel_name
        )

        # ---------------------------------------------
        # EQUIPMENT
        # ---------------------------------------------

        self.equipment_name = QLineEdit()

        form.addRow(
            "Feed Equipment:",
            self.equipment_name
        )

        # ---------------------------------------------
        # EQUIPMENT TYPE
        # ---------------------------------------------

        self.equipment_type = QLineEdit()

        form.addRow(
            "Equipment Type:",
            self.equipment_type
        )

        # ---------------------------------------------
        # CTS
        # ---------------------------------------------

        self.ct_count = QSpinBox()

        self.ct_count.setRange(
            0,
            20
        )

        form.addRow(
            "Number of CTs:",
            self.ct_count
        )

        # ---------------------------------------------
        # NUMERICAL RELAYS
        # ---------------------------------------------

        self.relay_count = QSpinBox()

        self.relay_count.setRange(
            0,
            20
        )

        form.addRow(
            "Numerical Relays:",
            self.relay_count
        )

        # ---------------------------------------------
        # AUXILIARY RELAYS
        # ---------------------------------------------

        self.aux_count = QSpinBox()

        self.aux_count.setRange(
            0,
            50
        )

        form.addRow(
            "Auxiliary Relays:",
            self.aux_count
        )

        layout.addLayout(
            form
        )

        # ---------------------------------------------
        # BUTTONS
        # ---------------------------------------------

        buttons = QHBoxLayout()

        save_button = QPushButton(
            "Save"
        )

        cancel_button = QPushButton(
            "Cancel"
        )

        buttons.addWidget(
            save_button
        )

        buttons.addWidget(
            cancel_button
        )

        layout.addLayout(
            buttons
        )

        save_button.clicked.connect(
            self.accept
        )

        cancel_button.clicked.connect(
            self.reject
        )

    # =================================================
    # GET CONFIGURATION
    # =================================================

    def get_configuration(self):

        return {

            "panel_name":
                self.panel_name.text(),

            "equipment_name":
                self.equipment_name.text().strip(),

            "equipment_type":
                self.equipment_type.text().strip(),

            "ct_count":
                self.ct_count.value(),

            "relay_count":
                self.relay_count.value(),

            "aux_count":
                self.aux_count.value()
        }