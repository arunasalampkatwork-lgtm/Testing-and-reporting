from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
    QPushButton,
)


class DashboardView(QWidget):

    def __init__(
        self,
        global_asset_service,
        parent=None
    ):

        super().__init__(parent)

        self.global_asset_service = (
            global_asset_service
        )

        self.asset_cards = {}

        self.build_ui()

        self.refresh()

    # =====================================================
    # BUILD UI
    # =====================================================

    def build_ui(self):

        main_layout = QVBoxLayout(
            self
        )

        main_layout.setContentsMargins(
            20,
            20,
            20,
            20
        )

        main_layout.setSpacing(
            15
        )

        # =================================================
        # HEADER
        # =================================================

        title = QLabel(
            "Protection Testing Suite Dashboard"
        )

        title.setStyleSheet(
            """
            QLabel {
                font-size: 26px;
                font-weight: bold;
            }
            """
        )

        main_layout.addWidget(
            title
        )

        subtitle = QLabel(
            "Universal asset overview across all projects"
        )

        subtitle.setStyleSheet(
            """
            QLabel {
                color: #999999;
                font-size: 13px;
            }
            """
        )

        main_layout.addWidget(
            subtitle
        )

        # =================================================
        # REFRESH
        # =================================================

        control_layout = QHBoxLayout()

        refresh_button = QPushButton(
            "Refresh"
        )

        refresh_button.clicked.connect(
            self.refresh
        )

        control_layout.addWidget(
            refresh_button
        )

        control_layout.addStretch()

        main_layout.addLayout(
            control_layout
        )

        # =================================================
        # METRIC GRID
        # =================================================

        self.asset_grid = QGridLayout()

        self.asset_grid.setHorizontalSpacing(
            12
        )

        self.asset_grid.setVerticalSpacing(
            12
        )

        main_layout.addLayout(
            self.asset_grid
        )

        # =================================================
        # CARDS
        # =================================================

        cards = [

            (
                "projects",
                "PROJECTS"
            ),

            (
                "substations",
                "SUBSTATIONS"
            ),

            (
                "switchboards",
                "SWITCHBOARDS"
            ),

            (
                "panels",
                "PANELS"
            ),

            (
                "cts",
                "CURRENT TRANSFORMERS"
            ),

            (
                "relays",
                "NUMERICAL RELAYS"
            ),

            (
                "aux",
                "AUXILIARY RELAYS"
            ),

            (
                "meters",
                "METERS"
            ),

        ]

        for index, (
            key,
            title_text
        ) in enumerate(cards):

            # IMPORTANT:
            # _create_card returns TWO objects.
            card, value_label = (
                self._create_card(
                    title_text
                )
            )

            row = index // 4

            column = index % 4

            # IMPORTANT:
            # Add ONLY the QWidget.
            self.asset_grid.addWidget(
                card,
                row,
                column
            )

            self.asset_cards[
                key
            ] = value_label

        # =================================================
        # SUMMARY
        # =================================================

        summary_frame = QFrame()

        summary_frame.setObjectName(
            "SummaryFrame"
        )

        summary_layout = QVBoxLayout(
            summary_frame
        )

        summary_title = QLabel(
            "Inventory Summary"
        )

        summary_title.setStyleSheet(
            """
            QLabel {
                font-size: 17px;
                font-weight: bold;
            }
            """
        )

        summary_layout.addWidget(
            summary_title
        )

        self.summary_label = QLabel()

        self.summary_label.setWordWrap(
            True
        )

        self.summary_label.setStyleSheet(
            """
            QLabel {
                color: #BBBBBB;
                font-size: 13px;
            }
            """
        )

        summary_layout.addWidget(
            self.summary_label
        )

        main_layout.addWidget(
            summary_frame
        )

        main_layout.addStretch()

        # =================================================
        # STYLE
        # =================================================

        self.setStyleSheet(
            """
            QFrame#MetricCard {

                background-color: #292929;

                border: 1px solid #444444;

                border-radius: 10px;

            }

            QFrame#MetricCard:hover {

                border: 1px solid #777777;

            }

            QFrame#SummaryFrame {

                background-color: #242424;

                border: 1px solid #444444;

                border-radius: 10px;

            }

            QPushButton {

                min-height: 34px;

                padding-left: 14px;

                padding-right: 14px;

                border-radius: 6px;

                border: 1px solid #555555;

                background-color: #303030;

            }

            QPushButton:hover {

                background-color: #3A3A3A;

            }
            """
        )

    # =====================================================
    # CREATE CARD
    # =====================================================

    def _create_card(
        self,
        title
    ):

        frame = QFrame()

        frame.setObjectName(
            "MetricCard"
        )

        frame.setMinimumHeight(
            105
        )

        layout = QVBoxLayout(
            frame
        )

        layout.setContentsMargins(
            15,
            12,
            15,
            12
        )

        title_label = QLabel(
            title
        )

        title_label.setStyleSheet(
            """
            QLabel {
                color: #999999;
                font-size: 11px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            title_label
        )

        value_label = QLabel(
            "0"
        )

        value_label.setStyleSheet(
            """
            QLabel {
                font-size: 30px;
                font-weight: bold;
            }
            """
        )

        layout.addWidget(
            value_label
        )

        return (
            frame,
            value_label
        )

    # =====================================================
    # REFRESH
    # =====================================================

    def refresh(self):

        if (
            self.global_asset_service
            is None
        ):

            return

        try:

            self.global_asset_service.refresh()

            counts = (
                self.global_asset_service
                .get_asset_counts()
            )

        except Exception as error:

            self.summary_label.setText(
                f"Unable to load asset data:\n{error}"
            )

            return

        # =================================================
        # UPDATE CARDS
        # =================================================

        for key, value in counts.items():

            if key in self.asset_cards:

                self.asset_cards[
                    key
                ].setText(
                    f"{value:,}"
                )

        # =================================================
        # SUMMARY
        # =================================================

        self.summary_label.setText(

            f"Projects: "
            f"{counts.get('projects', 0):,}\n"

            f"Substations: "
            f"{counts.get('substations', 0):,}\n"

            f"Switchboards: "
            f"{counts.get('switchboards', 0):,}\n"

            f"Panels: "
            f"{counts.get('panels', 0):,}\n"

            f"CTs: "
            f"{counts.get('cts', 0):,}\n"

            f"Numerical Relays: "
            f"{counts.get('relays', 0):,}\n"

            f"Auxiliary Relays: "
            f"{counts.get('aux', 0):,}\n"

            f"Meters: "
            f"{counts.get('meters', 0):,}"

        )