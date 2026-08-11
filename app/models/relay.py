from dataclasses import dataclass, field


@dataclass
class Relay:

    relay_id: str

    relay_tag: str = ""

    manufacturer: str = ""

    model: str = ""

    serial_number: str = ""

    protection_functions: list[str] = field(
        default_factory=list
    )