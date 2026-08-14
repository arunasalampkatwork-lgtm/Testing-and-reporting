from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Panel:

    node_id: str

    equipment_tag: str = ""

    equipment_type: str = ""

    description: str = ""

    rated_voltage: str = ""

    rated_power: str = ""

    number_of_cts: int = 0

    number_of_numerical_relays: int = 0

    number_of_auxiliary_relays: int = 0