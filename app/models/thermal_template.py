from dataclasses import dataclass, field


@dataclass
class ThermalCurvePoint:
    current_multiple: float
    operating_time: float


@dataclass
class ThermalVariable:
    name: str
    unit: str = ""
    description: str = ""
    default_value: float = 0.0
    is_input: bool = False


@dataclass
class ThermalTemplate:
    template_id: str
    protection_function: str
    manufacturer: str
    model: str
    name: str
    curve_type: str = "POINT_TABLE"
    rated_current: float = 0.0
    pickup_current: float = 1.0
    thermal_constant: float = 0.0
    cooling_constant: float = 0.0
    curves: list[ThermalCurvePoint] = field(default_factory=list)
    heating_curve: list[ThermalCurvePoint] = field(default_factory=list)
    cooling_curve: list[ThermalCurvePoint] = field(default_factory=list)
    equation: str = ""
    independent_variable: str = "I"
    dependent_variable: str = "T"
    variables: list[ThermalVariable] = field(default_factory=list)
    parameters: dict[str, float] = field(default_factory=dict)
    x_min: float = 1.0
    x_max: float = 20.0
    notes: str = ""
