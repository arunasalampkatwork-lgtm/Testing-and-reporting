"""
Protection calculation engine.

All engineering calculations used by the protection-testing
UI should be performed here.

The UI should only:

    1. collect values
    2. call this class
    3. display the returned result

CURRENT REPRESENTATION
----------------------

Protection current quantities are represented primarily as
multiples of nominal relay current:

    xIn

Example:

    CT = 1000 / 1 A
    In = 1 A

    Pickup = 1.20 xIn
    Test   = 2.40 xIn

Actual secondary injection:

    Pickup = 1.20 A
    Test   = 2.40 A


For:

    CT = 1000 / 5 A
    In = 5 A

    Pickup = 1.20 xIn
           = 6.00 A

    Test = 2.40 xIn
         = 12.00 A

The protection calculations themselves use xIn values.
The CT configuration is used only when conversion to/from
physical secondary current is required.
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

        expected = (
            ProtectionCalculator
            ._validate_number(
                expected,
                "Expected value"
            )
        )

        actual = (
            ProtectionCalculator
            ._validate_number(
                actual,
                "Actual value"
            )
        )

        if expected == 0:

            raise ZeroDivisionError(
                "Expected value cannot be zero."
            )

        return (
            (
                actual
                -
                expected
            )
            /
            abs(expected)
        ) * 100.0

    @staticmethod
    def _within_tolerance(
        expected,
        actual,
        tolerance_percent
    ):

        expected = (
            ProtectionCalculator
            ._validate_number(
                expected,
                "Expected value"
            )
        )

        actual = (
            ProtectionCalculator
            ._validate_number(
                actual,
                "Actual value"
            )
        )

        tolerance_percent = (
            ProtectionCalculator
            ._validate_number(
                tolerance_percent,
                "Tolerance"
            )
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
            *
            (
                1.0
                -
                tolerance_percent / 100.0
            )
        )

        upper = (
            expected
            *
            (
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
    # CT CONFIGURATION
    # =========================================================

    @staticmethod
    def validate_ct_ratio(
        ct_primary,
        ct_secondary
    ):
        """
        Validate CT primary and secondary ratings.

        Example:

            1000 / 1
            1000 / 5
        """

        ct_primary = (
            ProtectionCalculator
            ._validate_number(
                ct_primary,
                "CT primary"
            )
        )

        ct_secondary = (
            ProtectionCalculator
            ._validate_number(
                ct_secondary,
                "CT secondary"
            )
        )

        if ct_primary <= 0:

            raise ValueError(
                "CT primary must be greater than zero."
            )

        if ct_secondary <= 0:

            raise ValueError(
                "CT secondary must be greater than zero."
            )

        return {
            "ct_primary": ct_primary,
            "ct_secondary": ct_secondary,
        }

    @staticmethod
    def calculate_ct_ratio(
        ct_primary,
        ct_secondary
    ):
        """
        Calculate CT ratio.

        Example:

            1000 / 1
            ratio = 1000

        or:

            1000 / 5
            ratio = 200
        """

        ct = (
            ProtectionCalculator
            .validate_ct_ratio(
                ct_primary,
                ct_secondary
            )
        )

        return (
            ct["ct_primary"]
            /
            ct["ct_secondary"]
        )

    @staticmethod
    def xin_to_secondary_current(
        xin,
        ct_secondary
    ):
        """
        Convert xIn into actual secondary injection current.

        Example:

            2.5 xIn
            CT secondary = 1 A

            Actual = 2.5 A
        """

        xin = (
            ProtectionCalculator
            ._validate_number(
                xin,
                "Current in xIn"
            )
        )

        ct_secondary = (
            ProtectionCalculator
            ._validate_number(
                ct_secondary,
                "CT secondary"
            )
        )

        if ct_secondary <= 0:

            raise ValueError(
                "CT secondary must be greater than zero."
            )

        return (
            xin
            *
            ct_secondary
        )

    @staticmethod
    def secondary_current_to_xin(
        secondary_current,
        ct_secondary
    ):
        """
        Convert actual secondary injection current to xIn.

        Example:

            Secondary injection = 2.5 A
            CT secondary = 1 A

            = 2.5 xIn
        """

        secondary_current = (
            ProtectionCalculator
            ._validate_number(
                secondary_current,
                "Secondary current"
            )
        )

        ct_secondary = (
            ProtectionCalculator
            ._validate_number(
                ct_secondary,
                "CT secondary"
            )
        )

        if ct_secondary <= 0:

            raise ValueError(
                "CT secondary must be greater than zero."
            )

        return (
            secondary_current
            /
            ct_secondary
        )

    # =========================================================
    # 50 / 50N / 46
    # =========================================================

    @staticmethod
    def evaluate_current_pickup(
        expected_xin,
        actual_xin,
        tolerance_percent=5.0
    ):
        """
        Evaluate instantaneous / current pickup.

        All current values are represented as xIn.

        Example:

            Expected = 1.20 xIn
            Actual   = 1.24 xIn
            Tolerance = 5 %

        No CT primary/secondary conversion is required for
        the protection calculation itself.
        """

        expected_xin = (
            ProtectionCalculator
            ._validate_number(
                expected_xin,
                "Expected pickup"
            )
        )

        actual_xin = (
            ProtectionCalculator
            ._validate_number(
                actual_xin,
                "Actual pickup"
            )
        )

        tolerance_percent = (
            ProtectionCalculator
            ._validate_number(
                tolerance_percent,
                "Tolerance"
            )
        )

        if expected_xin <= 0:

            raise ValueError(
                "Expected pickup must be greater than zero."
            )

        error_percent = (
            ProtectionCalculator
            ._percentage_error(
                expected_xin,
                actual_xin
            )
        )

        passed = (
            ProtectionCalculator
            ._within_tolerance(
                expected_xin,
                actual_xin,
                tolerance_percent
            )
        )

        return {

            "expected_xin":
                expected_xin,

            "actual_xin":
                actual_xin,

            "error_percent":
                error_percent,

            "tolerance_percent":
                tolerance_percent,

            "result":
                (
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
        pickup_xin,
        test_xin
    ):
        """
        Calculate Plug Setting Multiplier.

            PSM = Test / Pickup

        Both quantities are xIn.

        Example:

            Pickup = 1.20 xIn
            Test   = 2.40 xIn

            PSM = 2.0
        """

        pickup_xin = (
            ProtectionCalculator
            ._validate_number(
                pickup_xin,
                "Pickup xIn"
            )
        )

        test_xin = (
            ProtectionCalculator
            ._validate_number(
                test_xin,
                "Test xIn"
            )
        )

        if pickup_xin <= 0:

            raise ValueError(
                "Pickup xIn must be greater than zero."
            )

        return (
            test_xin
            /
            pickup_xin
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
            .replace(
                "_",
                " "
            )
            .replace(
                "-",
                " "
            )
        )

        return " ".join(
            text.split()
        )

    @staticmethod
    def calculate_51_time(
        curve_code,
        pickup_xin,
        test_xin,
        tms
    ):
        """
        Calculate IEC IDMT operating time.

        Current quantities are xIn.

        Formula:

            t = TMS × K /
                ((PSM ^ alpha) - 1)

        Supported curves:

            IEC Standard / Normal Inverse
            IEC Very Inverse
            IEC Extremely Inverse
            IEC Long Time Inverse
        """

        pickup_xin = (
            ProtectionCalculator
            ._validate_number(
                pickup_xin,
                "Pickup xIn"
            )
        )

        test_xin = (
            ProtectionCalculator
            ._validate_number(
                test_xin,
                "Test xIn"
            )
        )

        tms = (
            ProtectionCalculator
            ._validate_number(
                tms,
                "TMS"
            )
        )

        if pickup_xin <= 0:

            raise ValueError(
                "Pickup xIn must be greater than zero."
            )

        if test_xin <= 0:

            raise ValueError(
                "Test xIn must be greater than zero."
            )

        if tms <= 0:

            raise ValueError(
                "TMS must be greater than zero."
            )

        psm = (
            ProtectionCalculator
            .calculate_psm(
                pickup_xin,
                test_xin
            )
        )

        if psm <= 1.0:

            raise ValueError(
                "PSM must be greater than 1.0 "
                "for IDMT calculation."
            )

        curve = (
            ProtectionCalculator
            ._normalise_curve_name(
                curve_code
            )
        )

        # -------------------------------------------------
        # IEC CURVE CONSTANTS
        # -------------------------------------------------

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

            # IEC Normal / Standard Inverse
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

            "pickup_xin":
                pickup_xin,

            "test_xin":
                test_xin,

            "psm":
                psm,

            "expected_time":
                expected_time,

            "curve":
                curve_code,

            "tms":
                tms,
        }

    @staticmethod
    def evaluate_time_test(
        expected_time,
        actual_time,
        tolerance_percent=5.0
    ):

        expected_time = (
            ProtectionCalculator
            ._validate_number(
                expected_time,
                "Expected time"
            )
        )

        actual_time = (
            ProtectionCalculator
            ._validate_number(
                actual_time,
                "Actual time"
            )
        )

        tolerance_percent = (
            ProtectionCalculator
            ._validate_number(
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

        if tolerance_percent < 0:

            raise ValueError(
                "Tolerance cannot be negative."
            )

        error_percent = (
            ProtectionCalculator
            ._percentage_error(
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

            "expected_time":
                expected_time,

            "actual_time":
                actual_time,

            "error_percent":
                error_percent,

            "lower_limit":
                lower_limit,

            "upper_limit":
                upper_limit,

            "tolerance_percent":
                tolerance_percent,

            "result":
                (
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

        expected_value = (
            ProtectionCalculator
            ._validate_number(
                expected_value,
                "Expected value"
            )
        )

        actual_value = (
            ProtectionCalculator
            ._validate_number(
                actual_value,
                "Actual value"
            )
        )

        tolerance_percent = (
            ProtectionCalculator
            ._validate_number(
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
            ProtectionCalculator
            ._percentage_error(
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

        passed = (
            lower_limit
            <= actual_value
            <= upper_limit
        )

        return {

            "expected_value":
                expected_value,

            "actual_value":
                actual_value,

            "error_percent":
                error_percent,

            "lower_limit":
                lower_limit,

            "upper_limit":
                upper_limit,

            "direction":
                direction,

            "result":
                (
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
            ProtectionCalculator
            ._validate_number(
                expected_frequency,
                "Expected frequency"
            )
        )

        actual_frequency = (
            ProtectionCalculator
            ._validate_number(
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

            "expected_frequency":
                expected_frequency,

            "actual_frequency":
                actual_frequency,

            "error_percent":
                result["error_percent"],

            "lower_limit":
                result["lower_limit"],

            "upper_limit":
                result["upper_limit"],

            "result":
                result["result"],
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
            ProtectionCalculator
            ._validate_number(
                frequency_1,
                "Frequency before"
            )
        )

        frequency_2 = (
            ProtectionCalculator
            ._validate_number(
                frequency_2,
                "Frequency after"
            )
        )

        time_interval = (
            ProtectionCalculator
            ._validate_number(
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
            ProtectionCalculator
            ._validate_number(
                expected_rocof,
                "Expected ROCOF"
            )
        )

        actual_rocof = (
            ProtectionCalculator
            ._validate_number(
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
            ProtectionCalculator
            ._validate_number(
                tolerance_percent,
                "Tolerance"
            )
        )

        if tolerance_percent < 0:

            raise ValueError(
                "Tolerance cannot be negative."
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

            "expected_rocof":
                expected_rocof,

            "actual_rocof":
                actual_rocof,

            "error_percent":
                error_percent,

            "lower_limit":
                lower,

            "upper_limit":
                upper,

            "result":
                (
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
            ProtectionCalculator
            ._validate_number(
                expected_angle,
                "Expected angle"
            )
        )

        actual_angle = (
            ProtectionCalculator
            ._validate_number(
                actual_angle,
                "Actual angle"
            )
        )

        angle_tolerance = (
            ProtectionCalculator
            ._validate_number(
                angle_tolerance,
                "Angle tolerance"
            )
        )

        if angle_tolerance < 0:

            raise ValueError(
                "Angle tolerance cannot be negative."
            )

        angle_error = (
            ProtectionCalculator
            ._angle_difference(
                expected_angle,
                actual_angle
            )
        )

        passed = (
            abs(angle_error)
            <= angle_tolerance
        )

        return {

            "expected_angle":
                expected_angle,

            "actual_angle":
                actual_angle,

            "angle_error":
                angle_error,

            "angle_tolerance":
                angle_tolerance,

            "result":
                (
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

            "expected_operation":
                expected,

            "observed_operation":
                observed,

            "result":
                (
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
        current_1_xin,
        current_2_xin
    ):
        """
        Basic differential calculation using xIn.

            Idiff = |I1 - I2|

        Both currents must use the same nominal-current
        reference.
        """

        current_1_xin = (
            ProtectionCalculator
            ._validate_number(
                current_1_xin,
                "Current 1 xIn"
            )
        )

        current_2_xin = (
            ProtectionCalculator
            ._validate_number(
                current_2_xin,
                "Current 2 xIn"
            )
        )

        return abs(
            current_1_xin
            -
            current_2_xin
        )

    @staticmethod
    def evaluate_differential_test(
        expected_xin,
        actual_differential_xin,
        tolerance_percent=5.0
    ):

        expected_xin = (
            ProtectionCalculator
            ._validate_number(
                expected_xin,
                "Expected differential xIn"
            )
        )

        actual_differential_xin = (
            ProtectionCalculator
            ._validate_number(
                actual_differential_xin,
                "Actual differential xIn"
            )
        )

        tolerance_percent = (
            ProtectionCalculator
            ._validate_number(
                tolerance_percent,
                "Tolerance"
            )
        )

        result = (
            ProtectionCalculator
            .evaluate_threshold(
                expected_value=expected_xin,
                actual_value=actual_differential_xin,
                tolerance_percent=tolerance_percent,
                direction="equal"
            )
        )

        return {

            "expected_xin":
                expected_xin,

            "actual_differential_xin":
                actual_differential_xin,

            "error_percent":
                result["error_percent"],

            "tolerance_percent":
                tolerance_percent,

            "result":
                result["result"],
        }