from odoo import models


class Website(models.Model):
    _inherit = "website"

    def _get_snippet_defaults(self, snippet):
        defaults = super()._get_snippet_defaults(snippet)
        if snippet == "theme_facodi.s_facodi_course_showcase":
            return defaults | {
                "filter_xmlid": "theme_facodi.dynamic_filter_published_courses",
                "template_key": (
                    "theme_facodi."
                    "dynamic_filter_template_slide_channel_facodi_course_card"
                ),
                "data_attributes": {
                    "snippet": "s_facodi_course_showcase",
                    "number-of-records": "6",
                    "number-of-elements": "3",
                    "number-of-elements-small-devices": "1",
                    "extra-classes": "g-3",
                    "column-classes": "col-12 col-md-6 col-xl-4 d-flex",
                },
            }
        return defaults
