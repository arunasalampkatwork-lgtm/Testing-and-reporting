import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QApplication,
    QSplashScreen,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.ui.main_window import MainWindow


class LoadingSplash(QSplashScreen):
    """
    Lightweight startup splash screen.

    The splash is deliberately implemented here so no changes are
    required in MainWindow. It remains visible while MainWindow is
    being constructed, then closes automatically.
    """

    def __init__(self):
        # A transparent pixmap is used as the base so we can paint
        # our own rounded loading panel.
        from PySide6.QtGui import QPixmap

        pixmap = QPixmap(620, 360)
        pixmap.fill(Qt.transparent)

        super().__init__(pixmap)

        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.setAttribute(
            Qt.WA_TranslucentBackground,
            True
        )

        self._message = "Starting ProtectionTestingSuite..."
        self._angle = 0

        self.resize(620, 360)

        # Small animation timer. During a long, completely synchronous
        # MainWindow constructor the OS can still keep the splash visible,
        # but animation will resume whenever Qt gets control back.
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(80)

    def set_message(self, message):
        self._message = message
        self.update()

    def _animate(self):
        self._angle = (
            self._angle + 30
        ) % 360

        self.update()

        # Process pending repaint events while startup is progressing.
        QApplication.processEvents()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setRenderHint(
            QPainter.Antialiasing,
            True
        )

        # Background panel
        painter.setBrush(
            QColor(24, 27, 32, 250)
        )

        painter.setPen(
            Qt.NoPen
        )

        painter.drawRoundedRect(
            0,
            0,
            self.width(),
            self.height(),
            20,
            20
        )

        # Green accent
        painter.setBrush(
            QColor(92, 210, 70)
        )

        painter.drawRoundedRect(
            0,
            0,
            8,
            self.height(),
            4,
            4
        )

        # Application title
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)

        painter.setFont(title_font)
        painter.setPen(
            QColor(235, 238, 242)
        )

        painter.drawText(
            45,
            75,
            "ProtectionTestingSuite"
        )

        # Subtitle
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)

        painter.setFont(subtitle_font)
        painter.setPen(
            QColor(155, 160, 168)
        )

        painter.drawText(
            47,
            101,
            "Electrical Protection Testing & Reporting"
        )

        # Spinner
        center_x = self.width() // 2
        center_y = 185

        painter.setBrush(Qt.NoBrush)

        for i in range(12):
            opacity = max(
                30,
                255 - ((i * 18) % 210)
            )

            painter.setPen(
                QPen(
                    QColor(
                        92,
                        210,
                        70,
                        opacity
                    ),
                    5,
                    Qt.SolidLine,
                    Qt.RoundCap
                )
            )

            import math

            angle = (
                self._angle
                +
                i * 30
            )

            radians = math.radians(
                angle
            )

            x1 = (
                center_x
                +
                int(
                    math.cos(radians)
                    * 28
                )
            )

            y1 = (
                center_y
                +
                int(
                    math.sin(radians)
                    * 28
                )
            )

            x2 = (
                center_x
                +
                int(
                    math.cos(radians)
                    * 45
                )
            )

            y2 = (
                center_y
                +
                int(
                    math.sin(radians)
                    * 45
                )
            )

            painter.drawLine(
                x1,
                y1,
                x2,
                y2
            )

        # Loading message
        message_font = QFont()
        message_font.setPointSize(10)

        painter.setFont(
            message_font
        )

        painter.setPen(
            QColor(190, 194, 200)
        )

        painter.drawText(
            45,
            270,
            self._message
        )

        # Progress-like line
        painter.setPen(
            Qt.NoPen
        )

        painter.setBrush(
            QColor(55, 60, 68)
        )

        painter.drawRoundedRect(
            45,
            292,
            self.width() - 90,
            5,
            2,
            2
        )

        painter.setBrush(
            QColor(92, 210, 70)
        )

        # Animated moving highlight
        progress_width = (
            self.width() - 90
        )

        x = (
            45
            +
            int(
                (
                    self._angle / 360
                )
                *
                progress_width
            )
        )

        painter.drawRoundedRect(
            max(45, x - 70),
            292,
            70,
            5,
            2,
            2
        )

        # Version/startup text
        small_font = QFont()
        small_font.setPointSize(8)

        painter.setFont(
            small_font
        )

        painter.setPen(
            QColor(110, 115, 123)
        )

        painter.drawText(
            45,
            325,
            "Initializing application..."
        )

        painter.end()


def main():
    app = QApplication(sys.argv)

    # -----------------------------------------------------
    # Application metadata
    # -----------------------------------------------------

    app.setApplicationName(
        "ProtectionTestingSuite"
    )

    app.setApplicationDisplayName(
        "ProtectionTestingSuite"
    )

    # -----------------------------------------------------
    # Show splash BEFORE constructing MainWindow.
    # -----------------------------------------------------

    splash = LoadingSplash()

    # Center the splash on the available screen.
    screen = (
        QApplication.primaryScreen()
    )

    if screen is not None:
        geometry = (
            screen.availableGeometry()
        )

        x = (
            geometry.x()
            +
            (
                geometry.width()
                -
                splash.width()
            )
            // 2
        )

        y = (
            geometry.y()
            +
            (
                geometry.height()
                -
                splash.height()
            )
            // 2
        )

        splash.move(
            x,
            y
        )

    splash.show()

    QApplication.processEvents()

    # -----------------------------------------------------
    # Main application construction
    # -----------------------------------------------------

    splash.set_message(
        "Loading application..."
    )

    QApplication.processEvents()

    window = MainWindow()

    splash.set_message(
        "Preparing testing environment..."
    )

    QApplication.processEvents()

    # -----------------------------------------------------
    # Show main window
    # -----------------------------------------------------

    window.show()

    QApplication.processEvents()

    splash.set_message(
        "Ready"
    )

    QApplication.processEvents()

    # Let the splash remain visible for one short event-loop
    # cycle so the final repaint is visible, then close it.
    QTimer.singleShot(
        250,
        splash.close
    )

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":
    main()
