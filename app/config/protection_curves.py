# app/config/protection_curves.py


PROTECTION_CURVES = {

    "51": {

        "IEC-NI": {
            "name": "IEC Normal Inverse"
        },

        "IEC-VI": {
            "name": "IEC Very Inverse"
        },

        "IEC-EI": {
            "name": "IEC Extremely Inverse"
        },

        "DT": {
            "name": "Definite Time"
        }
    },

    "51N": {

        "IEC-NI": {
            "name": "IEC Normal Inverse"
        },

        "IEC-VI": {
            "name": "IEC Very Inverse"
        },

        "IEC-EI": {
            "name": "IEC Extremely Inverse"
        },

        "DT": {
            "name": "Definite Time"
        }
    }
}


def get_curves(
    protection_function
):

    return PROTECTION_CURVES.get(
        protection_function,
        {}
    )


def get_available_curves():

    curves = set()

    for protection_curves in (
        PROTECTION_CURVES.values()
    ):

        curves.update(
            protection_curves.keys()
        )

    return sorted(
        curves
    )
