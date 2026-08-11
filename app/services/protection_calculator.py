"""
Protection calculation engine.

All engineering calculations used by the protection-testing
UI should be performed here.

The UI should only:
    1. collect values
    2. call this class
    3. display the returned result
"""

import math


class ProtectionCalculator:

    # =========================================================
    # GENERAL HELPERS
    # =========================================================

    @staticmethod
    def _validate_number(
        value,
        name="value"
    ):

        try:

            number = float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                f"{name} must be a valid number."
            )

        if not math.isfinite(
            number
        ):

            raise ValueError(
                f"{name} must be finite."
            )

        return number

    @staticmethod
    def _percentage_error(
        expected,
        actual
    ):

        expected = ProtectionCalculator._validate_number(
            expected,
            "Expected value"
        )

        actual = ProtectionCalculator._validate_number(
            actual,
            "Actual value"
        )

        if expected == 0:

            raise ZeroDivisionError(
                "Expected value cannot be zero."
            )

        return (
            (actual - expected)
            / abs(expected)
        ) * 100.0

    @staticmethod
    def _within_tolerance(
        expected,
        actual,
        tolerance_percent
    ):

        expected = ProtectionCalculator._validate_number(
            expected,
            "Expected value"
        )

        actual = ProtectionCalculator._validate_number(
            actual,
            "Actual value"
        )

        tolerance_percent = ProtectionCalculator._validate_number(
            tolerance_percent,
            "Tolerance"
        )

        if tolerance_percent < 0:

            raise ValueError(
                "Tolerance cannot be negative."
            )

        if expected == 0:

            return abs(actual) <= (
                tolerance_percent / 100.0
            )

        lower = (
            expected
            * (
                1.0
                -
                tolerance_percent / 100.0
            )
        )

        upper = (
            expected
            * (
                1.0
                +
                tolerance_percent / 100.0
            )
        )

        if lower > upper:

            lower, upper = (
                upper,
                lower
            )

        return (
            lower
            <= actual
            <= upper
        )

    # =========================================================
    # 50 / 50N / 46
    # =========================================================

    @staticmethod
    def evaluate_current_pickup(
        expected_current,
        actual_current,
        tolerance_percent=5.0
    ):

        expected_current = (
            ProtectionCalculator._validate_number(
                expected_current,
                "Expected current"
            )
        )

        actual_current = (
            ProtectionCalculator._validate_number(
                actual_current,
                "Actual current"
            )
        )

        tolerance_percent = (
            ProtectionCalculator._validate_number(
                tolerance_percent,
                "Tolerance"
            )
        )

        if expected_current <= 0:

            raise ValueError(
                "Expected current must be greater than zero."
            )

        error_percent = (
            ProtectionCalculator._percentage_error(
                expected_current,
                actual_current
            )
        )

        passed = (
            ProtectionCalculator._within_tolerance(
                expected_current,
                actual_current,
                tolerance_percent
            )
        )

        return {
            "expected_current": expected_current,
            "actual_current": actual_current,
            "error_percent": error_percent,
            "result": (
                "PASS"
                if passed
                else "FAIL"
            ),
        }

    # =========================================================
    # IDMT
    # =========================================================

    @staticmethod
    def calculate_psm(
        pickup_current,
        test_current
    ):

        pickup_current = (
            ProtectionCalculator._validate_number(
                pickup_current,
                "Pickup current"
            )
        )

        test_current = (
            ProtectionCalculator._validate_number(
                test_current,
                "Test current"
            )
        )

        if pickup_current <= 0:

            raise ValueError(
                "Pickup current must be greater than zero."
            )

        return (
            test_current
            /
            pickup_current
        )

    @staticmethod
    def _normalise_curve_name(
        curve_code
    ):

        if curve_code is None:
            return ""

        text = str(
            curve_code
        ).strip().lower()

        text = (
            text
            .replace("_", " ")
            .replace("-", " ")
        )

        return " ".join(
            text.split()
        )

    @staticmethod
    def calculate_51_time(
        curve_code,
        pickup_current,
        test_current,
        tms
    ):
        """
        Calculate IEC IDMT operating time.

        Supported IEC curves:

            IEC Standard / Normal Inverse
            IEC Very Inverse
            IEC Extremely Inverse
            IEC Long Time Inverse

        Formula:

            t = TMS * K / ((PSM ^ alpha) - 1)
        """

        pickup_current = (
            ProtectionCalculator._validate_number(
                pickup_current,
                "Pickup current"
            )
        )

        test_current = (
            ProtectionCalculator._validate_number(
                test_current,
                "Test current"
            )
        )

        tms = (
            ProtectionCalculator._validate_number(
                tms,
                "TMS"
            )
        )

        if pickup_current <= 0:

            raise ValueError(
                "Pickup current must be greater than zero."
            )

        if test_current <= 0:

            raise ValueError(
                "Test current must be greater than zero."
            )

        if tms <= 0:

            raise ValueError(
                "TMS must be greater than zero."
            )

        psm = (
            test_current
            /
            pickup_current
        )

        if psm <= 1.0:

            raise ValueError(
                "PSM must be greater than 1.0 for IDMT calculation."
            )

        curve = (
            ProtectionCalculator
            ._normalise_curve_name(
                curve_code
            )
        )

        # IEC 60255 commonly used constants.
        if (
            "extremely" in curve
            or "extreme" in curve
        ):

            k = 80.0
            alpha = 2.0

        elif "very" in curve:

            k = 13.5
            alpha = 1.0

        elif (
            "long" in curve
            or "lt inverse" in curve
        ):

            k = 120.0
            alpha = 1.0

        else:

            # Normal / Standard Inverse
            k = 0.14
            alpha = 0.02

        denominator = (
            math.pow(
                psm,
                alpha
            )
            -
            1.0
        )

        if denominator <= 0:

            raise ValueError(
                "Invalid IDMT denominator."
            )

        expected_time = (
            tms
            *
            k
            /
            denominator
        )

        return {
            "psm": psm,
            "expected_time": expected_time,
            "curve": curve_code,
            "tms": tms,
        }

    @staticmethod
    def evaluate_time_test(
        expected_time,
        actual_time,
        tolerance_percent=5.0
    ):

        expected_time = (
            ProtectionCalculator._validate_number(
                expected_time,
                "Expected time"
            )
        )

        actual_time = (
            ProtectionCalculator._validate_number(
                actual_time,
                "Actual time"
            )
        )

        tolerance_percent = (
            ProtectionCalculator._validate_number(
                tolerance_percent,
                "Tolerance"
            )
        )

        if expected_time <= 0:

            raise ValueError(
                "Expected time must be greater than zero."
            )

        if actual_time < 0:

            raise ValueError(
                "Actual time cannot be negative."
            )

        error_percent = (
            ProtectionCalculator._percentage_error(
                expected_time,
                actual_time
            )
        )

        lower_limit = (
            expected_time
            *
            (
                1.0
                -
                tolerance_percent / 100.0
            )
        )

        upper_limit = (
            expected_time
            *
            (
                1.0
                +
                tolerance_percent / 100.0
            )
        )

        passed = (
            lower_limit
            <= actual_time
            <= upper_limit
        )

        return {
            "expected_time": expected_time,
            "actual_time": actual_time,
            "error_percent": error_percent,
            "lower_limit": lower_limit,
            "upper_limit": upper_limit,
            "result": (
                "PASS"
                if passed
                else "FAIL"
            ),
        }

    # =========================================================
    # VOLTAGE
    # =========================================================

    @staticmethod
    def evaluate_threshold(
        expected_value,
        actual_value,
        tolerance_percent=5.0,
        direction="equal"
    ):
        """
        Evaluate measured threshold against setting.

        direction:
            equal
            lower
            upper

        The numerical pickup error is always calculated against
        the setting.

        For a threshold pickup test, the measured pickup point
        must be within the configured tolerance band.
        """

        expected_value = (
            ProtectionCalculator._validate_number(
                expected_value,
                "Expected value"
            )
        )

        actual_value = (
            ProtectionCalculator._validate_number(
                actual_value,
                "Actual value"
            )
        )

        tolerance_percent = (
            ProtectionCalculator._validate_number(
                tolerance_percent,
                "Tolerance"
            )
        )

        if expected_value <= 0:

            raise ValueError(
                "Expected threshold must be greater than zero."
            )

        if tolerance_percent < 0:

            raise ValueError(
                "Tolerance cannot be negative."
            )

        direction = str(
            direction
        ).strip().lower()

        error_percent = (
            ProtectionCalculator._percentage_error(
                expected_value,
                actual_value
            )
        )

        lower_limit = (
            expected_value
            *
            (
                1.0
                -
                tolerance_percent / 100.0
            )
        )

        upper_limit = (
            expected_value
            *
            (
                1.0
                +
                tolerance_percent / 100.0
            )
        )

        if direction == "lower":

            # For an undervoltage pickup setting, the measured
            # pickup voltage is still expected to be near the
            # configured setting.
            passed = (
                lower_limit
                <= actual_value
                <= upper_limit
            )

        elif direction == "upper":

            passed = (
                lower_limit
                <= actual_value
                <= upper_limit
            )

        else:

            passed = (
                lower_limit
                <= actual_value
                <= upper_limit
            )

        return {
            "expected_value": expected_value,
            "actual_value": actual_value,
            "error_percent": error_percent,
            "lower_limit": lower_limit,
            "upper_limit": upper_limit,
            "direction": direction,
            "result": (
                "PASS"
                if passed
                else "FAIL"
            ),
        }

    # =========================================================
    # FREQUENCY
    # =========================================================

    @staticmethod
    def evaluate_frequency_pickup(
        expected_frequency,
        actual_frequency,
        tolerance_percent=5.0
    ):

        expected_frequency = (
            ProtectionCalculator._validate_number(
                expected_frequency,
                "Expected frequency"
            )
        )

        actual_frequency = (
            ProtectionCalculator._validate_number(
                actual_frequency,
                "Actual frequency"
            )
        )

        result = (
            ProtectionCalculator
            .evaluate_threshold(
                expected_value=expected_frequency,
                actual_value=actual_frequency,
                tolerance_percent=tolerance_percent,
                direction="equal"
            )
        )

        return {
            "expected_frequency": expected_frequency,
            "actual_frequency": actual_frequency,
            "error_percent": result["error_percent"],
            "lower_limit": result["lower_limit"],
            "upper_limit": result["upper_limit"],
            "result": result["result"],
        }

    # =========================================================
    # ROCOF
    # =========================================================

    @staticmethod
    def calculate_rocof(
        frequency_1,
        frequency_2,
        time_interval
    ):

        frequency_1 = (
            ProtectionCalculator._validate_number(
                frequency_1,
                "Frequency before"
            )
        )

        frequency_2 = (
            ProtectionCalculator._validate_number(
                frequency_2,
                "Frequency after"
            )
        )

        time_interval = (
            ProtectionCalculator._validate_number(
                time_interval,
                "Time interval"
            )
        )

        if time_interval <= 0:

            raise ValueError(
                "Time interval must be greater than zero."
            )

        return (
            frequency_2
            -
            frequency_1
        ) / time_interval

    @staticmethod
    def evaluate_rocof(
        expected_rocof,
        actual_rocof,
        tolerance_percent=5.0
    ):

        expected_rocof = (
            ProtectionCalculator._validate_number(
                expected_rocof,
                "Expected ROCOF"
            )
        )

        actual_rocof = (
            ProtectionCalculator._validate_number(
                actual_rocof,
                "Actual ROCOF"
            )
        )

        expected_abs = abs(
            expected_rocof
        )

        actual_abs = abs(
            actual_rocof
        )

        if expected_abs == 0:

            raise ValueError(
                "Expected ROCOF cannot be zero."
            )

        error_percent = (
            (
                actual_abs
                -
                expected_abs
            )
            /
            expected_abs
        ) * 100.0

        tolerance_percent = (
            ProtectionCalculator._validate_number(
                tolerance_percent,
                "Tolerance"
            )
        )

        lower = (
            expected_abs
            *
            (
                1.0
                -
                tolerance_percent / 100.0
            )
        )

        upper = (
            expected_abs
            *
            (
                1.0
                +
                tolerance_percent / 100.0
            )
        )

        passed = (
            lower
            <= actual_abs
            <= upper
        )

        return {
            "expected_rocof": expected_rocof,
            "actual_rocof": actual_rocof,
            "error_percent": error_percent,
            "lower_limit": lower,
            "upper_limit": upper,
            "result": (
                "PASS"
                if passed
                else "FAIL"
            ),
        }

    # =========================================================
    # DIRECTIONAL
    # =========================================================

    @staticmethod
    def _angle_difference(
        expected_angle,
        actual_angle
    ):

        difference = (
            actual_angle
            -
            expected_angle
        )

        while difference > 180.0:

            difference -= 360.0

        while difference < -180.0:

            difference += 360.0

        return difference

    @staticmethod
    def evaluate_directional_test(
        expected_angle,
        actual_angle,
        angle_tolerance=5.0
    ):

        expected_angle = (
            ProtectionCalculator._validate_number(
                expected_angle,
                "Expected angle"
            )
        )

        actual_angle = (
            ProtectionCalculator._validate_number(
                actual_angle,
                "Actual angle"
            )
        )

        angle_tolerance = (
            ProtectionCalculator._validate_number(
                angle_tolerance,
                "Angle tolerance"
            )
        )

        if angle_tolerance < 0:

            raise ValueError(
                "Angle tolerance cannot be negative."
            )

        angle_error = (
            ProtectionCalculator._angle_difference(
                expected_angle,
                actual_angle
            )
        )

        passed = (
            abs(angle_error)
            <= angle_tolerance
        )

        return {
            "expected_angle": expected_angle,
            "actual_angle": actual_angle,
            "angle_error": angle_error,
            "result": (
                "PASS"
                if passed
                else "FAIL"
            ),
        }

    # =========================================================
    # FUNCTIONAL
    # =========================================================

    @staticmethod
    def evaluate_boolean_test(
        expected_operation,
        observed_operation
    ):

        expected = str(
            expected_operation
        ).strip().upper()

        observed = str(
            observed_operation
        ).strip().upper()

        passed = (
            expected == observed
        )

        return {
            "expected_operation": expected,
            "observed_operation": observed,
            "result": (
                "PASS"
                if passed
                else "FAIL"
            ),
        }

    # =========================================================
    # DIFFERENTIAL
    # =========================================================

    @staticmethod
    def calculate_differential_current(
        current_1,
        current_2
    ):
        """
        Basic magnitude differential calculation.

        For the simple two-input testing template:

            Idiff = |I1 - I2|
        """

        current_1 = (
            ProtectionCalculator._validate_number(
                current_1,
                "Current 1"
            )
        )

        current_2 = (
            ProtectionCalculator._validate_number(
                current_2,
                "Current 2"
            )
        )

        return abs(
            current_1
            -
            current_2
        )

    @staticmethod
    def evaluate_differential_test(
        expected_current,
        actual_differential_current,
        tolerance_percent=5.0
    ):

        expected_current = (
            ProtectionCalculator._validate_number(
                expected_current,
                "Expected differential current"
            )
        )

        actual_differential_current = (
            ProtectionCalculator._validate_number(
                actual_differential_current,
                "Actual differential current"
            )
        )

        tolerance_percent = (
            ProtectionCalculator._validate_number(
                tolerance_percent,
                "Tolerance"
            )
        )

        result = (
            ProtectionCalculator
            .evaluate_threshold(
                expected_value=expected_current,
                actual_value=actual_differential_current,
                tolerance_percent=tolerance_percent,
                direction="equal"
            )
        )

        return {
            "expected_current": expected_current,
            "actual_differential_current":
                actual_differential_current,
            "error_percent":
                result["error_percent"],
            "result":
                result["result"],
        }