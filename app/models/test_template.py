from dataclasses import dataclass


@dataclass
class TestField:

    field_id: str
    label: str
    field_type: str = "text"
    unit: str = ""
    required: bool = False


@dataclass
class TestTemplate:

    template_id: str
    protection_function: str
    name: str
    fields: list[TestField]