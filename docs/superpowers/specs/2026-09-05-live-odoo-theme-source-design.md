# FACODI Live Odoo Theme Source Design

## Decision

`https://edu-open2.odoo.com` is the visual source of truth for `theme_facodi`.
The addon will reproduce that identity as portable Odoo 19 Community source
code while leaving editorial pages and business behavior under standard Odoo
Website and eLearning ownership.

## Verified source state

The source database is `edu-open2`, website record `FACODI` (`website`, id 2).
The active base module is `theme_default`. The distinctive FACODI presentation
is currently stored as Website Builder/database artifacts rather than as an
installed FACODI theme module:

- `ir.attachment` 431, `facodi-online.css`;
- `ir.ui.view` 2477, `codoo.facodi_online.header`;
- `ir.ui.view` 2478, `codoo.facodi_online.footer`;
- `ir.ui.view` 2479, `codoo.facodi_online.assets`;
- Website Builder color attachments 423, 424 and 775.

The live identity uses these exact tokens:

| Token | Value |
|---|---|
| Ink | `#142846` |
| Cyan | `#37BED2` |
| Blue | `#3979C8` |
| Mint | `#A7E8BE` |
| Sun | `#EFFF00` |
| Paper | `#F9FAFB` |
| Line | `#40536D` |

The currently versioned purple identity (`#6a4bff`, `#5dc7ff`, `#f7f6ff`)
is not part of the approved design and must be removed from the addon and its
documentation.

## Product boundary

The theme owns:

- FACODI palette and Website Builder defaults;
- reusable visual primitives;
- the FACODI dynamic header and footer;
- editable FACODI snippets matching the live visual language;
- presentation-only refinements for standard `website_slides` pages;
- accessible responsive and reduced-motion behavior;
- optional preview, logo and favicon assets.

Standard Odoo continues to own:

- pages and their editorial content;
- menus and menu records;
- authentication, users and Portal;
- languages and translation records;
- courses, lessons, enrolment and progress;
- Website Builder editing, logo and favicon configuration;
- all routes and controllers.

The addon must not import or overwrite `/`, `/sobre`, `/manifesto`,
`/comunidade`, `/roadmap`, `/como-contribuir` or any other site page. It must
not contain ORM queries in QWeb, duplicate Website/eLearning controllers, or
depend on Enterprise modules.

## Implementation shape

The installed module remains `theme_facodi` and depends only on
`theme_common` and `website_slides`. The theme is built over the standard
Odoo theme lifecycle:

- `primary_variables.scss` maps the live Builder palette;
- `bootstrap_overridden.scss` supplies the live geometric shape defaults;
- `components.scss` owns wordmarks, buttons and reusable cards;
- `website.scss` owns the global shell, dynamic header/footer and accessibility;
- `snippets.scss` owns the editable hero, journey and institutional blocks;
- `website_slides.scss` styles stable standard eLearning selectors;
- `customizations.xml` inherits `website.layout` without hard-coded database
  identifiers and renders menus through `website.menu_id.child_id` plus the
  standard Portal sign-in/dropdown templates.

The database-only stylesheet link `/web/content/431` and the duplicate
YouTube hook are deliberately excluded. They are deployment artifacts or
behavior, not portable theme source.

## Acceptance criteria

1. A clean Odoo 19 Community database can install `theme_facodi`.
2. Theme assets compile with the pinned Odoo `design-themes` checkout.
3. The six live colors are represented and no superseded purple token remains.
4. `/` renders the FACODI shell, wordmark, dynamic navigation and footer.
5. `/slides` stays a standard `website_slides` route with FACODI presentation.
6. Website logo and favicon records are not forcibly replaced.
7. The three FACODI snippets remain registered and editable.
8. No editorial page, controller, model or Enterprise dependency is added.
9. Contract tests and Odoo HttpCase tests pass without warnings attributable to
   the addon.

