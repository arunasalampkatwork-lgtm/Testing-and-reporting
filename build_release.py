from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
ICON = ROOT / "resources" / "ProtectionTestingSuite.ico"
RELEASE_DATA = ROOT / "release_data"
RELEASE_PROJECTS = RELEASE_DATA / "projects"
EXE = ROOT / "ProtectionTestingSuite.exe"
ISS = ROOT / "ProtectionTestingSuite.iss"


def find_iscc():
    candidates = [
        shutil.which("ISCC.exe"),
        Path.home() / "AppData" / "Local" / "Programs" / "Inno Setup 6" / "ISCC.exe",
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files (x86)\Inno Setup 7\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 7\ISCC.exe"),
    ]

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate)

    return None


def run(command):
    print("\n>", " ".join(str(x) for x in command))
    subprocess.run(command, cwd=ROOT, check=True)


def prepare_release_data():
    """
    Validate the clean release-data staging area.

    IMPORTANT:
    Development data/ and projects/ are never copied into the release.
    """
    if not RELEASE_DATA.exists():
        raise SystemExit(
            "ERROR: release_data directory is missing."
        )

    RELEASE_PROJECTS.mkdir(
        parents=True,
        exist_ok=True
    )

    # Make sure the release project directory contains no development files.
    # This intentionally deletes only the release staging directory contents.
    for item in RELEASE_PROJECTS.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()


def main():
    if not (ROOT / "main.py").exists():
        raise SystemExit("ERROR: main.py was not found.")

    if not ICON.exists():
        raise SystemExit(
            f"ERROR: Application icon was not found:\n{ICON}"
        )

    prepare_release_data()

    # Clean PyInstaller working artefacts.
    for path in [
        ROOT / "build",
        ROOT / "ProtectionTestingSuite.spec",
    ]:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.exists():
            path.unlink()

    if EXE.exists():
        EXE.unlink()

    python = sys.executable

    try:
        subprocess.run(
            [python, "-m", "PyInstaller", "--version"],
            cwd=ROOT,
            check=True,
        )
    except subprocess.CalledProcessError:
        raise SystemExit(
            "\nPyInstaller is not installed in this Python environment.\n"
            f"Python: {python}\n\n"
            "Install it with:\n"
            "    python -m pip install pyinstaller\n"
        )

    # Build EXE directly in project root.
    run([
        python,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        "ProtectionTestingSuite",
        "--icon",
        str(ICON),
        "--distpath",
        str(ROOT),
        "--workpath",
        str(ROOT / "build"),
        "--specpath",
        str(ROOT / "build"),
        "main.py",
    ])

    if not EXE.exists():
        raise SystemExit(
            f"ERROR: PyInstaller completed but EXE was not found:\n{EXE}"
        )

    print(f"\nEXE created successfully:\n{EXE}")

    iscc = find_iscc()

    if iscc is None:
        print(
            "\nWARNING: Inno Setup compiler (ISCC.exe) was not found."
            "\nThe standalone EXE was built successfully."
        )
        return

    print(f"\nInno Setup compiler found:\n{iscc}")

    run([
        str(iscc),
        str(ISS),
    ])

    installer = ROOT / "ProtectionTestingSuite_Setup.exe"

    if installer.exists():
        print(
            f"\nInstaller created successfully:\n{installer}"
        )
    else:
        print(
            "\nWARNING: Inno Setup completed, but the expected installer "
            f"was not found:\n{installer}"
        )


if __name__ == "__main__":
    main()
