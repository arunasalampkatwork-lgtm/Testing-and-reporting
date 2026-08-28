from app.models.thermal_template import (
    ThermalTemplate,
    ThermalCurvePoint,
)


THERMAL_TEMPLATES = {

    # =====================================================
    # EXAMPLE
    # =====================================================

    "SIEMENS_7SJ80_49": ThermalTemplate(

        template_id="THERMAL-SIEMENS-7SJ80",

        protection_function="49",

        manufacturer="Siemens",

        model="7SJ80",

        name=(
            "Siemens 7SJ80 - Thermal Overload"
        ),

        curve_type="point",

        rated_current=1.0,

        thermal_constant=10.0,

        pickup_current=1.05,

        curves=[

            ThermalCurvePoint(
                current_multiple=1.05,
                operating_time=10000.0
            ),

            ThermalCurvePoint(
                current_multiple=1.10,
                operating_time=5000.0
            ),

            ThermalCurvePoint(
                current_multiple=1.20,
                operating_time=2500.0
            ),

            ThermalCurvePoint(
                current_multiple=1.50,
                operating_time=900.0
            ),

            ThermalCurvePoint(
                current_multiple=2.00,
                operating_time=400.0
            ),

        ],

        notes=(
            "Example template. "
            "Replace curve points with values "
            "from the relay manufacturer's documentation."
        ),
    ),
}


def get_thermal_templates():

    return THERMAL_TEMPLATES.copy()


def get_thermal_template(
    manufacturer,
    model,
):

    manufacturer = (
        str(manufacturer or "")
        .strip()
        .upper()
    )

    model = (
        str(model or "")
        .strip()
        .upper()
    )

    for template in THERMAL_TEMPLATES.values():

        if (
            template.manufacturer.upper()
            ==
            manufacturer
            and
            template.model.upper()
            ==
            model
        ):

            return template

    return None


def get_thermal_templates_for_function(
    protection_function
):

    protection_function = str(
        protection_function or ""
    ).strip().upper()

    return [

        template

        for template in THERMAL_TEMPLATES.values()

        if (
            template.protection_function.upper()
            ==
            protection_function
        )
    ]


def get_available_manufacturers():

    return sorted(
        set(
            template.manufacturer

            for template in THERMAL_TEMPLATES.values()
        )
    )


def get_models_for_manufacturer(
    manufacturer
):

    manufacturer = str(
        manufacturer or ""
    ).strip().upper()

    return sorted(
        set(

            template.model

            for template in THERMAL_TEMPLATES.values()

            if (
                template.manufacturer.upper()
                ==
                manufacturer
            )

        )
    )