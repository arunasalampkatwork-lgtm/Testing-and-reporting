from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

from PySide6.QtWidgets import (
    QFileDialog,
    QMessageBox,
)


class PanelReportService:

    def __init__(
        self,
        project_folder
    ):

        self.project_folder = Path(
            project_folder
        )

    # =====================================================
    # GENERATE PANEL REPORT
    # =====================================================

    def generate_report(
        self,
        panel,
        components,
        protection_tests,
        component_tests,
        report_date=None,
        substation_name="",
        switchboard_name="",
        parent=None
    ):

        panel_name = getattr(
            panel,
            "name",
            "Panel"
        )

        # =================================================
        # REPORT FILE NAME
        #
        # Include the complete electrical hierarchy so the
        # report remains identifiable even outside the
        # application.
        #
        # Example:
        #
        # REF-III SS-2 - HV-203A - P-03 -
        # Test Report - 2026-08-15.docx
        # =================================================

        filename_parts = [
            substation_name,
            switchboard_name,
            panel_name,
            "Test Report",
            str(report_date),
        ]

        filename_parts = [
            str(value).strip()
            for value in filename_parts
            if value is not None
            and str(value).strip()
        ]

        report_filename = (
            " - ".join(
                filename_parts
            )
            + ".docx"
        )

        default_path = (
            self.project_folder
            /
            "reports"
            /
            report_filename
        )

        output_path, _ = (
            QFileDialog.getSaveFileName(

                parent,

                "Save Panel Test Report",

                str(
                    default_path
                ),

                "Word Document (*.docx)"
            )
        )

        if not output_path:

            return

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        document = Document()

        self.configure_document(
            document
        )

        # =================================================
        # TITLE
        # =================================================

        self.add_title(
            document,
            "PANEL TEST REPORT"
        )

        # =================================================
        # PANEL DETAILS
        # =================================================

        self.add_heading(
            document,
            "PANEL DETAILS"
        )

        # =================================================
        # LOCATION / IDENTIFICATION
        # =================================================

        # The report explicitly records the electrical
        # hierarchy so that a report remains identifiable
        # even when separated from the project database.
        self.add_table(
            document,
            [

                (
                    "Substation",
                    substation_name
                ),

                (
                    "Switchboard",
                    switchboard_name
                ),

                (
                    "Panel No.",
                    panel_name
                ),

                (
                    "Test Date",
                    report_date
                ),

                (
                    "Feed Equipment",
                    getattr(
                        panel,
                        "equipment_name",
                        ""
                    )
                ),

                (
                    "Equipment Type",
                    getattr(
                        panel,
                        "equipment_type",
                        ""
                    )
                ),

                (
                    "Number of CTs",
                    getattr(
                        panel,
                        "ct_count",
                        ""
                    )
                ),

                (
                    "Numerical Relays",
                    getattr(
                        panel,
                        "relay_count",
                        ""
                    )
                ),

                (
                    "Auxiliary Relays",
                    getattr(
                        panel,
                        "aux_count",
                        ""
                    )
                ),
            ]
        )

        # =================================================
        # INSTALLED COMPONENTS
        # =================================================

        self.add_heading(
            document,
            "INSTALLED TEST COMPONENTS"
        )

        table = document.add_table(
            rows=1,
            cols=5
        )

        table.style = "Table Grid"

        headers = [

            "Component",

            "Type",

            "Manufacturer",

            "Model",

            "Serial Number",
        ]

        for index, header in enumerate(
            headers
        ):

            table.rows[0].cells[
                index
            ].text = header

        for component in (
            components or []
        ):

            cells = (
                table.add_row()
                .cells
            )

            values = [

                getattr(
                    component,
                    "name",
                    ""
                ),

                getattr(
                    component,
                    "component_type",
                    ""
                ),

                getattr(
                    component,
                    "manufacturer",
                    ""
                ),

                getattr(
                    component,
                    "model",
                    ""
                ),

                getattr(
                    component,
                    "serial_number",
                    ""
                ),
            ]

            for index, value in enumerate(
                values
            ):

                cells[index].text = (
                    str(
                        value or ""
                    )
                )

        # =================================================
        # TEST SUMMARY
        # =================================================

        self.add_heading(
            document,
            "TEST SUMMARY"
        )

        summary_table = document.add_table(
            rows=1,
            cols=5
        )

        summary_table.style = (
            "Table Grid"
        )

        headers = [

            "Test ID",

            "Date",

            "Component",

            "Test Type",

            "Result",
        ]

        for index, header in enumerate(
            headers
        ):

            summary_table.rows[
                0
            ].cells[
                index
            ].text = header

        component_names = {

            getattr(
                component,
                "component_id",
                ""
            ):
                getattr(
                    component,
                    "name",
                    ""
                )

            for component in (
                components or []
            )
        }

        # -------------------------------------------------
        # COMPONENT TESTS
        # -------------------------------------------------

        for test in (
            component_tests or []
        ):

            cells = (
                summary_table
                .add_row()
                .cells
            )

            values = [

                test.get(
                    "test_id",
                    ""
                ),

                test.get(
                    "test_date",
                    ""
                ),

                component_names.get(
                    test.get(
                        "component_id",
                        ""
                    ),

                    test.get(
                        "component_id",
                        ""
                    )
                ),

                test.get(
                    "test_type",
                    ""
                ),

                test.get(
                    "result",
                    ""
                ),
            ]

            for index, value in enumerate(
                values
            ):

                cells[index].text = (
                    str(
                        value or ""
                    )
                )

        # -------------------------------------------------
        # PROTECTION TESTS
        # -------------------------------------------------

        for test in (
            protection_tests or []
        ):

            cells = (
                summary_table
                .add_row()
                .cells
            )

            values = [

                test.get(
                    "test_id",
                    ""
                ),

                test.get(
                    "test_date",
                    ""
                ),

                component_names.get(
                    test.get(
                        "relay_id",
                        ""
                    ),

                    test.get(
                        "relay_id",
                        ""
                    )
                ),

                test.get(
                    "protection_code",
                    ""
                ),

                test.get(
                    "result",
                    ""
                ),
            ]

            for index, value in enumerate(
                values
            ):

                cells[index].text = (
                    str(
                        value or ""
                    )
                )

        # =================================================
        # DETAILED COMPONENT TEST RESULTS
        # =================================================

        if component_tests:

            self.add_heading(
                document,
                "COMPONENT TEST DETAILS"
            )

            for test in component_tests:

                component_name = (
                    component_names.get(
                        test.get(
                            "component_id",
                            ""
                        ),

                        test.get(
                            "component_id",
                            ""
                        )
                    )
                )

                test_type = test.get(
                    "test_type",
                    ""
                )

                self.add_heading(
                    document,
                    (
                        f"{component_name}"
                        +
                        (
                            f" - {test_type}"
                            if test_type
                            else ""
                        )
                    )
                )

                measurements = (
                    test.get(
                        "measurements",
                        {}
                    )
                    or
                    {}
                )

                # -------------------------------------------------
                # NORMAL FIELDS
                # -------------------------------------------------

                rows = []

                for key, value in (
                    measurements.items()
                ):

                    # ---------------------------------------------
                    # Skip nested phase data here.
                    # CT phase data is handled separately below.
                    # ---------------------------------------------

                    if key == "phase_tests":

                        continue

                    # ---------------------------------------------
                    # Skip null / empty values
                    # ---------------------------------------------

                    if self.is_empty_value(
                        value
                    ):

                        continue

                    # ---------------------------------------------
                    # Skip dictionaries/lists
                    # ---------------------------------------------

                    if isinstance(
                        value,
                        (dict, list, tuple)
                    ):

                        continue

                    rows.append(
                        (
                            key.replace(
                                "_",
                                " "
                            ).title(),

                            value
                        )
                    )

                if rows:

                    self.add_table(
                        document,
                        rows
                    )

                # -------------------------------------------------
                # CT THREE-PHASE DATA
                # -------------------------------------------------

                phase_tests = measurements.get(
                    "phase_tests"
                )

                if phase_tests:

                    self.add_heading(
                        document,
                        "PHASE-WISE CT TEST RESULTS"
                    )

                    self.add_phase_test_table(
                        document,
                        phase_tests
                    )

                # -------------------------------------------------
                # RESULT
                # -------------------------------------------------

                result = test.get(
                    "result"
                )

                if not self.is_empty_value(
                    result
                ):

                    self.add_result(
                        document,
                        result
                    )

                # -------------------------------------------------
                # REMARKS
                # -------------------------------------------------

                remarks = test.get(
                    "remarks"
                )

                if not self.is_empty_value(
                    remarks
                ):

                    document.add_paragraph(
                        (
                            "Remarks: "
                            +
                            str(
                                remarks
                            )
                        )
                    )
        # =================================================
        # PROTECTION TEST DETAILS
        # =================================================

        if protection_tests:

            self.add_heading(
                document,
                "PROTECTION TEST DETAILS"
            )

            for test in protection_tests:

                relay_name = (
                    component_names.get(
                        test.get(
                            "relay_id",
                            ""
                        ),

                        test.get(
                            "relay_id",
                            ""
                        )
                    )
                )

                protection_code = test.get(
                    "protection_code",
                    ""
                )

                heading = (
                    f"{relay_name}"
                    +
                    (
                        f" - {protection_code}"
                        if protection_code
                        else ""
                    )
                )

                self.add_heading(
                    document,
                    heading
                )

                measurements = (
                    test.get(
                        "measurements",
                        {}
                    )
                    or
                    {}
                )

                rows = []

                for key, value in (
                    measurements.items()
                ):

                    # -------------------------------------------------
                    # OMIT EMPTY VALUES
                    # -------------------------------------------------

                    if self.is_empty_value(
                        value
                    ):

                        continue

                    # -------------------------------------------------
                    # OMIT COMPLEX NESTED STRUCTURES
                    # -------------------------------------------------

                    if isinstance(
                        value,
                        (dict, list, tuple)
                    ):

                        continue

                    rows.append(
                        (
                            key.replace(
                                "_",
                                " "
                            ).title(),

                            value
                        )
                    )

                if rows:

                    self.add_table(
                        document,
                        rows
                    )

                # -------------------------------------------------
                # RESULT
                # -------------------------------------------------

                result = test.get(
                    "result"
                )

                if not self.is_empty_value(
                    result
                ):

                    self.add_result(
                        document,
                        result
                    )

                # -------------------------------------------------
                # REMARKS
                # -------------------------------------------------

                remarks = test.get(
                    "remarks"
                )

                if not self.is_empty_value(
                    remarks
                ):

                    document.add_paragraph(
                        (
                            "Remarks: "
                            +
                            str(
                                remarks
                            )
                        )
                    )
        # =================================================
        # OVERALL RESULT
        # =================================================

        results = []

        for test in (
            component_tests or []
        ):

            results.append(
                str(
                    test.get(
                        "result",
                        ""
                    )
                ).upper()
            )

        for test in (
            protection_tests or []
        ):

            results.append(
                str(
                    test.get(
                        "result",
                        ""
                    )
                ).upper()
            )

        if not results:

            overall = "NOT TESTED"

        elif any(
            result == "FAIL"
            for result in results
        ):

            overall = "FAIL"

        elif all(
            result == "PASS"
            for result in results
        ):

            overall = "PASS"

        else:

            overall = "PARTIALLY TESTED"

        self.add_heading(
            document,
            "OVERALL PANEL RESULT"
        )

        self.add_result(
            document,
            overall
        )

        # =================================================
        # SIGNATURE
        # =================================================

        self.add_heading(
            document,
            "TESTING / APPROVAL"
        )

        signature_table = (
            document.add_table(
                rows=3,
                cols=2
            )
        )

        signature_table.style = (
            "Table Grid"
        )

        signature_table.rows[
            0
        ].cells[0].text = "Tested By"

        signature_table.rows[
            1
        ].cells[0].text = "Reviewed By"

        signature_table.rows[
            2
        ].cells[0].text = "Date / Signature"

        document.save(
            str(
                output_path
            )
        )

        QMessageBox.information(
            parent,
            "Report Generated",
            (
                "Panel test report generated "
                "successfully.\n\n"
                f"{output_path}"
            )
        )

        return output_path

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def configure_document(
        document
    ):

        section = (
            document.sections[0]
        )

        section.top_margin = Inches(
            0.6
        )

        section.bottom_margin = Inches(
            0.6
        )

        section.left_margin = Inches(
            0.6
        )

        section.right_margin = Inches(
            0.6
        )

        document.styles[
            "Normal"
        ].font.name = "Arial"

        document.styles[
            "Normal"
        ].font.size = Pt(
            9
        )

    @staticmethod
    def add_title(
        document,
        text
    ):

        paragraph = (
            document.add_paragraph()
        )

        paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        run = paragraph.add_run(
            text
        )

        run.bold = True

        run.font.size = Pt(
            18
        )

    @staticmethod
    def add_heading(
        document,
        text
    ):

        paragraph = (
            document.add_paragraph()
        )

        run = paragraph.add_run(
            text
        )

        run.bold = True

        run.font.size = Pt(
            12
        )

    @staticmethod
    def add_table(
        document,
        rows
    ):

        if not rows:

            return

        table = document.add_table(
            rows=1,
            cols=2
        )

        table.style = "Table Grid"

        table.rows[0].cells[0].text = (
            "Parameter"
        )

        table.rows[0].cells[1].text = (
            "Value"
        )

        for label, value in rows:

            cells = (
                table
                .add_row()
                .cells
            )

            cells[0].text = (
                str(label)
            )

            cells[1].text = (
                ""
                if value is None
                else str(value)
            )

    @staticmethod
    def add_result(
        document,
        result
    ):

        paragraph = (
            document.add_paragraph()
        )

        run = paragraph.add_run(
            f"Result: {result}"
        )

        run.bold = True

        run.font.size = Pt(
            11
        )
    # =====================================================
    # EMPTY VALUE CHECK
    # =====================================================

    @staticmethod
    def is_empty_value(
        value
    ):

        if value is None:

            return True

        if isinstance(
            value,
            str
        ):

            cleaned = (
                value
                .strip()
                .lower()
            )

            if cleaned in (
                "",
                "null",
                "none",
                "n/a",
                "na",
                "-"
            ):

                return True

        return False
    # =====================================================
    # ADD PHASE-WISE CT TEST TABLE
    # =====================================================

    def add_phase_test_table(
        self,
        document,
        phase_tests
    ):
        """
        Add phase-wise CT test results to the report.

        Expected structure:

        phase_tests = [
            {
                "phase": "R",
                "injected_primary": "1000",
                "recorded_secondary": "1.002",
                "measured_ratio": "998.00",
                "ratio_error": "-0.20",
                "result": "PASS"
            },
            ...
        ]
        """

        if not phase_tests:
            return

        # -------------------------------------------------
        # Make sure we have dictionaries
        # -------------------------------------------------

        valid_phases = []

        for phase in phase_tests:

            if not isinstance(
                phase,
                dict
            ):
                continue

            valid_phases.append(
                phase
            )

        if not valid_phases:
            return

        # -------------------------------------------------
        # Preferred column order
        # -------------------------------------------------

        preferred_columns = [

            "phase",

            "injected_primary",

            "recorded_secondary",

            "measured_ratio",

            "ratio_error",

            "polarity",

            "polarity_result",

            "result",

        ]

        # -------------------------------------------------
        # Find all available keys
        # -------------------------------------------------

        all_keys = []

        for phase in valid_phases:

            for key in phase.keys():

                if key not in all_keys:

                    all_keys.append(
                        key
                    )

        # -------------------------------------------------
        # Build column order
        # -------------------------------------------------

        columns = []

        for key in preferred_columns:

            if key in all_keys:

                columns.append(
                    key
                )

        # -------------------------------------------------
        # Add any additional fields
        # -------------------------------------------------

        for key in all_keys:

            if key not in columns:

                columns.append(
                    key
                )

        # -------------------------------------------------
        # Remove completely empty columns
        # -------------------------------------------------

        final_columns = []

        for key in columns:

            has_value = False

            for phase in valid_phases:

                value = phase.get(
                    key
                )

                if not self.is_empty_value(
                    value
                ):

                    has_value = True

                    break

            if has_value:

                final_columns.append(
                    key
                )

        if not final_columns:
            return

        # -------------------------------------------------
        # Create table
        # -------------------------------------------------

        table = document.add_table(
            rows=1,
            cols=len(
                final_columns
            )
        )

        table.style = "Table Grid"

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        header_cells = (
            table
            .rows[0]
            .cells
        )

        for index, key in enumerate(
            final_columns
        ):

            header_cells[index].text = (
                key
                .replace(
                    "_",
                    " "
                )
                .title()
            )

        # -------------------------------------------------
        # Rows
        # -------------------------------------------------

        for phase in valid_phases:

            cells = (
                table
                .add_row()
                .cells
            )

            for index, key in enumerate(
                final_columns
            ):

                value = phase.get(
                    key
                )

                if self.is_empty_value(
                    value
                ):

                    cells[index].text = ""

                else:

                    cells[index].text = str(
                        value
                    )