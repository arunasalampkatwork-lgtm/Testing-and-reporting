from dataclasses import dataclass


@dataclass
class ProtectionFunction:

    function_id: str
    name: str
    description: str = ""