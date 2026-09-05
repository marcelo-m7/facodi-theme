# FACODI Theme Architecture

## Boundary

`theme_facodi` owns presentation only.

```text
Odoo 19 Community
├── website / Website Builder
├── website_slides
└── theme_common (pinned from odoo/design-themes)
          │
          ▼
     theme_facodi
     ├── palette and Website theme values
     ├── editable FACODI snippets
     ├── narrow website.layout inheritance
     └── presentation-only website_slides styling
```

Website and eLearning domain behavior stays in the standard Odoo modules. The theme does not become the source of truth for course data, publication, membership, access or learner progress.

## Upstream theme dependency

`theme_common` is sourced from the official `odoo/design-themes` repository and must be pinned by the build/runtime composition layer. It is not copied into this repository.

The current implementation cycle uses commit:

```text
a1818df4ade65406c0cacae8b1ea676e6f70095f
```

## Theme lifecycle

The addon follows Odoo design-theme conventions:

- technical module name `theme_facodi`;
- primary variables registered in `web._assets_primary_variables`;
- Bootstrap-level overrides registered in `web._assets_frontend_helpers`;
- `_generate_primary_snippet_templates` for Website Builder theme templates;
- theme XML is loaded through Odoo's theme-template lifecycle before being copied to the selected website;
- narrow QWeb inheritance instead of copied Website/eLearning templates.

## Visual system

`primary_variables.scss` owns the FACODI palette, color combinations and Website theme defaults. Frontend SCSS uses standard Odoo/Bootstrap semantic variables after the theme palette has been resolved.

Styles are separated by responsibility:

```text
primary_variables.scss      Website Builder palette/theme values
bootstrap_overridden.scss   Bootstrap shape defaults
components.scss             reusable FACODI presentation primitives
website.scss                global Website refinements
snippets.scss               FACODI snippet styling
website_slides.scss         standard eLearning presentation
```

## Website Builder

Editors retain standard Odoo controls for pages, menus, sections, colors, header/footer, logo and favicon. FACODI snippets extend the standard snippet catalog rather than creating a parallel page builder.

The theme never embeds ad-hoc `request.env`, `sudo()` or ORM searches in QWeb. Dynamic learning data must continue through supported Odoo Website/eLearning mechanisms.

## Website and navigation

`website.layout` is inherited only to add the `facodi-site` styling hook and theme-color metadata. The standard header/footer are preserved, including mobile navigation, login/portal behavior, language selection and Website branding records.

## eLearning

`website_slides` remains authoritative for `/slides`, course pages, lesson pages, membership and progress. The theme targets stable standard classes with SCSS and does not add duplicate routes, controllers or models.

## Standard-first decision rule

For every future presentation change:

```text
Does standard Odoo already provide it?
├── yes → configure or style the standard capability
└── no
    ├── stable template/snippet extension point exists → inherit narrowly
    └── otherwise → create one focused FACODI component
```

Do not replace complete application surfaces merely to change presentation.

## Upgrade discipline

Prefer palette/theme values first, standard Bootstrap/Odoo utilities second, narrow QWeb inheritance third, and custom components only when necessary. Any future JavaScript must solve a concrete theme/editor requirement and use the current Odoo frontend framework.
