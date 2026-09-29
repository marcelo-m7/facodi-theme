def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    compatibility_filter = env.ref(
        "theme_facodi.published_courses_filter",
        raise_if_not_found=False,
    )
    if compatibility_filter:
        compatibility_filter.write(
            {
                "domain": "[('visibility', 'in', ['public', 'connected'])]",
                "sort": "[]",
            }
        )

    wrapper = env.ref(
        "theme_facodi.dynamic_filter_published_courses",
        raise_if_not_found=False,
    )
    if wrapper and compatibility_filter:
        wrapper.write(
            {
                "filter_id": compatibility_filter.id,
                "field_names": "name,description_short,total_slides,website_url",
                "limit": 6,
            }
        )
