# FACODI Study Player Shell — Design

**Status:** approved conversational design; written specification for review  
**Date:** 2026-09-27  
**Repository:** `marcelo-m7/facodi-theme`  
**Branch:** `feat/facodi-study-player-shell`  
**Target:** Odoo 19 Community / `website_slides`  
**Design owner:** `theme_facodi`  
**Behavior owner:** native Odoo `website_slides`

## 1. Purpose

This change modernizes the native Odoo eLearning lesson/player experience so that it feels like a first-class FACODI study environment while remaining standard-first.

The implementation is inspired by the approved FACODI Stitch references and the existing Campus Paper / Digital Highlighter visual system already adopted by `theme_facodi`.

The goal is not to create a new video player, course engine, progress engine, notes product or AI backend.

The goal is to add a FACODI study shell around the native Odoo lesson experience, improving layout, hierarchy, navigation, responsiveness and study-oriented affordances while preserving native Odoo behavior.

## 2. Success criteria

The implementation is successful when:

- native Odoo course, lesson, completion, access and progress behavior continues to work unchanged;
- the lesson page clearly looks and feels like FACODI rather than a mostly stock Odoo surface;
- the active lesson, course progress and next/previous navigation are easier to understand;
- the layout works on desktop, tablet and mobile;
- the interface remains usable when JavaScript is unavailable;
- no new learning-domain model or controller is introduced;
- no fake progress, resource, author, duration or AI data is introduced;
- future Supabase AI actions can be added without redesigning the page again;
- accessibility and reduced-motion preferences are respected.

## 3. Scope

### Included

1. A dedicated FACODI study-player QWeb layer on top of native `website_slides`.
2. A dedicated SCSS layer for the lesson/player surface.
3. Small progressive-enhancement JavaScript for presentation interactions only.
4. Improved active-lesson presentation and lesson-list hierarchy.
5. Improved course-progress presentation using values already provided by Odoo.
6. Previous/next study navigation only where native URLs/data are already available in the rendered Odoo context.
7. Study utility panels:
   - About this lesson;
   - Resources;
   - Notes placeholder;
   - AI placeholder.
8. Mobile-friendly sidebar/drawer behavior.
9. Visual CTAs for:
   - suggest improvement;
   - report a problem.
10. Explicit future integration hooks for Supabase-backed AI actions, without network calls in this release.

### Excluded

- custom video playback engine;
- custom media transcoding;
- new `slide.channel` or `slide.slide` fields;
- new progress/completion logic;
- private notes persistence;
- Supabase calls;
- AI generation;
- new forum/discussion backend;
- fabricated resources or lesson metadata;
- replacement of native Odoo routes/controllers;
- a second course/lesson catalogue.

## 4. Architectural principles

### 4.1 Native Odoo remains authoritative

`slide.channel` remains the course model.

`slide.slide` remains the lesson/content model.

Odoo continues to own:

- enrolment;
- access rules;
- lesson completion;
- course completion;
- progress;
- media rendering;
- quiz behavior;
- lesson routing;
- course navigation.

FACODI only changes presentation and small client-side interaction around existing markup/data.

### 4.2 Theme owns presentation only

`theme_facodi` may:

- inherit native QWeb templates;
- add semantic wrappers/classes;
- move already-rendered native blocks into a clearer visual structure when safe;
- add decorative study panels;
- add ARIA attributes where needed;
- add CSS/SCSS;
- add presentation-only JavaScript.

`theme_facodi` must not:

- query learning data directly from QWeb with new ORM searches;
- add business logic;
- duplicate Odoo completion logic;
- add alternative course/lesson records;
- write progress;
- invent missing values.

### 4.3 Progressive enhancement

The baseline page must remain functional without FACODI JavaScript.

JavaScript is limited to:

- opening/closing the mobile study sidebar;
- switching local study-panel tabs;
- scrolling the active lesson into view;
- remembering presentation preferences in local storage where appropriate.

No core action such as completing a lesson, opening content or navigating a course may depend on FACODI JavaScript.

## 5. Proposed file structure

```text
theme_facodi/
├── views/
│   ├── website_slides.xml
│   └── website_slides_player.xml
├── static/src/scss/
│   ├── website_slides.scss
│   └── website_slides_player.scss
├── static/src/js/
│   └── facodi_study_player.js
└── tests/
    ├── test_elearning_catalog_rendering.py
    └── test_study_player_rendering.py
```

The player-specific files are intentionally separated from the existing catalogue/course styling so that the current `website_slides.scss` does not become a monolithic learning stylesheet.

## 6. Visual system

The Study Player continues the existing Campus Paper / Highlighter system.

### 6.1 Surfaces

- off-white paper as the page surface;
- white or warm-paper sheets for content panels;
- subtle graph-paper rhythm where it supports orientation;
- dark ink borders;
- hard offset shadows instead of blurred elevation;
- small/medium semantic corner radius, not oversized app-card rounding.

### 6.2 Highlighter semantics

Use existing FACODI semantic tokens:

- Sun/yellow: primary emphasis, active study state, primary CTA;
- Mint: completed/affirmative state;
- Cyan: navigation/information;
- Blue: supporting information;
- Ink: text, borders and strong hierarchy.

Existing design tokens remain the source of truth. The Study Player should not introduce arbitrary one-off colors when a FACODI token already exists.

### 6.3 Lesson states

Lesson rows need visually distinct states based only on native Odoo state:

- active/current;
- completed;
- available/not completed;
- inaccessible/locked if Odoo already renders that state.

FACODI must not infer completion or availability independently.

## 7. Desktop layout

The desktop study view should read as a three-part study surface where the native template structure allows it safely:

```text
┌──────────────────────────────────────────────────────────────┐
│ course context / breadcrumb / progress                       │
├──────────────────────────────────────┬───────────────────────┤
│                                      │ course index          │
│ native lesson/player/content         │ active lesson         │
│                                      │ sections / lessons    │
│                                      │ progress              │
├──────────────────────────────────────┴───────────────────────┤
│ About | Resources | Notes | AI                              │
├──────────────────────────────────────────────────────────────┤
│ Previous lesson                         Next lesson           │
└──────────────────────────────────────────────────────────────┘
```

The exact DOM placement must follow the safest available native Odoo extension points after implementation inspection.

If a full three-column arrangement would require replacing native behavior or fragile XPath surgery, the right-side course index may remain in the native location and only receive FACODI styling.

## 8. Mobile/tablet behavior

On smaller screens:

- the player/content remains first;
- the course index becomes collapsible;
- the sidebar uses a drawer-like presentation where practical;
- study panels stack vertically;
- tabs remain horizontally scrollable if needed;
- previous/next actions remain thumb-friendly;
- no fixed panel may block native video fullscreen or core controls.

All interactive controls require usable touch targets.

## 9. Study utility panels

### 9.1 About this lesson

Displays only native information already present in the lesson page/context.

No new ORM lookup is introduced merely to populate the panel.

### 9.2 Resources

Uses native resources/attachments only if they are already exposed by the standard lesson template/context.

If no native resources are available, the panel may display a neutral empty state.

### 9.3 Notes

This release provides presentation only.

The UI must explicitly communicate that persistence is not yet available, or the control must remain disabled/non-editable. It must not imply notes are saved when they are not.

### 9.4 AI

This release provides a future-facing panel with disabled or clearly inactive actions such as:

- Summarize lesson;
- Generate flashcards;
- Explain concept;
- Generate quiz;
- Ask FACODI AI.

No request is sent to Supabase or any AI provider in this release.

The markup should use stable `data-facodi-ai-action` hooks so the future Supabase implementation can attach behavior without redesigning the UI.

## 10. Contribution/problem-report CTAs

The lesson page may expose FACODI actions for:

- Suggest an improvement;
- Report a problem.

These should reuse existing FACODI/public contribution/contact routes if such routes already exist in the deployed project.

This theme change must not introduce a new backend submission mechanism.

If the implementation cannot resolve an existing real route safely from the current codebase, the CTA should not be added until that route is confirmed.

## 11. JavaScript contract

Target file:

`theme_facodi/static/src/js/facodi_study_player.js`

Responsibilities:

- initialize only when a FACODI study-player root element exists;
- toggle mobile course index;
- update ARIA-expanded state;
- switch local study-panel tabs;
- move focus appropriately after drawer/tab interactions;
- scroll the active native lesson row into view;
- persist only non-sensitive UI preferences, if useful.

It must not:

- mark lessons complete;
- write course progress;
- call Supabase;
- call Odoo RPC;
- intercept native media controls;
- replace native route navigation.

## 12. Accessibility

The implementation must include:

- logical heading hierarchy;
- keyboard-accessible tabs/drawer controls;
- visible focus states using FACODI focus tokens;
- meaningful `aria-expanded`, `aria-controls`, tab roles/relationships where custom tabs are used;
- no color-only communication of lesson completion/current state;
- reduced-motion handling;
- acceptable contrast for all highlighter surfaces.

Where native Odoo already provides accessible semantics, FACODI should preserve them rather than replace them.

## 13. Testing strategy

### 13.1 QWeb/rendering tests

Add targeted rendering assertions for:

- Study Player root wrapper;
- active lesson class/hook;
- course index still contains native Odoo lesson links;
- completion controls are still present when expected;
- native player/content region is preserved;
- utility panel markup renders without fake data;
- AI controls are inert/disabled;
- contribution CTAs appear only when backed by real routes.

### 13.2 Static/style contract tests

Add lightweight source-level assertions for:

- no new ORM `.search(` calls in player QWeb;
- no Supabase endpoint/client references;
- no custom completion RPC;
- reduced-motion rule exists;
- responsive breakpoint behavior exists;
- new player stylesheet is registered in the manifest.

### 13.3 Regression validation

Verify at minimum:

- public course/lesson;
- authenticated course/lesson;
- video lesson;
- document/article lesson where available;
- quiz lesson where available;
- completed and incomplete lesson states;
- mobile viewport;
- desktop viewport;
- Portuguese route;
- English/default route;
- JavaScript disabled baseline.

## 14. Error/fallback behavior

- If FACODI JavaScript fails, native Odoo navigation and content remain usable.
- If resources are absent, show an honest empty state.
- If native previous/next information is not available, do not fabricate navigation.
- If an AI action has no backend, keep it disabled/inactive and label it appropriately.
- If an expected optional native block is absent, the QWeb inheritance must fail gracefully by targeting stable upstream hooks rather than replacing broad page sections.

## 15. Rollout strategy

Implementation should be additive and reviewable:

1. register the new player view/style assets;
2. add minimal semantic wrappers;
3. style the native lesson surface;
4. add responsive course-index treatment;
5. add utility panels;
6. add progressive-enhancement JavaScript;
7. add tests;
8. validate native behavior before merging.

No deployment-specific change is required in `facodi-deploy` for the feature itself.

## 16. Future Supabase integration boundary

A later implementation may connect AI actions to Supabase Edge Functions.

That future work should bind to stable frontend hooks, for example:

```html
<button
  type="button"
  data-facodi-ai-action="summarize"
  data-facodi-slide-id="...">
  Summarize lesson
</button>
```

The future integration must remain outside this release.

This keeps the current implementation safe, testable and standard-first while preventing a later AI phase from forcing another structural redesign.

## 17. Explicit non-goals

This design does not attempt to turn FACODI into a separate LMS.

It does not replace Odoo's native lesson lifecycle, and it does not make the theme responsible for educational-domain state.

The Study Player is a presentation and interaction shell around native Odoo behavior.
