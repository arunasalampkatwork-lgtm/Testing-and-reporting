from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
)

from app.ui.panel_configuration_copy_dialog import (
    PanelConfigurationCopyDialog
)


class PanelConfigDialog(QDialog):

    def __init__(
        self,
        node,
        projects_dir=None,
        target_project_folder=None,
        parent=None
    ):

        super().__init__(parent)

        self.node = node

        self.projects_dir = projects_dir

        self.target_project_folder = (
            target_project_folder
        )

        self.copied_configuration = {}

        self.setWindowTitle(
            "Panel Configuration"
        )

        self.resize(
            500,
            500
        )

        layout = QVBoxLayout(
            self
        )

        form = QFormLayout()

        # =================================================
        # PANEL
        # =================================================

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

        # =================================================
        # EQUIPMENT
        # =================================================

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

        # =================================================
        # CT
        # =================================================

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

        # =================================================
        # NUMERICAL RELAYS
        # =================================================

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

        # =================================================
        # AUXILIARY RELAYS
        # =================================================

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

        # =================================================
        # METERS
        # =================================================

        self.meter_count = QSpinBox()

        self.meter_count.setRange(
            0,
            50
        )

        self.meter_count.setValue(
            self._get_int_value(
                node,
                "meter_count",
                0
            )
        )

        form.addRow(
            "Meters:",
            self.meter_count
        )

        layout.addLayout(
            form
        )

        # =================================================
        # COPY CONFIGURATION
        # =================================================

        self.copy_configuration_button = (
            QPushButton(
                "Copy Configuration from Existing Panel..."
            )
        )

        self.copy_configuration_button.clicked.connect(
            self.copy_from_existing_panel
        )

        layout.addWidget(
            self.copy_configuration_button
        )

        # =================================================
        # BUTTONS
        # =================================================

        buttons = QHBoxLayout()

        save_button = QPushButton(
            "Save"
        )

        cancel_button = QPushButton(
            "Cancel"
        )

        save_button.clicked.connect(
            self.accept
        )

        cancel_button.clicked.connect(
            self.reject
        )

        buttons.addStretch()

        buttons.addWidget(
            save_button
        )

        buttons.addWidget(
            cancel_button
        )

        layout.addLayout(
            buttons
        )

    # =====================================================
    # COPY FROM EXISTING PANEL
    # =====================================================

    def copy_from_existing_panel(
        self
    ):

        if self.projects_dir is None:

            return

        dialog = (
            PanelConfigurationCopyDialog(

                projects_dir=
                    self.projects_dir,

                target_project_folder=
                    self.target_project_folder,

                target_panel_id=
                    getattr(
                        self.node,
                        "node_id",
                        None
                    ),

                parent=self,
            )
        )

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):

            return

        configuration = (
            dialog.get_configuration()
        )

        self.copied_configuration = (
            configuration
        )

        # =================================================
        # APPLY PANEL CONFIGURATION
        # =================================================

        panel_config = (
            configuration.get(
                "panel_configuration",
                {}
            )
        )

        if "equipment_name" in panel_config:

            self.equipment_name.setText(
                str(
                    panel_config[
                        "equipment_name"
                    ]
                    or ""
                )
            )

        if "equipment_type" in panel_config:

            self.equipment_type.setText(
                str(
                    panel_config[
                        "equipment_type"
                    ]
                    or ""
                )
            )

        if "ct_count" in panel_config:

            self.ct_count.setValue(
                int(
                    panel_config[
                        "ct_count"
                    ]
                    or 0
                )
            )

        if "relay_count" in panel_config:

            self.relay_count.setValue(
                int(
                    panel_config[
                        "relay_count"
                    ]
                    or 0
                )
            )

        if "aux_count" in panel_config:

            self.aux_count.setValue(
                int(
                    panel_config[
                        "aux_count"
                    ]
                    or 0
                )
            )

        if "meter_count" in panel_config:

            self.meter_count.setValue(
                int(
                    panel_config[
                        "meter_count"
                    ]
                    or 0
                )
            )

    # =====================================================
    # GET CONFIGURATION
    # =====================================================

    def get_configuration(
        self
    ):

        configuration = {

            "panel_name":
                self.panel_name.text().strip(),

            "equipment_name":
                self.equipment_name.text().strip(),

            "equipment_type":
                self.equipment_type.text().strip(),

            "ct_count":
                self.ct_count.value(),

            "relay_count":
                self.relay_count.value(),

            "aux_count":
                self.aux_count.value(),

            "meter_count":
                self.meter_count.value(),
        }

        # =================================================
        # COPIED COMPONENT CONFIGURATION
        # =================================================

        if self.copied_configuration:

            configuration[
                "_copied_component_configuration"
            ] = (
                self.copied_configuration.get(
                    "component_configuration",
                    []
                )
            )

        return configuration

    # =====================================================
    # INTEGER HELPER
    # =====================================================

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