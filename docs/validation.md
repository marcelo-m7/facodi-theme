# Validation — 2026-09-07

## Environment and scope

Validation uses disposable PostgreSQL 16 and the official Odoo 19.0 Community
container with `odoo/design-themes` pinned at
`a1818df4ade65406c0cacae8b1ea676e6f70095f`. The public FACODI sites are evidence
and deployment targets only; this repository's CI does not modify production.

Release under validation: `theme_facodi` `19.0.5.0.3`.

## Automated evidence required for release

The release gate is the repository's `Odoo 19 Theme CI` workflow. A revision is
eligible for merge only when the workflow succeeds on that exact PR head. After
merge, the workflow must succeed again on the exact `main` merge commit.

The workflow performs:

- repository, homepage, Foundation v2 and native-i18n contracts;
- responsive eLearning catalogue style contract;
- pinned official Odoo design-theme checkout;
- installation of the pinned legacy `19.0.5.0.1` theme on a clean PostgreSQL 16 database;
- real Odoo 19 addon tests and frontend/Website Builder asset compilation;
- seeding of persisted legacy course-showcase markup;
- upgrade to the current release with `-u theme_facodi`;
- verification that the legacy dynamic-snippet builder contract is repaired without losing editor content.

## eLearning regression matrix

The Odoo `HttpCase` and `TransactionCase` suite verifies the presentation added in
`19.0.5.0.3` against real `website_slides` records and routes:

- `/slides` keeps the standard `.o_wslides_course_card` hook;
- course cards render an explicit `slide.channel` cover first;
- a published stored `slide.slide` image is the next visual source;
- YouTube thumbnails are derived deterministically from Odoo's stored `youtube_id`;
- YouTube fixture creation is mocked so the test suite itself does not depend on provider HTTP;
- courses without usable media render the FACODI HTML/CSS fallback and no broken `<img>`;
- the visual resolver returns one entry per channel and excludes unpublished/category slides;
- training pages keep `.o_wslides_slides_list_slide` and `.o_wslides_js_slides_list_slide_link`;
- documentation pages keep `.o_wslides_lesson_card`;
- content-type cues are present for standard Odoo slide categories;
- documentation cards render stored images, deterministic YouTube media and icon fallbacks;
- Portuguese `/pt/slides` and authenticated `/slides` retain the standard catalogue hooks.

The static style contract additionally requires:

- FACODI catalogue, course-media, lesson-media, fallback and content-type selectors;
- CSS Grid column definitions at 576, 992, 1280 and 1600 px;
- predictable `object-fit: cover` media cropping;
- visible `:focus-visible` rules;
- `prefers-reduced-motion` handling.

## Runtime boundaries

The catalogue visual resolver is intentionally read-only. It does not write images,
make thumbnail-provider requests or introduce a custom course model/controller. The
QWeb layer consumes a batch visual map and preserves `website_slides` as the owner of
search, filtering, enrolment, lessons and progress.

The content-type labels come from Odoo's translated `slide_category` selection
metadata instead of a second FACODI translation vocabulary. English remains the
canonical theme source language and Website language routing remains native Odoo.

## Reproduction

With Odoo core, the pinned design-themes checkout and this repository available on
`addons_path`, the fast contracts are:

```sh
bash tests/test_module_contract.sh
bash tests/test_homepage_dashboard_contract.sh
bash tests/test_foundation_v2_contract.sh
bash tests/test_i18n_contract.sh
bash tests/test_elearning_catalog_style_contract.sh
```

The CI workflow then runs the clean-install and upgrade commands against the same
disposable database using the official Odoo 19 container and `--test-tags
/theme_facodi`.

## Existing Website and Builder coverage

The broader regression suite continues to verify:

- native theme lifecycle and `_theme_facodi_post_copy()`;
- selectable FACODI desktop header plus standard Odoo mobile header;
- nested/external Website menu behavior and Portal identity controls;
- configured Website logo and favicon ownership;
- reusable FACODI snippets and New Page compositions;
- editor-owned page HTML across theme reload;
- `/`, `/contactus` and `/web/login`;
- native Portuguese, Spanish and French Website translations;
- compilation and HTTP retrieval of frontend assets without Sass errors.

The persisted legacy course-showcase test specifically protects the Odoo dynamic
snippet editor contract (`.s_dynamic_snippet_container` and
`.s_dynamic_snippet_content`) introduced by release `19.0.5.0.2`.

## Visual and deployment boundary

CI proves source contracts, real Odoo rendering, asset compilation, clean install and
upgrade behavior. It does not claim pixel-perfect browser geometry on every device or
an authenticated production Website Builder session. Browser screenshots and manual
keyboard inspection remain supporting evidence rather than a formal WCAG audit.

`marcelo-m7/facodi-deploy` must pin the exact merged `facodi-theme` commit separately.
Advancing that gitlink validates the deployment composition; it is not evidence that
Coolify production has already redeployed.