from dataclasses import dataclass, field
from typing import Any


@dataclass
class ProtectionTest:

    test_id: str

    panel_id: str

    relay_id: str

    protection_code: str

    settings: dict[str, Any] = field(
        default_factory=dict
    )

    measurements: dict[str, Any] = field(
        default_factory=dict
    )

    result: str = "NOT TESTED"

    remarks: str = ""