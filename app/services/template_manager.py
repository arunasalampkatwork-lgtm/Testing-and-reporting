from app.config.test_templates import (
    TEST_TEMPLATES
)


class TemplateManager:

    def __init__(self):

        self.templates = TEST_TEMPLATES

    # =====================================================
    # GET TEMPLATE
    # =====================================================

    def get_template(
        self,
        protection_function
    ):

        return self.templates.get(
            protection_function
        )

    # =====================================================
    # CHECK TEMPLATE
    # =====================================================

    def has_template(
        self,
        protection_function
    ):

        return (
            protection_function
            in self.templates
        )

    # =====================================================
    # ALL TEMPLATES
    # =====================================================

    def get_available_templates(self):

        return list(
            self.templates.values()
        )