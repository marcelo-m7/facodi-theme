{
    "name": "FACODI Theme",
    "summary": "FACODI visual identity for Odoo Website and eLearning",
    "version": "19.0.3.0.0",
    "category": "Theme/Education",
    "sequence": 120,
    "author": "FACODI",
    "website": "https://facodi.pt",
    "license": "LGPL-3",
    "depends": ["theme_common", "website_slides"],
    "data": [
        "data/generate_primary_template.xml",
        "data/ir_asset.xml",
        "views/customizations.xml",
        "views/snippets.xml",
        "views/website_slides.xml",
    ],
    "images": ["static/description/theme_facodi.svg"],
    "images_preview_theme": {},
    "configurator_snippets": {
        "homepage": [
            "s_facodi_hero",
            "s_facodi_learning_journey",
            "s_facodi_institutional",
            "s_features",
            "s_call_to_action",
        ],
    },
    "assets": {
        "web.assets_frontend": [
            "theme_facodi/static/src/scss/components.scss",
            "theme_facodi/static/src/scss/website.scss",
            "theme_facodi/static/src/scss/snippets.scss",
            "theme_facodi/static/src/scss/website_slides.scss",
        ],
    },
    "installable": True,
    "application": False,
}
