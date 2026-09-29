def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    wrapper = env.ref(
        "theme_facodi.dynamic_filter_published_courses",
        raise_if_not_found=False,
    )
    canonical_filter = env.ref(
        "website_slides.dynamic_snippet_latest_courses_filter",
        raise_if_not_found=False,
    )
    if not canonical_filter:
        raise RuntimeError(
            "website_slides canonical eLearning course filter is required"
        )

    if wrapper:
        wrapper.write(
            {
                "filter_id": canonical_filter.id,
                "field_names": "name,description_short,total_slides,website_url",
                "limit": 6,
            }
        )

    legacy_filter = env.ref(
        "theme_facodi.published_courses_filter",
        raise_if_not_found=False,
    )
    if legacy_filter:
        legacy_filter.unlink()
