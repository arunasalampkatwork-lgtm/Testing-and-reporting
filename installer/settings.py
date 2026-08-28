from pathlib import Path
import os
import sys
import shutil


# =========================================================
# APPLICATION ROOT
# =========================================================

# In development, keep the existing repository layout.
# In a PyInstaller build, application data must NOT live beside
# the EXE because Program Files is normally not writable.
APP_ROOT = Path(__file__).resolve().parents[2]


# =========================================================
# USER-WRITABLE DATA
# =========================================================

if getattr(sys, "frozen", False):

    USER_DATA_ROOT = Path(
        os.environ.get(
            "LOCALAPPDATA",
            Path.home() / "AppData" / "Local"
        )
    ) / "ProtectionTestingSuite"

else:

    USER_DATA_ROOT = APP_ROOT


DATA_DIR = USER_DATA_ROOT / "data"
PROJECTS_DIR = USER_DATA_ROOT / "projects"


# =========================================================
# BUNDLED INITIAL DATA
# =========================================================

BUNDLED_ROOT = Path(
    getattr(
        sys,
        "_MEIPASS",
        APP_ROOT
    )
)

BUNDLED_DATA_DIR = (
    BUNDLED_ROOT / "data"
)

BUNDLED_PROJECTS_DIR = (
    BUNDLED_ROOT / "projects"
)


def _copy_initial_file(
    source,
    destination
):
    """
    Copy an initial bundled file only when the user's copy
    does not already exist.
    """

    if (
        source.exists()
        and
        not destination.exists()
    ):

        destination.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        shutil.copy2(
            source,
            destination
        )


def ensure_user_data():

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    PROJECTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # -----------------------------------------------------
    # Seed database files if bundled copies exist.
    # -----------------------------------------------------

    for filename in (
        "AssetDatabase.xlsx",
        "TestHistory.xlsx",
    ):

        _copy_initial_file(
            BUNDLED_DATA_DIR / filename,
            DATA_DIR / filename
        )

    # -----------------------------------------------------
    # Seed projects only on first installation.
    #
    # Existing projects are NEVER overwritten.
    # -----------------------------------------------------

    if (
        BUNDLED_PROJECTS_DIR.exists()
        and
        not any(PROJECTS_DIR.iterdir())
    ):

        for source in BUNDLED_PROJECTS_DIR.iterdir():

            destination = (
                PROJECTS_DIR / source.name
            )

            if source.is_dir():

                shutil.copytree(
                    source,
                    destination,
                    dirs_exist_ok=True
                )

            else:

                shutil.copy2(
                    source,
                    destination
                )


ensure_user_data()


# =========================================================
# INITIAL SUBSTATIONS
# =========================================================

SUBSTATIONS = [
    [
        "REF-I",
        "REF-II",
        "FCCU",
        "WAX",
        "PROPYLENE",
        "LEB",
        "DHDS",
        "RESID SRU",
        "DCU",
        "BS VI",
        "OMS",
        "SS-4",
        "SS-5 A&B",
        "SS-5 C&D",
        "SS 6",
        "SS 7",
        "MOUNDED BULLET",
        "3.5 MGR",
        "ETP-2 SS-3",
        "ETP-4",
        "ETP HT",
        "CRWS",
        "CHEMICAL HOUSE",
        "MTF SS",
        "DMRO",
        "TTP",
        "SS-1",
        "SS-2",
        "EURO-IV",
        "NHGU",
        "TANK FARM MCC",
        "PT-213",
        "GT-IV",
        "NOPH",
        "NPH",
        "DESAL SEASHORE",
        "DESAL RO",
        "COGEN",
        "CPP",
        "CPP-C",
        "R&D",
        "DM",
        "NDM",
        "FWPH",
        "COKE YARD",
        "110 kV SS",
        "110 kV YARD",
        "CORPORATE OFFICE",
    ]
]


ASSET_DATABASE = DATA_DIR / "AssetDatabase.xlsx"
TEST_HISTORY_DATABASE = DATA_DIR / "TestHistory.xlsx"
