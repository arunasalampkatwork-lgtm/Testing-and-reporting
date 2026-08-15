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

        # =============================================
        # PANEL
        # =============================================

        self.panel_name = QLineEdit()

        self.panel_name.setText(
            str(
                getattr(
                    node,
                    "name",
                    ""
                )
            )
        )

        self.panel_name.setReadOnly(
            True
        )

        form.addRow(
            "Panel:",
            self.panel_name
        )

        # =============================================
        # EQUIPMENT / FEED EQUIPMENT
        # =============================================

        self.equipment_name = QLineEdit()

        self.equipment_name.setText(
            str(
                getattr(
                    node,
                    "equipment_name",
                    ""
                ) or ""
            )
        )

        form.addRow(
            "Feed Equipment:",
            self.equipment_name
        )

        # =============================================
        # EQUIPMENT TYPE
        # =============================================

        self.equipment_type = QLineEdit()

        self.equipment_type.setText(
            str(
                getattr(
                    node,
                    "equipment_type",
                    ""
                ) or ""
            )
        )

        form.addRow(
            "Equipment Type:",
            self.equipment_type
        )

        # =============================================
        # CT COUNT
        # =============================================

        self.ct_count = QSpinBox()

        self.ct_count.setRange(
            0,
            20
        )

        self.ct_count.setValue(
            self._get_int_value(
                node,
                "ct_count",
                0
            )
        )

        form.addRow(
            "Number of CTs:",
            self.ct_count
        )

        # =============================================
        # NUMERICAL RELAY COUNT
        # =============================================

        self.relay_count = QSpinBox()

        self.relay_count.setRange(
            0,
            20
        )

        self.relay_count.setValue(
            self._get_int_value(
                node,
                "relay_count",
                0
            )
        )

        form.addRow(
            "Numerical Relays:",
            self.relay_count
        )

        # =============================================
        # AUXILIARY RELAY COUNT
        # =============================================

        self.aux_count = QSpinBox()

        self.aux_count.setRange(
            0,
            50
        )

        self.aux_count.setValue(
            self._get_int_value(
                node,
                "aux_count",
                0
            )
        )

        form.addRow(
            "Auxiliary Relays:",
            self.aux_count
        )

        layout.addLayout(
            form
        )

        # =============================================
        # BUTTONS
        # =============================================

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
    # SAFE INTEGER VALUE
    # =================================================

    @staticmethod
    def _get_int_value(
        node,
        attribute,
        default=0
    ):

        value = getattr(
            node,
            attribute,
            default
        )

        try:

            return int(
                value or default
            )

        except (
            TypeError,
            ValueError
        ):

            return default

    # =================================================
    # GET CONFIGURATION
    # =================================================

    def get_configuration(self):

        return {

            "panel_name":
                self.panel_name
                .text()
                .strip(),

            "equipment_name":
                self.equipment_name
                .text()
                .strip(),

            "equipment_type":
                self.equipment_type
                .text()
                .strip(),

            "ct_count":
                self.ct_count.value(),

            "relay_count":
                self.relay_count.value(),

            "aux_count":
                self.aux_count.value()
        }