{
    "name": "FACODI Website Theme",
    "summary": "FACODI visual identity for Odoo Website and eLearning",
    "version": "19.0.1.0.0",
    "category": "Website/Theme",
    "author": "FACODI",
    "website": "https://facodi.pt",
    "license": "LGPL-3",
    "depends": ["website_slides"],
    "data": [
        "views/website_layout.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            "website_facodi/static/src/scss/primary_variables.scss",
        ],
        "web.assets_frontend": [
            "website_facodi/static/src/scss/theme.scss",
            "website_facodi/static/src/scss/elearning.scss",
        ],
    },
    "installable": True,
    "application": False,
}
