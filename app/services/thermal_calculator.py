import ast
import math


class UnsafeEquationError(ValueError):
    pass


class _SafeExpressionValidator(ast.NodeVisitor):
    ALLOWED_NODES = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.USub,
        ast.UAdd,
        ast.Name,
        ast.Constant,
        ast.Call,
    )
    ALLOWED_FUNCTIONS = {
        "sqrt": math.sqrt,
        "exp": math.exp,
        "log": math.log,
        "ln": math.log,
        "log10": math.log10,
        "abs": abs,
        "min": min,
        "max": max,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
    }

    def __init__(self, names):
        self.names = set(names) | set(self.ALLOWED_FUNCTIONS) | {"pi", "e"}

    def generic_visit(self, node):
        if not isinstance(node, self.ALLOWED_NODES):
            raise UnsafeEquationError(
                f"Unsupported expression element: {type(node).__name__}"
            )
        super().generic_visit(node)

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise UnsafeEquationError("Only named mathematical functions are allowed.")
        if node.func.id not in self.ALLOWED_FUNCTIONS:
            raise UnsafeEquationError(
                f"Function '{node.func.id}' is not allowed."
            )
        if node.keywords:
            raise UnsafeEquationError("Keyword arguments are not allowed.")
        for arg in node.args:
            self.visit(arg)

    def visit_Name(self, node):
        if node.id not in self.names:
            raise UnsafeEquationError(
                f"Unknown variable or function: {node.id}"
            )


class ThermalCalculator:

    @staticmethod
    def normalize_equation(expression):
        expression = str(expression or "").strip()
        if not expression:
            raise ValueError("Equation is required.")
        expression = expression.replace("^", "**")
        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        return expression

    @classmethod
    def validate_equation(cls, expression, variable_names):
        expression = cls.normalize_equation(expression)
        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as exc:
            raise ValueError(f"Invalid equation syntax: {exc.msg}") from exc
        _SafeExpressionValidator(variable_names).visit(tree)
        return expression

    @classmethod
    def evaluate_equation(cls, expression, variables):
        names = set(variables.keys())
        normalized = cls.validate_equation(expression, names)
        environment = dict(_SafeExpressionValidator.ALLOWED_FUNCTIONS)
        environment.update({"pi": math.pi, "e": math.e})
        environment.update({k: float(v) for k, v in variables.items()})
        try:
            result = eval(normalized, {"__builtins__": {}}, environment)
        except (ArithmeticError, ValueError, TypeError, ZeroDivisionError) as exc:
            raise ValueError(f"Equation could not be evaluated: {exc}") from exc
        if isinstance(result, bool) or not isinstance(result, (int, float)):
            raise ValueError("Equation must return a numeric value.")
        result = float(result)
        if not math.isfinite(result):
            raise ValueError("Equation returned a non-finite value.")
        return result

    @classmethod
    def equation_time(cls, current_multiple, equation, parameters, independent_variable="I"):
        variables = dict(parameters or {})
        variables[independent_variable] = float(current_multiple)
        return cls.evaluate_equation(equation, variables)

    @staticmethod
    def generate_equation_curve(template, samples=100):
        if not template.equation:
            return []
        x_min = float(template.x_min)
        x_max = float(template.x_max)
        if x_max <= x_min:
            raise ValueError("Curve maximum must be greater than curve minimum.")
        samples = max(2, min(int(samples), 500))
        points = []
        for index in range(samples):
            x = x_min + (x_max - x_min) * index / (samples - 1)
            try:
                y = ThermalCalculator.equation_time(
                    x,
                    template.equation,
                    template.parameters,
                    template.independent_variable,
                )
            except ValueError:
                continue
            if y >= 0 and math.isfinite(y):
                points.append((x, y))
        return points

    @staticmethod
    def interpolate_time(current_multiple, curve_points):
        if not curve_points:
            raise ValueError("Thermal curve contains no points.")
        points = sorted(curve_points, key=lambda point: point.current_multiple)
        x = float(current_multiple)
        if x <= points[0].current_multiple:
            return float(points[0].operating_time)
        if x >= points[-1].current_multiple:
            return float(points[-1].operating_time)
        for lower, upper in zip(points, points[1:]):
            x1 = float(lower.current_multiple)
            x2 = float(upper.current_multiple)
            if x1 <= x <= x2:
                y1 = float(lower.operating_time)
                y2 = float(upper.operating_time)
                if x2 == x1:
                    return y1
                return y1 + ((x - x1) / (x2 - x1)) * (y2 - y1)
        raise ValueError("Unable to interpolate thermal curve.")

    @staticmethod
    def exponential_time(current_multiple, pickup_multiple, thermal_constant, target_fraction=0.95):
        current_multiple = float(current_multiple)
        pickup_multiple = float(pickup_multiple)
        thermal_constant = float(thermal_constant)
        target_fraction = float(target_fraction)
        if current_multiple <= pickup_multiple:
            return float("inf")
        if thermal_constant <= 0:
            raise ValueError("Thermal constant must be greater than zero.")
        if not 0 < target_fraction < 1:
            raise ValueError("Target fraction must be between 0 and 1.")
        return -thermal_constant * math.log(1.0 - target_fraction)

    @staticmethod
    def calculate_error(actual_time, expected_time):
        actual_time = float(actual_time)
        expected_time = float(expected_time)
        if expected_time == 0:
            return 0.0
        return ((actual_time - expected_time) / expected_time) * 100.0

    @staticmethod
    def evaluate(actual_time, expected_time, tolerance):
        error = ThermalCalculator.calculate_error(actual_time, expected_time)
        passed = abs(error) <= float(tolerance)
        return {
            "expected_time": float(expected_time),
            "actual_time": float(actual_time),
            "error_percent": error,
            "tolerance": float(tolerance),
            "passed": passed,
            "result": "PASS" if passed else "FAIL",
        }
