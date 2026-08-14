from dataclasses import dataclass
from datetime import datetime


@dataclass
class TestSession:

    test_id: str

    project_id: str

    panel_id: str

    test_date: str

    tester: str = ""

    status: str = "IN PROGRESS"