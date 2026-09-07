# FACODI Theme

`facodi-theme` provides the Odoo 19 Community addon **`theme_facodi`** for
FACODI Website and eLearning presentation.

The public Website at [edu-open2.odoo.com](https://edu-open2.odoo.com) is the
visual source of truth. Release `19.0.5.0.3` preserves that identity while
keeping navigation, Website Builder and eLearning behavior on standard Odoo 19
mechanisms. It adds responsive course presentation and content-derived catalogue
visuals without introducing a parallel course system.

## Verified visual identity

The live site uses Odoo `theme_default` plus Website Builder customizations.
Those database artifacts were inspected through the Odoo API and translated
into maintainable QWeb and SCSS; they are evidence, not runtime dependencies.

| Role | Color |
|---|---|
| Ink | `#142846` |
| Cyan | `#37BED2` |
| Blue | `#3979C8` |
| Mint | `#A7E8BE` |
| Sun | `#EFFF00` |
| Paper | `#F9FAFB` |

The visual language uses strong ink borders, offset shadows, geometric cards,
bright calls to action and responsive layouts. Font stacks prefer Space
Grotesk, Inter and JetBrains Mono when already available and fall back to
system fonts without making remote font requests.

## What the addon provides

- Website Builder palette and semantic color combinations;
- FACODI wordmark, buttons, cards and visual tokens;
- a selectable FACODI desktop header registered through Odoo `theme.utils`;
- standard Website logo, dynamic `website.menu` records and `website.submenu` recursion;
- standard Portal sign-in and authenticated user dropdown;
- the standard Odoo mobile header rather than a parallel FACODI mobile menu;
- dynamic footer using Website menu records and standard routes;
- nine independently maintained editable FACODI snippets and ten native New Page compositions;
- native Odoo translations for Portuguese (Portugal), Spanish and French, with English source copy;
- responsive presentation refinements for standard `website_slides` catalogue, training and documentation surfaces;
- dynamic course visuals resolved from explicit course covers, stored lesson images, Odoo YouTube IDs or an HTML fallback;
- translated content-type cues using Odoo's own `slide_category` selection labels;
- accessible focus indicators and reduced-motion behavior;
- optional preview, logo and favicon assets.

The addon **does not import Website pages**. It does not overwrite Homepage,
About, Manifesto, Community, Roadmap or other editorial content. It also does
not add controllers, a second course model, authentication logic or business-data
queries in QWeb.

## Standard-first ownership

- Website Builder owns pages, menus, translations, section editing, configured
  logos and favicons.
- Odoo Website owns the outer public header, header selection/configuration and
  the standard responsive/mobile header.
- `theme_facodi.template_header_facodi` owns only the FACODI desktop navigation
  composition and its presentation.
- `website_slides` owns `/slides`, courses, lessons, enrolment and learner
  progress.
- Portal owns sign-in and user navigation.

The former live database link `/web/content/431` is deliberately absent from
the addon. Its `facodi-online.css` contents are represented by versioned SCSS,
and no database-specific record id is required after installation.

## eLearning catalogue visuals

The `/slides` catalogue stays on Odoo's native controller, search/filtering and
course-card templates. FACODI resolves visuals in one read-only batch with this
priority:

1. explicit `slide.channel.image_1920`;
2. a published, non-category lesson with stored `slide.slide.image_1920`;
3. `https://i.ytimg.com/vi/<youtube_id>/hqdefault.jpg`, using Odoo's stored
   `slide.slide.youtube_id`;
4. a FACODI HTML/CSS fallback without a broken image request.

The resolver performs no HTTP fetch and writes no derived thumbnail back to Odoo.
QWeb receives one visual map for the current channel recordset, avoiding an ORM
search for each course card. Documentation lesson cards use the same stored-image,
YouTube-ID and fallback policy.

The catalogue uses a 1/2/3/4/5-column responsive CSS Grid across progressively
wider breakpoints. Standard `website_slides` card/list links and JS hooks remain in
the rendered DOM. Training and documentation cards receive FACODI content-type cues
while labels continue to come from Odoo's translated selection metadata.

## Native header integration

The FACODI header is a normal Odoo theme header option. The module:

1. registers `theme_facodi.template_header_facodi` through
   `theme.utils._header_templates`;
2. enables it in `_theme_facodi_post_copy` when the theme is applied;
3. exposes it in `website.HeaderTemplateOption` through `html_builder.assets`;
4. replaces only the standard `//header//nav` extension point;
5. composes `website.navbar`, `website.placeholder_header_brand`,
   `website.navbar_nav`, `website.submenu`, `portal.placeholder_user_sign_in`
   and `portal.user_dropdown`;
6. renders that FACODI navigation only on desktop and delegates mobile
   navigation to `website.template_header_mobile`.

There is no unconditional whole-`<header>` replacement and no FACODI-specific
navigation JavaScript.

## Builder library and page compositions

The nine public snippet XML IDs remain stable:

- `s_facodi_hero`;
- `s_facodi_learning_journey`;
- `s_facodi_institutional`;
- `s_facodi_intro`;
- `s_facodi_features`;
- `s_facodi_community`;
- `s_facodi_roadmap`;
- `s_facodi_faq`;
- `s_facodi_course_cta`.

Each block lives in its own file under `theme_facodi/views/snippets/`; the small
`views/snippets/snippets.xml` file only registers the FACODI Builder group and
its blocks. This keeps snippet identities stable while avoiding page-specific
copies of the same markup.

Choose **New → Page → FACODI** to create a page from one of the ten compositions.
The theme registers templates; it creates no editorial pages automatically.
Edit the resulting page using the standard Website Builder and save normally.
Course and contact links point to the canonical `/slides` and `/contactus`
routes.

| Composition | Snippets |
|---|---|
| Home | Hero, Learning Journey, Course CTA |
| About | Editorial Intro, Institutional, Features |
| Manifesto | Editorial Intro, Institutional, Community |
| How | Editorial Intro, Learning Journey, FAQ |
| Community | Editorial Intro, Community, FAQ |
| Pathways | Editorial Intro, Learning Journey, Course CTA |
| Contribution | Editorial Intro, Features, Community |
| Roadmap | Editorial Intro, Roadmap, Community |
| Partners | Editorial Intro, Features, Community |
| Editorial | Editorial Intro, Features, Course CTA |

Compositions provide editable starting copy, without invented partners,
metrics or testimonials. Publishers own final editorial text and URLs. FAQ
uses native keyboard-accessible disclosure elements with no duplicate IDs.

## Internationalization

English is the canonical source language of the FACODI QWeb templates. The
addon uses Odoo's native module translation mechanism and does not implement a
parallel language selector, JavaScript translation store or per-language QWeb
branches.

The shipped catalogues are:

- `theme_facodi/i18n/pt.po` for `pt_PT` — Português (Portugal);
- `theme_facodi/i18n/es.po` for `es_ES` — Español;
- `theme_facodi/i18n/fr.po` for `fr_FR` — Français.

There is intentionally no `en.po`: English is the source language. The
canonical extraction template is `theme_facodi/i18n/theme_facodi.pot`.

On a FACODI Website, enable/publish English, `pt_PT`, `es_ES` and `fr_FR` using
the standard Odoo Website language configuration and set English as the
Website default language. Language activation and the default-language choice
remain Website configuration rather than a hard-coded side effect of this
reusable theme.

Theme translations are stored on Odoo's theme view records and propagated to
the Website-specific view copies by the standard theme lifecycle. The test
suite loads the native catalogues before applying the theme and validates the
localized Website routes. eLearning content-type badges reuse Odoo's translated
field-selection labels rather than duplicating those translations in the theme.

The New Page composition names are kept in English. Odoo 19 stores the
`theme.ir.ui.view.name` field as a non-translatable technical label, so the
addon does not introduce a custom translation layer for those names. Visible
snippet copy and translatable Website Builder strings use native Odoo i18n.

## Runtime dependencies

The module depends only on:

- `theme_common`, from the pinned Odoo 19-compatible
  `odoo/design-themes@a1818df4ade65406c0cacae8b1ea676e6f70095f` checkout;
- `website_slides`, supplied by Odoo Community.

There is no dependency on Odoo Enterprise or on a FACODI business addon.

## Installation

Make Odoo core, the pinned `odoo/design-themes` checkout and this repository
available on `addons_path`:

```bash
odoo -d facodi \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/opt/odoo-design-themes,/path/to/facodi-theme \
  -i theme_facodi \
  --stop-after-init
```

For an existing installation, deploy the new source and update the module:

```bash
odoo -d facodi \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/opt/odoo-design-themes,/path/to/facodi-theme \
  -u theme_facodi \
  --stop-after-init
```

Activate or reapply the theme from Website settings after testing in a staging
database. Page content remains separate, but intentionally customized local
header or footer views should be reviewed before changing the selected theme
header.

## Verification

Run the fast repository contracts:

```bash
bash tests/test_module_contract.sh
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_foundation_v2_contract.sh
bash tests/test_i18n_contract.sh
bash tests/test_elearning_catalog_style_contract.sh
```

GitHub Actions then uses PostgreSQL 16 and the official `odoo:19.0` image to:

- install the pinned legacy theme release on a clean database;
- compile frontend and Website Builder assets;
- apply the theme through the native `apply_new_theme` lifecycle;
- verify the selectable FACODI desktop header and standard Odoo mobile header;
- verify configured Website logo output, dynamic nested/external/active menu behavior and Portal identity actions;
- activate native Website languages and verify localized routes;
- verify all reusable Website-specific snippet copies;
- verify `/slides`, localized `/pt/slides`, authenticated catalogue rendering, `/contactus` and `/web/login`;
- validate batch course-cover resolution, deterministic YouTube URLs and no-image fallbacks;
- validate training/documentation content-type cues while preserving standard Odoo hooks;
- render all ten New Page compositions and preserve editor-owned page HTML across theme reload;
- compile and fetch frontend CSS without Sass errors;
- rerun the regression suite on `-u theme_facodi` upgrade;
- repair and verify persisted legacy dynamic-snippet builder markup;
- confirm that the configured Website favicon is not replaced.

Editorial course cover images remain authoritative. Website Builder color combinations
remain authoritative; the theme does not partially switch colors based on OS
dark mode.

## Repository integration

`marcelo-m7/facodi-deploy` consumes this repository as a pinned Git submodule.
Image composition and deployment remain responsibilities of that repository;
this repository contains only the installable presentation addon. Deployment
integration must advance the gitlink only to an exact FACODI theme commit whose
own clean-install and upgrade CI is green.

See [architecture](docs/architecture.md) for implementation boundaries and
[validation](docs/validation.md) for the current evidence matrix.

## License

LGPL-3.0.