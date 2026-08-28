from pathlib import Path
import sys
from PySide6.QtGui import QIcon


def resource_root() -> Path:
    candidates = []

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.extend([
            exe_dir / "resources",
            exe_dir / "_internal" / "resources",
        ])

    project_root = Path(__file__).resolve().parents[2]
    candidates.extend([
        project_root / "resources",
        project_root / "app" / "resources",
    ])

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


def icon(name: str) -> QIcon:
    path = resource_root() / "icons" / f"{name}.svg"
    return QIcon(str(path)) if path.exists() else QIcon()
