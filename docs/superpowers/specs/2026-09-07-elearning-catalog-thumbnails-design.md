# FACODI eLearning catalogue and dynamic thumbnails — design

Date: 2026-09-07
Repository: `marcelo-m7/facodi-theme`
Target: Odoo 19 Community, `website` + `website_slides`

## Goal

Modernize the FACODI eLearning experience, especially `/slides`, while keeping `website_slides` authoritative for catalogue data, course/lesson routes, membership, progress, filters, search, pagination and content access.

The theme must stop relying on static/hardcoded course imagery when better visual material already exists in Odoo content. Course and lesson cards should render the best available visual without creating a parallel catalogue or persisting derived covers back into business records.

## Architectural constraints

- `theme_facodi` remains presentation-oriented.
- `website_slides` owns `slide.channel`, `slide.slide`, catalogue mechanics and learning state.
- No new catalogue model, controller, route, cron or external thumbnail service.
- No per-card ORM searches in QWeb.
- No `sudo()` to reveal private/unpublished learning content to public visitors.
- No HTTP calls to YouTube, Vimeo, Google Drive or other providers during `/slides` rendering.
- No copying of external thumbnails into `slide.channel.image_1920` merely for presentation.
- Preserve Website Builder, Bootstrap/Odoo conventions, native translations and standard JavaScript hooks/classes.
- Prefer focused QWeb inheritance/XPath over complete template replacements.

## Existing Odoo 19 behavior used by the design

`slide.channel` and `slide.slide` both inherit `image.mixin`. Standard `website_slides` already renders `slide.channel.image_1920` in catalogue cards and `slide.slide.image_1920` in lesson cards.

For video/document ingestion, Odoo already identifies YouTube IDs and can fetch/store provider thumbnails in `slide.slide.image_1920` while metadata is being created or refreshed. The catalogue implementation should reuse this stored state first. A deterministic YouTube thumbnail URL may be rendered only when a valid standard `youtube_id` exists and no stored slide image is available.

The standard course catalogue currently renders Bootstrap row columns and preserves search, tags, membership, progress and pager state. Those mechanics remain authoritative.

## Visual resolver

### Non-destructive rule

A manually configured course cover remains authoritative. Derived visuals are rendering fallbacks only and never overwrite the channel image.

### Priority

For each `slide.channel`:

1. real explicitly configured channel cover;
2. representative published slide with `image_1920`;
3. representative published YouTube slide with a valid `youtube_id` and deterministic thumbnail URL;
4. another representative published slide with usable stored imagery;
5. FACODI HTML/CSS fallback.

Categories (`slide.slide.is_category`) are never selected as representative content.

When selecting a representative slide, preserve the course's natural content order (`sequence`, `id`) after filtering to eligible visual candidates. Existing stored slide images take precedence over provider-derived URLs.

### Distinguishing a real course cover

The resolver must avoid treating the standard Odoo placeholder/default image as an editorially configured course cover. It should determine whether `image_1920` is genuinely present rather than assuming the binary image widget's placeholder output means the course has a real cover.

### Batch behavior

The presentation helper is implemented as an extension of `slide.channel` inside `theme_facodi`. It accepts a recordset and resolves all requested channels together.

Conceptual result:

```python
{
    channel_id: {
        "kind": "channel" | "slide" | "youtube" | "fallback",
        "slide": slide_or_false,
        "url": optional_external_url,
        "alt": text,
    }
}
```

The implementation must make a bounded number of queries for the whole channel recordset, not one search per card. The helper must respect the current user's visibility/access context and must not call external services.

The helper is presentation-only: it does not create fields that become editorial truth and does not persist derived thumbnails.

## QWeb integration

Use focused inherited templates in a dedicated `website_slides` customization XML file.

Primary inheritance targets:

- `website_slides.courses_home`
  - widen only the catalogue layout wrapper with a FACODI-specific class;
  - preserve search bar, filters, sidebar, offcanvas and pagination.

- `website_slides.courses_search_results`
  - adapt the results container/grid for a wider responsive catalogue;
  - retain standard `channels`, search/filter state and `website.pager`.

- `website_slides.course_card`
  - replace only the visual media region with the FACODI visual resolver output;
  - retain standard course URL, title, tags, membership/progress state and CTA semantics.

- `website_slides.lesson_card`
  - use the same visual hierarchy for lesson imagery where appropriate;
  - distinguish video/document/article/quiz/image content visually while preserving standard access rules and controls.

- `website_slides.course_slides_list_slide`
  - localized markup/class additions only when needed for content-type/state presentation;
  - preserve `.o_wslides_slides_list_slide`, `.o_wslides_js_slides_list_slide_link`, drag/drop hooks, completion controls, preview controls and publisher actions.

No standard template is copied wholesale unless a focused XPath is demonstrably impossible.

## `/slides` layout

The catalogue should use a wider FACODI content frame rather than the narrow standard container, while still keeping readable gutters and a maximum width on very large screens.

Target behavior:

- wide desktop: up to about 5 cards when width genuinely allows it;
- normal desktop: about 3–4 cards;
- tablet: 2 cards;
- mobile: 1 card.

CSS Grid is preferred for the course results area because it can respond to actual available width, including the authenticated-user sidebar, without hardcoding a different template for every state. Bootstrap remains the surrounding layout system.

Search, tag filters, mobile offcanvas, authenticated overview/sidebar and pager remain standard Odoo components.

## Course card design

Each course card keeps the standard course link and learning state but receives a compact FACODI visual hierarchy:

1. 16:9 visual region;
2. optional status/type indicator;
3. title clamped to roughly two lines;
4. short description clamped to roughly three lines;
5. tags;
6. compact metadata such as duration/content count;
7. standard progress/start/continue/completed state.

Cards must not grow excessively because of long copy. Media uses `object-fit: cover` and consistent aspect ratio.

The whole linked card remains keyboard-accessible. Existing nested post-link behavior for tags must remain functional.

## Lesson/content presentation

For training course lists, retain the standard list structure and JavaScript hooks. Improve spacing, content-type recognition, completion/new/preview states and keyboard focus without changing data behavior.

For documentation lesson cards, improve media consistency and content-type identification while preserving standard access checks, likes/dislikes, tags, completion and navigation.

Content type should be derived from existing `slide_category`, `slide_type` and standard icon data rather than introducing a duplicate taxonomy.

## YouTube behavior

Do not parse arbitrary YouTube URLs in theme code when Odoo already exposes `slide.youtube_id`.

Resolution order for YouTube slides:

1. stored `slide.image_1920` when available;
2. deterministic public YouTube thumbnail URL derived from valid `youtube_id`;
3. generic FACODI content fallback.

The server never fetches the deterministic URL during catalogue rendering. The browser loads the image directly when that fallback is selected.

Provider failures must degrade to the FACODI fallback without breaking the card.

## FACODI fallback

The final fallback is rendered as semantic HTML + CSS rather than one generic raster image.

It may contain:

- FACODI wordmark treatment;
- course/content initials;
- title or abbreviated label;
- existing content-type icon;
- simple FACODI geometric composition.

This keeps fallback cards visually distinct and resolution-independent without duplicating image files.

## Accessibility

- Meaningful focus-visible treatment on cards, CTAs, filters and lesson links.
- Preserve semantic headings from standard templates.
- Images that add no information beyond the adjacent title use `alt=""` to avoid duplicate announcements.
- A representative-content thumbnail may use meaningful alternative text when it conveys distinct content.
- Fallback text remains readable and sufficiently contrasted.
- Interactive target sizes remain usable on touch devices.
- Existing Odoo controls retain their accessible names and behavior.
- Respect reduced-motion preferences.

## Performance

- No network request from Odoo to thumbnail providers during catalogue rendering.
- No per-course search from QWeb.
- Resolve representative slides in a batch for all catalogue channels.
- Reuse stored Odoo image derivatives (`image_512`, etc.) when possible.
- Browser images use appropriate native loading behavior; below-the-fold catalogue images should normally be lazy-loaded, while existing above-the-fold homepage showcase behavior remains independently controlled.
- Do not add client-side JavaScript when backend/QWeb/CSS can solve the requirement.

## Files expected to change

- `theme_facodi/models/__init__.py`
- new `theme_facodi/models/slide_channel.py`
- new `theme_facodi/views/website_slides.xml`
- `theme_facodi/static/src/scss/website_slides.scss`
- `theme_facodi/__manifest__.py`
- `theme_facodi/tests/test_website.py` and/or focused new tests
- repository contract tests if new files/data registrations need assertions
- `README.md`, `docs/architecture.md` and `docs/validation.md` where behavior/evidence changes
- native PO/POT catalogues only for newly introduced user-visible source strings

`facodi-learning` should not be changed unless implementation proves that a truly functional learning concern cannot be kept presentation-only. That would require a separate design decision rather than silently moving business logic into the theme.

## Testing strategy

Start with failing regression tests before implementation.

Fixtures must cover at least:

1. course with explicit cover;
2. course without cover and with representative slide image;
3. course without cover and with YouTube slide;
4. course with no usable image;
5. non-video slide/content;
6. private or unpublished content that must not become a public thumbnail;
7. authenticated course membership/progress state.

Runtime checks:

- `/slides` public returns 200 and renders FACODI catalogue structure;
- `/slides` authenticated preserves overview/membership behavior;
- training course page preserves standard lesson list controls;
- documentation course page preserves standard lesson cards and controls;
- English and Portuguese routes render without custom language branching;
- standard course/lesson classes required by Odoo JavaScript remain present;
- generated frontend assets compile without Sass errors;
- clean install succeeds;
- `-u theme_facodi` succeeds;
- prior Website Builder dynamic snippet regression remains green.

Responsive validation targets representative viewport classes: mobile, tablet, normal desktop and wide desktop. Where browser acceptance is available in CI, assert observable layout/card dimensions or column behavior rather than only static CSS strings. Otherwise document the remaining visual-only manual validation boundary.

## Git workflow

Implementation branch: `feat/elearning-catalog-thumbnails`, created from the then-current `main` commit `a138995e000a2d2316e96f07666128709b9dc108`.

Development flow:

1. add regression tests;
2. confirm expected failures;
3. implement the batch visual resolver;
4. add focused QWeb inheritance;
5. implement responsive SCSS and accessibility refinements;
6. run repository and Odoo runtime tests;
7. review complete diff for accidental ownership or template regressions;
8. commit focused changes;
9. open a PR;
10. require CI green for the exact PR head before considering merge.

Deployment composition remains the responsibility of `marcelo-m7/facodi-deploy` and is outside this theme implementation unless explicitly requested after the theme PR is validated.

## Success criteria

The work is successful when `/slides` presents a spacious, modern FACODI learning catalogue while remaining standard Odoo `website_slides`, and when imagery follows this non-destructive hierarchy:

```text
EXPLICIT COURSE COVER
        ↓
STORED CONTENT THUMBNAIL
        ↓
YOUTUBE THUMBNAIL FROM STANDARD youtube_id
        ↓
OTHER REPRESENTATIVE CONTENT IMAGE
        ↓
FACODI HTML/CSS FALLBACK
```

No course requires a manually duplicated static theme image to remain visually presentable, and the implementation introduces no N+1 catalogue queries or provider HTTP calls from the server during rendering.
