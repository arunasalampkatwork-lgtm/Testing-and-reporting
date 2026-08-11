from pathlib import Path


# Root directory of the application
APP_ROOT = Path(__file__).resolve().parents[2]

# Data directories
DATA_DIR = APP_ROOT / "data"
PROJECTS_DIR = APP_ROOT / "projects"

# Database files
ASSET_DATABASE = DATA_DIR / "AssetDatabase.xlsx"
TEST_HISTORY_DATABASE = DATA_DIR / "TestHistory.xlsx"

# Initial substations
SUBSTATIONS = [
    ["REF-I","REF-II","FCCU","WAX","PROPYLENE","LEB","DHDS","RESID SRU","DCU","BS VI","OMS","SS-4","SS-5 A&B","SS-5 C&D","SS 6","SS 7","MOUNDED BULLET","3.5 MGR","ETP-2 SS-3","ETP-4 ","ETP HT","CRWS","CHEMICAL HOUSE ","MTF SS","DMRO","TTP","SS-1","SS-2","EURO-IV","NHGU","TANK FARM MCC","PT-213","GT-IV","NOPH","NPH","DESAL SEASHORE","DESAL RO","COGEN","CPP","CPP-C","R&D","DM","NDM","FWPH","COKE YARD","110 kV SS","110 kV YARD","CORPORATE OFFICE"]
]