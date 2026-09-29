def migrate(cr, version):
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid in (
        "theme_facodi.dynamic_filter_published_courses",
        "theme_facodi.published_courses_filter",
    ):
        record = env.ref(xmlid, raise_if_not_found=False)
        if record:
            record.unlink()
