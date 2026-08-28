import sys
import traceback
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
)

from app.ui.main_window import MainWindow
from app.config.settings import DATA_DIR, ensure_user_data


APP_ID = "CPCL.ProtectionTestingSuite"


def install_exception_hook():

    def exception_hook(
        exc_type,
        exc_value,
        exc_traceback
    ):

        if issubclass(
            exc_type,
            KeyboardInterrupt
        ):

            sys.__excepthook__(
                exc_type,
                exc_value,
                exc_traceback
            )

            return

        DATA_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        log_file = (
            DATA_DIR /
            "application_error.log"
        )

        try:

            with open(
                log_file,
                "a",
                encoding="utf-8"
            ) as file:

                traceback.print_exception(
                    exc_type,
                    exc_value,
                    exc_traceback,
                    file=file
                )

        except Exception:

            pass

        traceback.print_exception(
            exc_type,
            exc_value,
            exc_traceback
        )

        try:

            QMessageBox.critical(
                None,
                "Protection Testing Suite",
                (
                    "The application encountered an unexpected "
                    "error.\n\n"
                    f"{exc_value}\n\n"
                    f"Details were written to:\n{log_file}"
                )
            )

        except Exception:

            pass

    sys.excepthook = exception_hook


def main():

    ensure_user_data()

    # Windows taskbar grouping / shortcut identity.
    try:

        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            APP_ID
        )

    except Exception:

        pass

    app = QApplication(
        sys.argv
    )

    app.setApplicationName(
        "Protection Testing Suite"
    )

    app.setApplicationDisplayName(
        "Protection Testing Suite"
    )

    app.setOrganizationName(
        "CPCL"
    )

    app.setApplicationVersion(
        "1.0.0"
    )

    install_exception_hook()

    window = MainWindow()

    window.show()

    sys.exit(
        app.exec()
    )


if __name__ == "__main__":

    main()
