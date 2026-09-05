# FACODI Native Header and Reusable Snippets Design

Date: 2026-09-05
Repository: `marcelo-m7/facodi-theme`
Target module: `theme_facodi`
Status: approved design, pending implementation plan

## 1. Purpose

Refactor the FACODI Odoo 19 theme so that the visual language shown in the current FACODI website is preserved while the implementation relies more closely on Odoo Website theme mechanisms.

The change has two related goals:

1. preserve the current FACODI navigation appearance without permanently replacing the entire standard `website.layout` header;
2. persist FACODI visual sections as reusable Odoo Website Builder snippets and reusable page compositions rather than page-specific duplicated markup.

The theme remains presentation-only. Website menus, logo configuration, portal authentication, user dropdowns, eLearning data and Website Builder editing remain owned by Odoo standard modules.

## 2. Current State

The repository already contains the correct theme module name and dependencies:

- module: `theme_facodi`;
- category: `Theme/Education`;
- dependencies: `theme_common`, `website_slides`.

The current theme already provides reusable FACODI snippets, including:

- FACODI Hero;
- Learning Journey;
- Institutional;
- Editorial intro;
- Learning principles;
- Community and contribution;
- Roadmap;
- Frequently asked questions;
- Course catalogue CTA.

It also provides page compositions that reuse these snippets through `t-snippet-call`.

The current architectural problem is the header implementation. `views/customizations.xml` inherits `website.layout` and uses `position="replace"` on the whole `<header>`. Although the replacement correctly uses standard Odoo components such as `website.placeholder_header_brand`, `website.submenu`, `portal.placeholder_user_sign_in` and `portal.user_dropdown`, replacing the entire header makes the theme unnecessarily coupled to the current core header structure and reduces compatibility with Odoo Website header options.

## 3. Approved Visual Contract

The refactor must preserve the public appearance of the current FACODI navigation shown in the approved reference screenshot:

- light paper-like background;
- dark blue FACODI navigation text and border;
- configurable website logo/brand at the left;
- menu aligned to the right on desktop;
- dynamic Website menu entries;
- authenticated user or login action shown as a lime FACODI button;
- compact, bordered FACODI mobile toggle;
- visible bottom separator line;
- existing FACODI typography, border, shadow and interaction language.

The Odoo editor/admin chrome is outside the theme contract and must not be styled as part of the public header.

## 4. Target Architecture

### 4.1 Header ownership

The target design uses an Odoo-native selectable FACODI header template rather than an unconditional full-header replacement.

The header must continue to compose standard Odoo primitives:

- `website.placeholder_header_brand` for website-controlled logo/brand;
- standard Website menu records and `website.submenu` for navigation;
- `portal.placeholder_user_sign_in` for anonymous login;
- `portal.user_dropdown` for authenticated users;
- the standard Website mobile header/template mechanism for responsive behavior.

FACODI owns only composition and visual treatment.

Conceptually:

```text
website.layout
└── selected FACODI header template
    ├── standard configurable brand
    ├── standard dynamic Website menus
    ├── standard portal sign-in
    └── standard portal user dropdown
```

The theme must expose the FACODI header through the Website Builder header-template option mechanism so it behaves as a normal theme header choice.

### 4.2 Snippet ownership

Each FACODI building block remains a reusable Website snippet with its own stable QWeb template ID and `data-snippet` identity.

The implementation should move away from one large `views/snippets.xml` containing every block. The target layout is one template file per FACODI block plus a small registry file that registers the FACODI snippet group and available snippets.

Target structure:

```text
theme_facodi/
├── views/
│   ├── website_templates.xml
│   ├── page_templates.xml
│   └── snippets/
│       ├── snippets.xml
│       ├── s_facodi_hero.xml
│       ├── s_facodi_learning_journey.xml
│       ├── s_facodi_institutional.xml
│       ├── s_facodi_intro.xml
│       ├── s_facodi_features.xml
│       ├── s_facodi_community.xml
│       ├── s_facodi_roadmap.xml
│       ├── s_facodi_faq.xml
│       └── s_facodi_course_cta.xml
└── static/src/
    ├── scss/
    │   ├── components.scss
    │   ├── website.scss
    │   ├── snippets.scss
    │   └── website_slides.scss
    └── website_builder/
        └── header_template_option.xml
```

Exact filenames may be adjusted to match Odoo 19 theme conventions discovered during implementation, but responsibilities must remain separated.

### 4.3 Page compositions

Existing page templates remain compositions of reusable snippets rather than duplicated markup.

For example, the FACODI homepage remains conceptually:

```xml
<t t-snippet-call="theme_facodi.s_facodi_hero"/>
<t t-snippet-call="theme_facodi.s_facodi_learning_journey"/>
<t t-snippet-call="theme_facodi.s_facodi_course_cta"/>
```

Changing a snippet definition must not require editing every page composition that uses it.

### 4.4 Visual primitives

Shared visual primitives remain centralized in SCSS rather than copied into snippet-specific styles.

Existing primitives to preserve include, among others:

- `facodi-button`;
- `facodi-button-primary`;
- `facodi-button-secondary`;
- `facodi-card`;
- `facodi-stat-card`;
- `facodi-panel`;
- `facodi-grid`;
- `facodi-kicker`;
- `facodi-wordmark`.

Odoo color combinations (`o_cc`) and Website Builder-controlled visual properties must remain editable wherever practical.

## 5. Module Boundaries

`theme_facodi` remains independent from FACODI business addons.

It must not depend on:

- `facodi_learning`;
- `facodi_ai`;
- `monynha-odoo`;
- deployment-specific modules.

`website_slides` remains the only functional eLearning dependency because the theme styles and extends the standard eLearning presentation.

The theme must not query course data directly with `request.env` from presentation templates to create a parallel catalogue. Odoo `website_slides` remains the owner of course/catalogue records and routes.

## 6. Deployment Repository Contract

`marcelo-m7/facodi-deploy` is a composition/deployment repository, not a presentation source repository.

No FACODI theme markup or SCSS should be duplicated into `facodi-deploy`.

After `facodi-theme` is implemented and validated, `facodi-deploy` should only advance the `addons/facodi-theme` gitlink to the tested commit. Any deploy-side test change should only verify the pinned theme version/module availability, not recreate theme behavior.

## 7. Internationalization

The existing native Odoo i18n implementation must remain intact.

Refactoring snippet files must preserve translatable source strings and existing translation behavior. Markup used only for icons, numeric markers or branding that is intentionally non-translatable must retain appropriate `t-translation="off"` handling.

Moving strings between QWeb files must not silently drop existing translations. Translation extraction/update must be part of verification when source locations change.

## 8. Accessibility and Responsive Behavior

The refactor must preserve or improve:

- semantic navigation landmarks;
- accessible labels for the mobile navigation toggle;
- visible keyboard focus states;
- reduced-motion behavior already present in the theme;
- readable contrast for FACODI dark blue, lime and paper combinations;
- responsive desktop/mobile navigation without custom parallel authentication logic.

Mobile navigation should use the native Odoo Website mobile header/template mechanism whenever supported by the selected Odoo 19 theme API rather than implementing an unrelated second navigation system.

## 9. Error and Upgrade Safety

The implementation must fail safely during module installation/upgrade:

- inherited view XPaths must target stable Odoo 19 theme extension points;
- no XPath should replace the complete core header unless Odoo 19 provides no supported selectable-header mechanism, in which case implementation must stop and the design must be revisited before proceeding;
- all snippet XML must load independently in manifest order;
- duplicate XML IDs are forbidden;
- the theme must install on a clean Odoo 19 Community database with `theme_common` and `website_slides`;
- upgrading an existing database from the current `theme_facodi` version must preserve Website menus, logo settings, pages and translated content.

## 10. Testing Strategy

Implementation will follow TDD and extend the existing theme contracts.

Required automated coverage:

1. **Module contract tests**
   - manifest loads the new snippet files;
   - FACODI header template option is registered;
   - no unconditional `xpath expr="//header" position="replace"` remains;
   - standard dynamic menu and brand primitives remain present;
   - all nine FACODI snippets are registered exactly once.

2. **Odoo installation tests**
   - clean install on Odoo 19 succeeds;
   - theme assets compile;
   - homepage renders HTTP 200;
   - `website_slides` routes continue rendering.

3. **Website behavior tests**
   - rendered header contains configurable Odoo website brand/logo output;
   - rendered header contains Website menu records dynamically;
   - anonymous sign-in and authenticated user mechanisms remain standard Portal components;
   - selected FACODI header renders expected FACODI classes.

4. **Snippet tests**
   - each snippet template exists and renders;
   - page compositions reference snippets instead of duplicating their internal structures;
   - snippet source strings remain translatable.

5. **Regression checks**
   - current FACODI visual tokens and key classes remain available;
   - existing four-language i18n contract remains green;
   - eLearning theme tests remain green.

6. **Deployment contract**
   - only after theme CI is green, update `facodi-deploy` gitlink to the exact validated FACODI theme commit;
   - run deploy repository contract/CI against that exact gitlink.

## 11. Acceptance Criteria

The work is complete only when all of the following are true:

- the public navigation is visually equivalent to the approved FACODI reference;
- logo remains configurable from Odoo Website settings/editor;
- Website Menu Editor changes appear automatically in the public menu;
- login and authenticated user dropdown remain standard Portal/Odoo mechanisms;
- FACODI header is represented through the Odoo Website theme/header option mechanism rather than an unconditional complete core-header replacement;
- responsive/mobile navigation uses Odoo-native header mechanisms;
- all nine FACODI blocks appear independently in the Website Builder FACODI group;
- page compositions continue to reuse snippet templates;
- no theme presentation code is copied into `facodi-deploy`;
- clean Odoo 19 installation and upgrade tests pass;
- existing multilingual behavior remains valid;
- `facodi-deploy` pins the exact tested `facodi-theme` commit only after theme validation.

## 12. Non-Goals

This change does not:

- redesign the approved FACODI visual identity;
- change public menu content or ordering stored in Odoo;
- create a new course catalogue or parallel eLearning routes;
- change FACODI business models;
- add AI functionality;
- modify Coolify/GCP infrastructure beyond advancing the tested theme gitlink later;
- alter Odoo's backend/admin editor chrome.

## 13. Implementation Sequence Constraint

Implementation must proceed in this order:

1. add failing contracts for the native/selectable header and separated snippets;
2. implement/refactor `theme_facodi` until its Odoo 19 CI is green;
3. perform visual/behavioral validation against the approved reference;
4. only then update the `facodi-deploy` submodule gitlink;
5. validate `facodi-deploy` against the exact tested commit.

Production deployment is outside this design step and must not be triggered automatically by the theme refactor.
