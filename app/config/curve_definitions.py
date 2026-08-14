CURVE_DEFINITIONS = {

    "IEC-NI": {
        "name": "IEC Normal Inverse",
        "type": "IEC_INVERSE",
        "k": 0.14,
        "alpha": 0.02
    },

    "IEC-VI": {
        "name": "IEC Very Inverse",
        "type": "IEC_INVERSE",
        "k": 13.5,
        "alpha": 1.0
    },

    "IEC-EI": {
        "name": "IEC Extremely Inverse",
        "type": "IEC_INVERSE",
        "k": 80.0,
        "alpha": 2.0
    },

    "DT": {
        "name": "Definite Time",
        "type": "DEFINITE_TIME",
        "k": None,
        "alpha": None
    }
}


def get_curve(curve_code):

    return CURVE_DEFINITIONS.get(
        curve_code
    )


def get_available_curves():

    return list(
        CURVE_DEFINITIONS.keys()
    )