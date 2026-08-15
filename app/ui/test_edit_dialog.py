from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QComboBox,
    QLineEdit,
)

from PySide6.QtCore import QSignalBlocker

from app.ui.testing_view import TestingView


class TestEditDialog(QDialog):

    def __init__(
        self,
        test_service,
        test_id,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.test_service = (
            test_service
        )

        self.test_id = (
            test_id
        )

        self.record = None

        self.testing_view = None

        self.setWindowTitle(
            f"Edit Protection Test - {test_id}"
        )

        self.resize(
            1000,
            800
        )

        self.build_ui()

        self.load_test()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(
        self
    ):

        layout = QVBoxLayout(
            self
        )

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        self.header = QLabel(
            "Edit Protection Test"
        )

        self.header.setStyleSheet(
            """
            QLabel {
                font-size: 20px;
                font-weight: bold;
                padding: 8px;
            }
            """
        )

        layout.addWidget(
            self.header
        )

        # -------------------------------------------------
        # TEST INFO
        # -------------------------------------------------

        self.info_label = QLabel()

        self.info_label.setStyleSheet(
            """
            QLabel {
                padding: 5px;
            }
            """
        )

        layout.addWidget(
            self.info_label
        )

        # -------------------------------------------------
        # TESTING VIEW PLACEHOLDER
        # -------------------------------------------------

        self.testing_container_layout = (
            QVBoxLayout()
        )

        layout.addLayout(
            self.testing_container_layout
        )

        # -------------------------------------------------
        # BUTTONS
        # -------------------------------------------------

        buttons = QHBoxLayout()

        buttons.addStretch()

        self.save_button = QPushButton(
            "Save Changes"
        )

        self.cancel_button = QPushButton(
            "Cancel"
        )

        self.save_button.clicked.connect(
            self.save_changes
        )

        self.cancel_button.clicked.connect(
            self.reject
        )

        buttons.addWidget(
            self.save_button
        )

        buttons.addWidget(
            self.cancel_button
        )

        layout.addLayout(
            buttons
        )

    # =====================================================
    # LOAD TEST
    # =====================================================

    def load_test(
        self
    ):

        try:

            self.record = (
                self.test_service
                .get_test(
                    self.test_id
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Database Error",
                str(error)
            )

            self.reject()

            return

        if self.record is None:

            QMessageBox.warning(
                self,
                "Test Not Found",
                (
                    f"Protection test "
                    f"'{self.test_id}' was not found."
                )
            )

            self.reject()

            return

        self.create_testing_view()

    # =====================================================
    # CREATE TESTING VIEW
    # =====================================================

    def create_testing_view(
        self
    ):

        protection_code = (
            self.record.get(
                "protection_code",
                ""
            )
        )

        # -------------------------------------------------
        # CREATE CT SNAPSHOT
        #
        # We intentionally create a small CT object from
        # the stored test snapshot.
        #
        # We DO NOT read today's CT configuration.
        #
        # This preserves historical accuracy.
        # -------------------------------------------------

        settings = (
            self.record.get(
                "settings",
                {}
            )
            or {}
        )

        ct_snapshot = (
            self._create_ct_snapshot(
                settings
            )
        )

        # -------------------------------------------------
        # CREATE TESTING VIEW
        # -------------------------------------------------

        self.testing_view = TestingView(

            project_id=(
                self.record.get(
                    "project_id"
                )
            ),

            panel_id=(
                self.record.get(
                    "panel_id"
                )
            ),

            relay_id=(
                self.record.get(
                    "relay_id"
                )
            ),

            protection_function=(
                protection_code
            ),

            test_service=(
                self.test_service
            ),

            component=None,

            ct_component=(
                ct_snapshot
            ),

            parent=self
        )

        self.testing_container_layout.addWidget(
            self.testing_view
        )

        # -------------------------------------------------
        # INFO
        # -------------------------------------------------

        self.info_label.setText(
            (
                f"Test ID: {self.test_id}    |    "
                f"Protection: {protection_code}    |    "
                f"CT: "
                f"{settings.get('ct_ratio', 'N/A')}"
            )
        )

        # -------------------------------------------------
        # LOAD VALUES
        # -------------------------------------------------

        self.populate_testing_view()

    # =====================================================
    # CT SNAPSHOT
    # =====================================================

    @staticmethod
    def _create_ct_snapshot(
        settings
    ):

        class CTSnapshot:
            pass

        ct = CTSnapshot()

        ct.component_id = (
            settings.get(
                "ct_id",
                ""
            )
        )

        ct.name = (
            settings.get(
                "ct_name",
                ""
            )
        )

        ct.ct_primary = (
            settings.get(
                "ct_primary_a",
                0
            )
        )

        ct.ct_secondary = (
            settings.get(
                "ct_secondary_a",
                settings.get(
                    "nominal_current_a",
                    0
                )
            )
        )

        ct.ct_ratio = (
            settings.get(
                "ct_ratio",
                ""
            )
        )

        return ct

    # =====================================================
    # POPULATE TESTING VIEW
    # =====================================================

    def populate_testing_view(
        self
    ):

        measurements = (
            self.record.get(
                "measurements",
                {}
            )
            or {}
        )

        # -------------------------------------------------
        # Block signals while populating.
        #
        # We don't want half-filled fields to produce
        # half-baked calculations.
        # -------------------------------------------------

        blockers = []

        for widget in (
            self.testing_view.fields.values()
        ):

            blockers.append(
                QSignalBlocker(
                    widget
                )
            )

        blockers.append(
            QSignalBlocker(
                self.testing_view.tolerance_widget
            )
        )

        blockers.append(
            QSignalBlocker(
                self.testing_view.remarks_widget
            )
        )

        blockers.append(
            QSignalBlocker(
                self.testing_view.result_widget
            )
        )

        # -------------------------------------------------
        # NORMAL FIELDS
        # -------------------------------------------------

        for field_id, widget in (
            self.testing_view.fields.items()
        ):

            if field_id not in measurements:
                continue

            value = measurements.get(
                field_id
            )

            self._set_widget_value(
                widget,
                value
            )

        # -------------------------------------------------
        # TOLERANCE
        # -------------------------------------------------

        tolerance = (
            measurements.get(
                "tolerance_percent",
                5
            )
        )

        self.testing_view.tolerance_widget.setText(
            str(
                tolerance
            )
        )

        # -------------------------------------------------
        # REMARKS
        # -------------------------------------------------

        self.testing_view.remarks_widget.setText(
            str(
                measurements.get(
                    "remarks",
                    self.record.get(
                        "remarks",
                        ""
                    )
                )
                or ""
            )
        )

        # -------------------------------------------------
        # IMPORTANT
        #
        # Calculated fields are intentionally NOT loaded
        # from the database.
        #
        # We recalculate them from the editable inputs.
        # -------------------------------------------------

        self.testing_view.result_widget.clear()

        # -------------------------------------------------
        # RELEASE SIGNAL BLOCKERS
        # -------------------------------------------------

        del blockers

        # -------------------------------------------------
        # RECALCULATE
        # -------------------------------------------------

        self.recalculate()

    # =====================================================
    # SET WIDGET VALUE
    # =====================================================

    @staticmethod
    def _set_widget_value(
        widget,
        value
    ):

        if value is None:
            value = ""

        if isinstance(
            widget,
            QLineEdit
        ):

            widget.setText(
                str(value)
            )

            return

        if isinstance(
            widget,
            QComboBox
        ):

            text = str(
                value
            )

            index = (
                widget.findText(
                    text
                )
            )

            if index >= 0:

                widget.setCurrentIndex(
                    index
                )

            return

    # =====================================================
    # RECALCULATE
    # =====================================================

    def recalculate(
        self
    ):

        view = (
            self.testing_view
        )

        try:

            if view.test_type == "idmt":

                view.calculate_idmt()

            elif view.test_type == (
                "current_pickup_time"
            ):

                view.calculate_current_pickup()

            elif view.test_type == (
                "voltage_threshold"
            ):

                view.calculate_voltage()

            elif view.test_type == (
                "frequency_threshold"
            ):

                view.calculate_frequency()

            elif view.test_type == "rocof":

                view.calculate_rocof()

            elif view.test_type == (
                "directional_current"
            ):

                view.calculate_directional()

            elif view.test_type == "functional":

                view.calculate_functional()

            elif view.test_type == "differential":

                view.calculate_differential()

        except Exception:

            # The normal TestingView calculation methods
            # already handle incomplete input.
            pass

    # =====================================================
    # SAVE
    # =====================================================

    def save_changes(
        self
    ):

        view = (
            self.testing_view
        )

        values = (
            view.get_field_values()
        )

        # -------------------------------------------------
        # Validate
        # -------------------------------------------------

        if not view.validate_fields(
            values
        ):

            return

        result = (
            values.get(
                "result",
                ""
            )
            or
            "NOT TESTED"
        )

        # -------------------------------------------------
        # Preserve CT snapshot
        # -------------------------------------------------

        old_settings = (
            self.record.get(
                "settings",
                {}
            )
            or {}
        )

        settings = {

            "nominal_current_a":
                old_settings.get(
                    "nominal_current_a",
                    view.nominal_current
                ),

            "nominal_current_unit":
                "A",

            "input_current_unit":
                (
                    "xIn"
                    if view.is_current_based_test()
                    else ""
                ),

            "ct_id":
                old_settings.get(
                    "ct_id",
                    ""
                ),

            "ct_name":
                old_settings.get(
                    "ct_name",
                    ""
                ),

            "ct_primary_a":
                old_settings.get(
                    "ct_primary_a",
                    0
                ),

            "ct_secondary_a":
                old_settings.get(
                    "ct_secondary_a",
                    view.nominal_current
                ),

            "ct_ratio":
                old_settings.get(
                    "ct_ratio",
                    ""
                ),
        }

        # -------------------------------------------------
        # SAVE
        # -------------------------------------------------

        try:

            self.test_service.update_protection_test(

                test_id=(
                    self.test_id
                ),

                settings=(
                    settings
                ),

                measurements=(
                    values
                ),

                result=(
                    result
                ),

                remarks=(
                    values.get(
                        "remarks",
                        ""
                    )
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error)
            )

            return

        QMessageBox.information(
            self,
            "Test Updated",
            (
                f"Test {self.test_id} "
                "has been updated successfully."
            )
        )

        self.accept()