from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
MAIN_WINDOW = ROOT / "app" / "ui" / "main_window.py"
BACKUP = MAIN_WINDOW.with_suffix(".py.before_icons")

text = MAIN_WINDOW.read_text(encoding="utf-8")

if "from app.ui.icon_helper import icon" not in text:
    anchor = "from app.ui.dashboard_view import DashboardView\n"
    if anchor not in text:
        raise SystemExit("Could not find import anchor in main_window.py")
    text = text.replace(anchor, anchor + "from app.ui.icon_helper import icon\n", 1)

old = '''        brand_icon = QLabel(
            "⚡"
        )
'''
new = '''        brand_icon = QLabel()
        brand_icon.setPixmap(
            icon("app").pixmap(32, 32)
        )
'''
if old in text:
    text = text.replace(old, new, 1)

pairs = [
    (
'''        self.project_action.setToolTip(
            "Open and manage testing projects"
        )
''',
'''        self.project_action.setIcon(icon("projects"))
        self.project_action.setToolTip(
            "Open and manage testing projects"
        )
'''
    ),
    (
'''        self.asset_management_action.setToolTip(
            "Browse the global asset register, configurations and test history"
        )
''',
'''        self.asset_management_action.setIcon(icon("assets"))
        self.asset_management_action.setToolTip(
            "Browse the global asset register, configurations and test history"
        )
'''
    ),
    (
'''        self.report_action.setToolTip(
            "Generate testing reports"
        )
''',
'''        self.report_action.setIcon(icon("reports"))
        self.report_action.setToolTip(
            "Generate testing reports"
        )
'''
    ),
    (
'''        self.dashboard_action.setToolTip(
            "View testing statistics and operational overview"
        )
''',
'''        self.dashboard_action.setIcon(icon("dashboard"))
        self.dashboard_action.setToolTip(
            "View testing statistics and operational overview"
        )
'''
    ),
]
for old, new in pairs:
    if old in text and new not in text:
        text = text.replace(old, new, 1)

if not BACKUP.exists():
    shutil.copy2(MAIN_WINDOW, BACKUP)

MAIN_WINDOW.write_text(text, encoding="utf-8")
compile(text, str(MAIN_WINDOW), "exec")
print(f"Icons applied: {MAIN_WINDOW}")
print(f"Backup created: {BACKUP}")
