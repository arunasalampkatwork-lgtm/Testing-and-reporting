"""
Protection function configuration.

This file defines:
    - protection code
    - display name
    - test type
    - description

The UI uses the test_type to determine which testing template
should be displayed.
"""

PROTECTION_FUNCTIONS = {

    # =========================================================
    # OVERCURRENT
    # =========================================================

    "50": {
        "name": "Instantaneous Overcurrent",
        "test_type": "current_pickup_time",
        "description": (
            "Instantaneous phase overcurrent protection."
        ),
    },

    "51": {
        "name": "Time Overcurrent",
        "test_type": "idmt",
        "description": (
            "Inverse definite minimum time overcurrent protection."
        ),
    },

    "50N": {
        "name": "Instantaneous Earth Fault",
        "test_type": "current_pickup_time",
        "description": (
            "Instantaneous earth fault overcurrent protection."
        ),
    },

    "51N": {
        "name": "Time Earth Fault",
        "test_type": "idmt",
        "description": (
            "Inverse definite minimum time earth fault protection."
        ),
    },

    "46": {
        "name": "Negative Sequence Overcurrent",
        "test_type": "current_pickup_time",
        "description": (
            "Negative sequence overcurrent protection."
        ),
    },

    # =========================================================
    # VOLTAGE
    # =========================================================

    "27": {
        "name": "Undervoltage",
        "test_type": "voltage_threshold",
        "description": (
            "Under-voltage protection."
        ),
    },

    "59": {
        "name": "Overvoltage",
        "test_type": "voltage_threshold",
        "description": (
            "Over-voltage protection."
        ),
    },

    # =========================================================
    # FREQUENCY
    # =========================================================

    "81U": {
        "name": "Underfrequency",
        "test_type": "frequency_threshold",
        "description": (
            "Under-frequency protection."
        ),
    },

    "81O": {
        "name": "Overfrequency",
        "test_type": "frequency_threshold",
        "description": (
            "Over-frequency protection."
        ),
    },

    "81R": {
        "name": "Rate of Change of Frequency",
        "test_type": "rocof",
        "description": (
            "Rate of change of frequency protection."
        ),
    },

    # =========================================================
    # DIRECTIONAL
    # =========================================================

    "67": {
        "name": "Directional Overcurrent",
        "test_type": "directional_current",
        "description": (
            "Directional phase overcurrent protection."
        ),
    },

    "67N": {
        "name": "Directional Earth Fault",
        "test_type": "directional_current",
        "description": (
            "Directional earth fault protection."
        ),
    },

    # =========================================================
    # DIFFERENTIAL
    # =========================================================

    "87": {
        "name": "Differential Protection",
        "test_type": "differential",
        "description": (
            "Differential protection."
        ),
    },

    "87T": {
        "name": "Transformer Differential",
        "test_type": "differential",
        "description": (
            "Transformer differential protection."
        ),
    },

    "87M": {
        "name": "Motor Differential",
        "test_type": "differential",
        "description": (
            "Motor differential protection."
        ),
    },

    # =========================================================
    # GENERIC FUNCTIONAL
    # =========================================================

    "50BF": {
        "name": "Breaker Failure",
        "test_type": "functional",
        "description": (
            "Breaker failure protection."
        ),
    },

    "86": {
        "name": "Lockout",
        "test_type": "functional",
        "description": (
            "Master trip / lockout function."
        ),
    },

}


# =============================================================
# ALIASES
# =============================================================

PROTECTION_ALIASES = {

    "50": "50",
    "50 INST": "50",
    "50 INSTANTANEOUS OVERCURRENT": "50",

    "51": "51",
    "51 TIME OVERCURRENT": "51",

    "50N": "50N",
    "50N INSTANTANEOUS EARTH FAULT": "50N",

    "51N": "51N",
    "51N TIME EARTH FAULT": "51N",

    "27": "27",
    "27 UNDERVOLTAGE": "27",

    "59": "59",
    "59 OVERVOLTAGE": "59",

    "46": "46",
    "46 NEGATIVE SEQUENCE OVERCURRENT": "46",

    "67": "67",
    "67 DIRECTIONAL OVERCURRENT": "67",

    "67N": "67N",
    "67N DIRECTIONAL EARTH FAULT": "67N",

    "81U": "81U",
    "81 UNDERFREQUENCY": "81U",

    "81O": "81O",
    "81 OVERFREQUENCY": "81O",

    "81R": "81R",
    "ROCOF": "81R",

    "87": "87",
    "87 DIFFERENTIAL": "87",

    "87T": "87T",
    "87 TRANSFORMER DIFFERENTIAL": "87T",

    "87M": "87M",
    "87 MOTOR DIFFERENTIAL": "87M",

    "50BF": "50BF",
    "86": "86",
}


# =============================================================
# FUNCTIONS
# =============================================================

def normalize_protection_code(protection_code):
    """
    Convert a protection-function display name or code into
    the canonical protection code.
    """

    if protection_code is None:
        return None

    text = str(
        protection_code
    ).strip()

    if not text:
        return None

    upper = text.upper()

    if upper in PROTECTION_FUNCTIONS:
        return upper

    if upper in PROTECTION_ALIASES:
        return PROTECTION_ALIASES[upper]

    # Match the beginning of strings such as:
    # "51 Time Overcurrent"
    for code in PROTECTION_FUNCTIONS.keys():

        if upper.startswith(
            code.upper() + " "
        ):

            return code

    return upper


def get_protection_function(
    protection_code
):
    """
    Return configuration for a protection function.
    """

    code = normalize_protection_code(
        protection_code
    )

    return PROTECTION_FUNCTIONS.get(
        code
    )


def get_protection_test_type(
    protection_code
):
    """
    Return the test type for a protection function.
    """

    function = get_protection_function(
        protection_code
    )

    if function is None:
        return None

    return function.get(
        "test_type"
    )


def get_all_protection_functions():
    """
    Return all configured protection functions.
    """

    return PROTECTION_FUNCTIONS.copy()


def get_protection_codes():
    """
    Return all canonical protection codes.
    """

    return list(
        PROTECTION_FUNCTIONS.keys()
    )