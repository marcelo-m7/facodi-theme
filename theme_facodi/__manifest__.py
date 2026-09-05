{
    "name": "FACODI Theme",
    "summary": "FACODI visual identity for Odoo Website and eLearning",
    "version": "19.0.5.0.0",
    "category": "Theme/Education",
    "sequence": 120,
    "author": "FACODI",
    "website": "https://facodi.pt",
    "license": "LGPL-3",
    "depends": ["theme_common", "website_slides"],
    "data": [
        "data/ir_asset.xml",
        "views/header.xml",
        "views/customizations.xml",
        "views/snippets.xml",
        "views/page_templates.xml",
    ],
    "images": ["static/description/theme_facodi.svg"],
    "images_preview_theme": {},
    "assets": {
        "web.assets_frontend": [
            "theme_facodi/static/src/scss/components.scss",
            "theme_facodi/static/src/scss/website.scss",
            "theme_facodi/static/src/scss/snippets.scss",
            "theme_facodi/static/src/scss/website_slides.scss",
        ],
        "html_builder.assets": [
            "theme_facodi/static/src/builder/**/*",
        ],
    },
    "installable": True,
    "application": False,
}
