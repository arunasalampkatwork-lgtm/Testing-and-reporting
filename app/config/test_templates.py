from app.models.test_template import (
    TestTemplate,
    TestField
)


TEST_TEMPLATES = {

    # =====================================================
    # 50 - INSTANTANEOUS OVERCURRENT
    # =====================================================

    "50": TestTemplate(

        template_id="TPL-50",

        protection_function="50",

        name="50 - Instantaneous Overcurrent",

        fields=[

            TestField(
                field_id="pickup_current",
                label="Pickup Current Setting",
                field_type="number",
                unit="A",
                required=True
            ),

            TestField(
                field_id="test_current",
                label="Test Current",
                field_type="number",
                unit="A",
                required=True
            ),

            TestField(
                field_id="expected_result",
                label="Expected Result",
                field_type="text"
            ),

            TestField(
                field_id="actual_result",
                label="Actual Result",
                field_type="select"
            ),

            TestField(
                field_id="result",
                label="Result",
                field_type="text"
            )
        ]
    ),


    # =====================================================
    # 50N - INSTANTANEOUS EARTH FAULT
    # =====================================================

    "50N": TestTemplate(

        template_id="TPL-50N",

        protection_function="50N",

        name="50N - Instantaneous Earth Fault",

        fields=[

            TestField(
                field_id="pickup_current",
                label="Pickup Current Setting",
                field_type="number",
                unit="A",
                required=True
            ),

            TestField(
                field_id="test_current",
                label="Test Current",
                field_type="number",
                unit="A",
                required=True
            ),

            TestField(
                field_id="expected_result",
                label="Expected Result",
                field_type="text"
            ),

            TestField(
                field_id="actual_result",
                label="Actual Result",
                field_type="select"
            ),

            TestField(
                field_id="result",
                label="Result",
                field_type="text"
            )
        ]
    ),


    # =====================================================
    # 51 - TIME OVERCURRENT
    # =====================================================

    "51": TestTemplate(

        template_id="TPL-51",

        protection_function="51",

        name="51 - Time Overcurrent",

        fields=[

            TestField(
                field_id="pickup_current",
                label="Pickup Current",
                field_type="number",
                unit="A",
                required=True
            ),

            TestField(
                field_id="test_current",
                label="Test Current",
                field_type="number",
                unit="A",
                required=True
            ),

            TestField(
                field_id="curve",
                label="Curve",
                field_type="curve",
                required=True
            ),

            TestField(
                field_id="tms",
                label="Time Multiplier Setting",
                field_type="number",
                required=True
            ),

            TestField(
                field_id="psm",
                label="PSM",
                field_type="number"
            ),

            TestField(
                field_id="expected_time",
                label="Expected Operating Time",
                field_type="number",
                unit="s"
            ),

            TestField(
                field_id="actual_time",
                label="Actual Operating Time",
                field_type="number",
                unit="s",
                required=True
            ),

            TestField(
                field_id="error_percent",
                label="Error",
                field_type="number",
                unit="%"
            ),

            TestField(
                field_id="result",
                label="Result",
                field_type="text"
            )
        ]
    ),


    # =====================================================
    # 51N - TIME EARTH FAULT
    # =====================================================

    "51N": TestTemplate(

        template_id="TPL-51N",

        protection_function="51N",

        name="51N - Time Earth Fault",

        fields=[

            TestField(
                field_id="pickup_current",
                label="Pickup Current",
                field_type="number",
                unit="A",
                required=True
            ),

            TestField(
                field_id="test_current",
                label="Test Current",
                field_type="number",
                unit="A",
                required=True
            ),

            TestField(
                field_id="curve",
                label="Curve",
                field_type="curve",
                required=True
            ),

            TestField(
                field_id="tms",
                label="Time Multiplier Setting",
                field_type="number",
                required=True
            ),

            TestField(
                field_id="psm",
                label="PSM",
                field_type="number"
            ),

            TestField(
                field_id="expected_time",
                label="Expected Operating Time",
                field_type="number",
                unit="s"
            ),

            TestField(
                field_id="actual_time",
                label="Actual Operating Time",
                field_type="number",
                unit="s",
                required=True
            ),

            TestField(
                field_id="error_percent",
                label="Error",
                field_type="number",
                unit="%"
            ),

            TestField(
                field_id="result",
                label="Result",
                field_type="text"
            )
        ]
    ),


    # =====================================================
    # 27 - UNDERVOLTAGE
    # =====================================================

    "27": TestTemplate(

        template_id="TPL-27",

        protection_function="27",

        name="27 - Undervoltage",

        fields=[

            TestField(
                field_id="pickup_voltage",
                label="Pickup Voltage Setting",
                field_type="number",
                unit="V",
                required=True
            ),

            TestField(
                field_id="test_voltage",
                label="Test Voltage",
                field_type="number",
                unit="V",
                required=True
            ),

            TestField(
                field_id="expected_result",
                label="Expected Result",
                field_type="text"
            ),

            TestField(
                field_id="actual_result",
                label="Actual Result",
                field_type="select"
            ),

            TestField(
                field_id="result",
                label="Result",
                field_type="text"
            )
        ]
    ),


    # =====================================================
    # 59 - OVERVOLTAGE
    # =====================================================

    "59": TestTemplate(

        template_id="TPL-59",

        protection_function="59",

        name="59 - Overvoltage",

        fields=[

            TestField(
                field_id="pickup_voltage",
                label="Pickup Voltage Setting",
                field_type="number",
                unit="V",
                required=True
            ),

            TestField(
                field_id="test_voltage",
                label="Test Voltage",
                field_type="number",
                unit="V",
                required=True
            ),

            TestField(
                field_id="expected_result",
                label="Expected Result",
                field_type="text"
            ),

            TestField(
                field_id="actual_result",
                label="Actual Result",
                field_type="select"
            ),

            TestField(
                field_id="result",
                label="Result",
                field_type="text"
            )
        ]
    ),


    # =====================================================
    # 87 - DIFFERENTIAL
    # =====================================================

    "87": TestTemplate(

        template_id="TPL-87",

        protection_function="87",

        name="87 - Differential Protection",

        fields=[

            TestField(
                field_id="pickup_current",
                label="Differential Pickup Setting",
                field_type="number",
                unit="A",
                required=True
            ),

            TestField(
                field_id="test_current",
                label="Differential Test Current",
                field_type="number",
                unit="A",
                required=True
            ),

            TestField(
                field_id="expected_result",
                label="Expected Result",
                field_type="text"
            ),

            TestField(
                field_id="actual_result",
                label="Actual Result",
                field_type="select"
            ),

            TestField(
                field_id="result",
                label="Result",
                field_type="text"
            )
        ]
    )
}