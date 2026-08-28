from pathlib import Path
import os
import shutil
import sys


# ============================================================
# APPLICATION PATHS
# ============================================================

# In development:
#   APP_ROOT = project root
#
# In a PyInstaller --onefile EXE:
#   APP_ROOT = directory containing the EXE
#
# APP_ROOT should be treated as the application/install location,
# not as the writable data location.
if getattr(sys, "frozen", False):
    APP_ROOT = Path(sys.executable).resolve().parent
else:
    APP_ROOT = Path(__file__).resolve().parents[2]


# ============================================================
# PERSISTENT USER DATA
# ============================================================

def _get_persistent_root():
    """
    Return the permanent writable data location.

    Development:
        Keep the existing project-root data/projects folders.

    Installed/frozen EXE:
        Store writable application data under:
        %LOCALAPPDATA%\\ProtectionTestingSuite

    This prevents PyInstaller's temporary extraction directory
    from becoming the application's database/project location.
    """
    if not getattr(sys, "frozen", False):
        return APP_ROOT

    local_app_data = os.environ.get("LOCALAPPDATA")

    if local_app_data:
        return (
            Path(local_app_data)
            / "ProtectionTestingSuite"
        )

    # Fallback for unusual Windows environments.
    user_profile = Path.home()

    return (
        user_profile
        / "AppData"
        / "Local"
        / "ProtectionTestingSuite"
    )


PERSISTENT_ROOT = _get_persistent_root()

DATA_DIR = PERSISTENT_ROOT / "data"
PROJECTS_DIR = PERSISTENT_ROOT / "projects"


# ============================================================
# DIRECTORY INITIALIZATION
# ============================================================

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

PROJECTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# FIRST-RUN DATA MIGRATION
# ============================================================

def _copy_directory_contents(source, destination):
    """
    Copy the contents of source into destination without deleting
    anything already present in destination.

    Existing files in the persistent location are preserved.
    """
    source = Path(source)
    destination = Path(destination)

    if not source.exists() or not source.is_dir():
        return

    destination.mkdir(
        parents=True,
        exist_ok=True
    )

    for item in source.iterdir():

        target = destination / item.name

        if item.is_dir():

            shutil.copytree(
                item,
                target,
                dirs_exist_ok=True
            )

        elif item.is_file():

            # Never overwrite a file that already exists in the
            # persistent location.
            if not target.exists():
                shutil.copy2(
                    item,
                    target
                )


def _migrate_existing_development_data():
    """
    On the first frozen/installed run, migrate data/projects from
    the development installation if they exist.

    This is intentionally conservative:
    existing persistent files are never overwritten.
    """
    if not getattr(sys, "frozen", False):
        return

    development_data = APP_ROOT / "data"
    development_projects = APP_ROOT / "projects"

    # Do not copy a directory onto itself.
    if development_data.resolve() != DATA_DIR.resolve():
        _copy_directory_contents(
            development_data,
            DATA_DIR
        )

    if development_projects.resolve() != PROJECTS_DIR.resolve():
        _copy_directory_contents(
            development_projects,
            PROJECTS_DIR
        )


_migrate_existing_development_data()


# ============================================================
# DATABASE FILES
# ============================================================

ASSET_DATABASE = DATA_DIR / "AssetDatabase.xlsx"
TEST_HISTORY_DATABASE = DATA_DIR / "TestHistory.xlsx"


# ============================================================
# INITIAL SUBSTATIONS
# ============================================================

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
        "ETP-4 ",
        "ETP HT",
        "CRWS",
        "CHEMICAL HOUSE ",
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
