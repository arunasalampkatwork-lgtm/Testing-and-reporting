# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


# The .spec file lives in <project>\installer.
# SPECPATH therefore points at the installer directory.
# The actual project root is its parent.
PROJECT_ROOT = Path(SPECPATH).resolve().parent


hiddenimports = collect_submodules("PySide6")


a = Analysis(
    [str(PROJECT_ROOT / "main.py")],

    pathex=[
        str(PROJECT_ROOT)
    ],

    binaries=[],

    datas=[
        # Optional bundled application databases.
        # PyInstaller accepts these only when the source exists.
        *(
            [
                (
                    str(PROJECT_ROOT / "data"),
                    "data"
                )
            ]
            if (PROJECT_ROOT / "data").exists()
            else []
        ),

        # Optional bundled project templates / initial projects.
        *(
            [
                (
                    str(PROJECT_ROOT / "projects"),
                    "projects"
                )
            ]
            if (PROJECT_ROOT / "projects").exists()
            else []
        ),
    ],

    hiddenimports=hiddenimports,

    hookspath=[],

    hooksconfig={},

    runtime_hooks=[],

    excludes=[
        "tkinter",
    ],

    noarchive=False,
)


pyz = PYZ(
    a.pure,
    a.zipped_data
)


exe = EXE(
    pyz,
    a.scripts,

    a.binaries,
    a.datas,

    [],

    name="ProtectionTestingSuite",

    debug=False,

    bootloader_ignore_signals=False,

    strip=False,

    upx=True,

    console=False,

    icon=str(
        PROJECT_ROOT /
        "installer" /
        "ProtectionTestingSuite_1.ico"
    ),

    version=str(
        PROJECT_ROOT /
        "installer" /
        "version_info.txt"
    ),
)
