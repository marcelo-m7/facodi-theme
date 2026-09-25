# FACODI D2 — Editorial & Public Pages Redesign

**Status:** approved conversational design; written specification for review  
**Date:** 2026-09-25  
**Primary repository:** `marcelo-m7/facodi-theme`  
**Live composition target:** FACODI Website on `facodi.com`  
**Design owner:** `theme_facodi`

## 1. Purpose

D2 extends the approved FACODI Campus Paper / Digital Highlighter Campus system from Home and the D1 learning interfaces into the remaining public editorial surfaces.

The goal is not to freeze editorial pages into addon XML. The goal is to give Odoo Website Builder a stronger, reusable FACODI editorial component library and to style native public applications so the whole site feels like one coherent digital campus.

D2 covers:

- About / project story;
- the “How it works” section;
- contribution/community pages;
- native News/Blog index and article pages;
- native Contact page/form;
- legal/policy readability surfaces;
- reusable editorial compositions for Manifesto, Partners and general public pages.

D2 does not redesign learning-domain pages already completed in D1.

## 2. Source hierarchy

D2 uses the supplied Google AI Stitch materials as visual and editorial reference, with this priority:

1. `Digital Highlighter Campus / DESIGN.md` — system-level palette, typography, grid, hard shadows, stationery metaphors and accessibility rules.
2. FACODI homepage redesign reference — establishes the Campus Paper interpretation already implemented in the theme.
3. Course catalogue and Curricular Unit references — establish the filing-card/index-tab language and disciplined use of fluorescent markers.
4. FACODI marketing kit — supports the “Campus Bulletin” editorial concept for news and announcements.
5. extracted current FACODI public navigation/content — establishes the canonical information architecture and existing routes.
6. the current `facodi-theme` component library and Campus Paper/D1 contracts — implementation baseline.

The most recent Stitch export is not a literal mockup for every editorial page. D2 therefore translates its design system into editorial layouts rather than inventing unsupported page screenshots.

## 3. Design intent

Editorial pages should feel like a well-organized shared study folder:

- project story = annotated dossier;
- principles = ledger cards;
- process = study/workflow timeline;
- contribution = community noticeboard;
- news = campus bulletin;
- contact = correspondence sheet;
- legal = clean policy document.

The design must remain:

- optimistic;
- academically credible;
- open/community-oriented;
- readable for long-form content;
- visually tactile without becoming decorative noise.

The fluorescent palette directs attention; it must not turn every section into a highlighter collage.

## 4. Architecture boundaries

### 4.1 Theme owns presentation, not editorial truth

`theme_facodi` owns:

- reusable editorial snippets/components;
- visual page-picker compositions;
- SCSS;
- native Odoo template inheritance where justified;
- responsive/accessibility behavior;
- translations for theme-owned source copy;
- browser/runtime visual contracts.

The theme must not:

- import permanent `website.page` records for About, Contribution, Manifesto, Partners, Contact or Legal pages;
- overwrite editor-authored page content during install/upgrade;
- introduce business-domain models;
- hard-code live contact data such as phone numbers or personal addresses;
- fabricate project metrics, partners, testimonials or institutional claims.

### 4.2 Website Builder remains authoritative for editorial pages

The actual About, Contribution and other editor-managed pages remain database-owned Website Builder content.

D2 provides:

- new reusable snippets;
- stronger page-picker compositions;
- stable semantic CSS classes;
- a controlled live recomposition step after the addon is green.

The live recomposition must preserve editor-owned content not explicitly replaced.

### 4.3 Native Odoo applications remain authoritative

- `website_blog` remains authoritative for blog posts, tags, dates, authors, pager and blog routes.
- Odoo Website remains authoritative for Contact and `website_form`.
- legal/policy page content remains Website/editor-owned.
- language routing remains native Odoo.

D2 styles or narrowly inherits these applications. It does not duplicate them.

## 5. Theme dependency decision

D2 makes News/Blog a first-class FACODI public surface.

Because the canonical FACODI site exposes a native blog, `theme_facodi` may add `website_blog` as an explicit addon dependency in release `19.0.9.0.0`.

This is preferred over copying blog templates or using conditional references to templates that may not exist at module-load time.

No additional Enterprise dependency is allowed.

## 6. Visual rules

D2 continues the existing Campus Paper implementation.

### 6.1 Highlighter semantics

- yellow — primary emphasis / selected idea / principal CTA;
- mint — constructive/community/affirmative content;
- cyan — navigation/information/reference;
- pink — priority/attention only;
- orange — review/warning/update only.

Highlighter colors remain backgrounds, rules, tabs or marker strokes behind dark ink. They are not used as low-contrast body text.

### 6.2 Editorial density

Learning interfaces can be dense. Editorial pages should breathe more.

- reading width for long prose: approximately 42–50rem;
- large project-story blocks may span wider grids;
- side notes and rails should not compress primary reading text below a comfortable width;
- legal pages use the least decorative treatment.

### 6.3 Paper depth

Use:

- graph paper for large canvas/hero backgrounds;
- white paper sheets for core content;
- hard ink shadows for lifted cards/CTAs;
- subtle ruled-paper lines for timelines and article metadata;
- limited sticky-note accents.

Avoid blurred material-design shadows.

## 7. Reusable D2 component vocabulary

D2 builds on the existing highlighter heading, paper card, sticky note, folder tabs, metadata row, study steps, CTA sheet and highlighter callout.

New reusable components:

### 7.1 `.facodi-project-story`

Purpose: explain origin, mission and current project status.

Structure:

- mono kicker;
- large narrative heading;
- 1–3 short editorial paragraphs;
- optional timeline/date/source metadata;
- optional side note;
- real project/community CTA.

Must work without images.

### 7.2 `.facodi-principles-ledger`

Purpose: present project principles or manifesto statements.

Structure:

- 2–4 cards;
- numbered/indexed;
- each card contains one principle, explanation and optional link;
- marker stripe may vary per card but color must not imply unsupported status.

### 7.3 `.facodi-process-timeline`

Purpose: explain a real process such as learning discovery or contribution review.

Structure:

- ordered steps;
- connected visual rule;
- short title/body;
- optional real CTA at final step.

Timeline order must represent actual process order.

### 7.4 `.facodi-contribution-board`

Purpose: show real ways to participate.

Eligible contribution types:

- suggest a public learning resource;
- improve context/translation;
- collaborate/contact FACODI.

The board must not imply automatic publication, paid work, formal accreditation or guaranteed acceptance.

### 7.5 `.facodi-bulletin-hero`

Purpose: visual header for native News/Blog index and editorial announcement surfaces.

Language:

- Campus Bulletin / News;
- project updates;
- learning notes;
- community stories.

It must not render fictional post counts or newsletter subscriber metrics.

### 7.6 `.facodi-editorial-quote`

Purpose: reusable pull-quote / manifesto excerpt / key sentence.

Must remain an editorial text block, not a testimonial component unless the quote is actually attributed to a real source.

### 7.7 `.facodi-contact-sheet`

Purpose: frame native Odoo contact content.

Desktop:

- contextual panel;
- native form panel.

Mobile:

- one column.

No hard-coded phone, email or office address is introduced by the theme.

### 7.8 `.facodi-policy-document`

Purpose: readable shell for privacy, cookies and terms.

Features:

- restrained paper sheet;
- readable prose width;
- consistent headings/lists/links;
- optional internal table of contents only when actual anchor headings exist;
- no decorative sticky-note clutter.

## 8. About page design

### 8.1 Intent

The About page should answer:

1. What is FACODI?
2. Why does it exist?
3. How does it organize open learning?
4. What are its limits?
5. How can someone participate?

### 8.2 Composition

Recommended builder composition:

1. editorial intro / project dossier hero;
2. `facodi-project-story`;
3. `facodi-principles-ledger`;
4. “How it works” `facodi-process-timeline` with stable anchor `#how-it-works`;
5. institutional/open-network context;
6. editorial next routes;
7. closing contribution/contact CTA.

### 8.3 Content boundaries

The theme may provide editable starter copy but must not hard-code claims such as:

- student counts;
- number of partner universities;
- recognition/accreditation status;
- employment outcomes;
- guaranteed certificates.

FACODI must remain explicit that curriculum/reference context is not automatic academic equivalence.

## 9. “How it works” design

“How it works” remains part of About unless a future content decision creates a dedicated page.

Its process should be simple and real:

1. discover a course, Roadmap or curricular reference;
2. study using public resources;
3. follow reviewed links/context;
4. suggest useful resources or improvements.

The exact number of steps may be reduced when the page copy is edited, but the visual component must support 3–5 steps cleanly.

No fake progress state is used here.

## 10. Contribution page design

### 10.1 Intent

The contribution page should reduce uncertainty around participation.

It must distinguish:

- submission;
- review;
- publication.

### 10.2 Composition

1. contribution hero;
2. `facodi-contribution-board`;
3. `facodi-process-timeline` showing proposal → review → publication;
4. contribution principles / moderation expectations;
5. community block;
6. CTA sheet linking to the real resource-submission route and Contact.

### 10.3 Required boundary copy

The page must make clear that:

- a submitted resource is not automatically published;
- FACODI may review context/relevance;
- contribution does not imply academic equivalence or formal endorsement.

The theme must not invent moderation SLA or acceptance rates.

## 11. Community and ecosystem surfaces

Existing Community/Ecosystem snippets remain valid but D2 should make them feel less like generic marketing cards and more like a shared campus noticeboard.

Allowed presentation:

- paper notes;
- contributor cards;
- open-network references;
- community CTA.

Partner/network names must only be displayed when they are explicitly editorially configured or already approved in current site content.

No logo wall of invented partners.

## 12. Native News / Blog index

### 12.1 Intent

Treat native Odoo blog as the **Campus Bulletin**.

### 12.2 Behavior preservation

D2 preserves:

- native blog routes;
- blog selection;
- tags/categories;
- publication date;
- author when configured;
- pagination;
- search/filter behavior;
- native post URLs.

### 12.3 Index presentation

The index may contain:

- `facodi-bulletin-hero`;
- a highlighted latest post only if Odoo already provides real ordering/data;
- post cards rendered as bulletin sheets;
- metadata row;
- real tags;
- excerpt;
- date/author only when present.

No fake “featured” status is introduced unless a real model/configuration provides it.

### 12.4 Post card style

Each post card:

- hard paper border;
- subtle marker category stripe;
- title;
- native cover image where present;
- excerpt;
- date/tags;
- real “read article” link.

Custom blog cover imagery remains authoritative.

## 13. Native Blog article

### 13.1 Intent

Long-form reading should be calmer than catalogue pages.

### 13.2 Composition

- article header sheet;
- title;
- real author/date/tags;
- native cover/media where configured;
- prose body with controlled reading width;
- FACODI callout/quote styling inside article content;
- native share/comment/navigation behavior when enabled.

### 13.3 Typography/readability

- body line length optimized for reading;
- clear H2/H3 hierarchy;
- lists, code/pre, blockquotes and links styled consistently;
- images/videos remain responsive;
- no graph grid directly behind long paragraphs.

## 14. Contact page

### 14.1 Intent

Contact should feel like sending a note to an open campus, not a generic corporate sales page.

### 14.2 Composition

`facodi-contact-sheet`:

left/context panel:
- why to contact;
- examples of valid contact intents;
- link to contribution route when a resource submission is the better path.

right/form panel:
- native Odoo contact form;
- native validation;
- native submission behavior.

### 14.3 Contact-data safety

The theme must never inject placeholder contact data such as:

- fake telephone numbers;
- fake addresses;
- fake support hours.

If configured contact information exists in Website/company data, native Odoo may render it. The theme only styles it.

## 15. Legal / policy pages

### 15.1 Scope

D2 covers visual readability for:

- Privacy Policy;
- Cookie Policy;
- Terms and Conditions;
- equivalent native policy pages.

### 15.2 Rules

- no rewrite of legal copy;
- no legal interpretation added by theme;
- no neon-heavy decoration;
- links clearly visible;
- heading hierarchy maintained;
- lists/tables/code styled legibly;
- mobile line length and overflow handled.

The policy shell should visually belong to FACODI while prioritizing seriousness and readability.

## 16. Manifesto, Partners and generic editorial compositions

D2 preserves the existing page-picker philosophy.

### Manifesto

Use:

- editorial intro;
- principles ledger;
- editorial quote;
- institutional/community context;
- next routes.

### Partners

Use:

- editorial intro;
- ecosystem/network block;
- paper-card partner entries only when real;
- collaboration CTA.

### Generic editorial

Offer a composition built from:

- editorial intro;
- optional quote/callout;
- paper-card body;
- CTA;
- next routes.

No fixed `website.page` records are added.

## 17. Page Builder behavior

Every D2 snippet must:

- be registered in the FACODI snippet group;
- remain editable in Website Builder;
- support normal Odoo duplication/removal/reordering;
- avoid JS-only editing semantics;
- avoid querying ORM directly from QWeb;
- preserve user edits across module upgrade.

Starter copy is editable content, not immutable product logic.

## 18. Live page recomposition

Live recomposition is a separate controlled step after theme CI passes.

Target pages may include:

- About;
- Contribution;
- any generic editorial pages selected for consolidation.

Rules:

1. read current page architecture first;
2. preserve meaningful editor-authored content;
3. remove only obsolete/redundant layout fragments;
4. insert approved D2 snippets/compositions;
5. verify PT/ES/FR;
6. do not modify learning-domain records;
7. do not alter Contact form behavior;
8. do not rewrite legal copy.

This step may use Odoo MCP only after quota/access is available.

## 19. Responsive behavior

### Desktop >= 1024px

- 12-column editorial compositions;
- contact: approximately 5/7 or 4/8 context/form split;
- project story may use 7/5 narrative/note layouts;
- principles ledger supports 3 columns;
- blog cards 2–3 columns depending native container width.

### Tablet 768–1023px

- 8-column rhythm;
- multi-column editorial blocks reduce to two columns;
- side notes move below main content when necessary.

### Mobile < 768px

- single-column editorial flow;
- 1rem gutters;
- titles wrap;
- CTAs stack where needed;
- horizontal decorative transforms disabled;
- long URLs/code/tables never create page-level overflow;
- contact form fields remain full width;
- blog media is responsive.

Hard gate: no page-level horizontal overflow at 320px.

## 20. Accessibility

D2 must preserve:

- semantic heading order;
- native form labels/errors;
- keyboard navigation;
- visible `:focus-visible`;
- minimum practical touch targets;
- color-independent meaning;
- reduced-motion behavior;
- readable text contrast;
- meaningful link labels.

Decorative stationery effects must be `aria-hidden` where applicable.

Blog and legal long-form content must remain readable at 200% zoom.

## 21. Internationalization

English remains canonical source QWeb.

Theme-owned user-facing copy must be represented in:

- POT;
- PT;
- ES;
- FR.

D2 must not hard-code Portuguese in source XML.

Live Website page translations remain database-owned and must not be replaced wholesale by module upgrade.

Blog post translations remain native Odoo content.

## 22. Testing strategy

### 22.1 Static contracts

Add contracts for:

- every new D2 snippet;
- snippet registry;
- page-picker compositions;
- absence of fixed editorial `website.page` imports;
- absence of fake contact data/metrics/testimonials;
- no direct ORM in editorial QWeb;
- release version.

### 22.2 Odoo theme tests

Prove:

- snippets load;
- generated page compositions render;
- editor modifications persist across upgrade;
- native Contact form remains functional;
- Blog index/article templates render when `website_blog` is installed;
- native blog metadata/links remain present;
- legal/editorial styling assets compile;
- PT/ES/FR contracts remain green.

### 22.3 Browser acceptance

Disposable runtime must validate:

- About composition;
- Contribution composition;
- native Blog index;
- one real/fixture blog article;
- Contact;
- representative legal page.

Widths:

- 1440;
- 1024 where useful;
- 390;
- 320.

Fail on page-level overflow.

### 22.4 Production acceptance

After live recomposition/deployment:

- verify canonical public routes;
- verify page titles and internal links;
- verify language variants;
- verify contact form loads;
- verify blog index/article;
- verify legal routes;
- verify no placeholder contact data was introduced.

## 23. Release strategy

D2 is delivered in the following order:

1. reusable editorial component library;
2. About/How composition;
3. Contribution/Community composition;
4. native Blog presentation;
5. Contact/legal presentation;
6. i18n/accessibility/browser gates;
7. owner-repo PR/merge;
8. live Website recomposition;
9. exact gitlink pin in `facodi-deploy`;
10. disposable runtime/browser acceptance;
11. production promotion.

Target release:

- `theme_facodi 19.0.9.0.0`.

No `facodi-learning` release is required for D2 unless implementation uncovers an actual cross-addon presentation contract that cannot remain theme-owned.

## 24. Out of scope

D2 explicitly excludes:

- newsletter subscription backend;
- email-marketing automation;
- fake newsletter statistics;
- CRM lead-flow redesign;
- support ticket system;
- partner database;
- testimonial system;
- private community profiles;
- discussion/forum;
- legal-content authorship;
- blog recommendation engine;
- custom CMS replacing Odoo Website/Blog;
- fixed imported copies of editorial Website pages;
- changing learning-domain logic completed in D1.

## 25. Acceptance criteria

D2 is complete when:

1. About, How, Contribution, Blog, Contact and Legal surfaces share a coherent Campus Paper editorial language;
2. the theme provides reusable editorial components rather than monolithic fixed pages;
3. Website Builder remains authoritative for editor-managed pages;
4. `website_blog` remains authoritative for News/Blog data and behavior;
5. native Contact form behavior is preserved;
6. no fake contact information, metrics, partners or testimonials are introduced;
7. legal copy is not rewritten by the theme;
8. all new theme source copy is translated through native PT/ES/FR catalogues;
9. editor changes persist through module upgrades;
10. representative editorial pages have no page-level horizontal overflow at 320px;
11. owner-repo CI and disposable browser acceptance are green;
12. live page recomposition is reviewed before production deployment.
