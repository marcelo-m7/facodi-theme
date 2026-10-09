# FACODI Navigation and Institutional Consolidation (2026-10-09)

## Current target
Home · Explore · Learn (Courses, Learning paths, Curricular units, Resources) · Community (News, Discussions, Contribute) · About (The Project, Partnerships) · Contact.

- **Explore** is a separate top-level route `/explore`; it is NOT a synonym for Learn.
- **Learn** groups structured learning destinations.
- **About** contains two destinations: `/about` and `/partnerships`.
- Privacy Policy, Terms of Use, Legal Notice, Content Rights, Cookies and Accessibility pages must stay available from the footer, not the primary menu.
- `/about` incorporates curricular context, technology/editorial flow, creator/community and next steps.
- `/partnerships` assembles UAlg, SEA-EU and collaborator context; its claims distinguish factual curricular use from formal endorsement.
- Historical institutional URLs (`/academic-model`, `/infrastructure`, `/about-marcelo`, `/about-ualg`) are **retained** until internal links, translations, redirects and SEO are verified. Do not delete them blindly.

## Source of truth and deployment

- The live changes were first written through Odoo MCP, as requested.
- `theme_facodi/data/facodi_navigation_editorial.json` captures the exact live navigation and HTML for `/about` and `/partnerships`.
- `theme_facodi/scripts/apply_navigation_editorial.py` idempotently reconciles the menu and page records using Odoo ORM. This is an **explicit reconciliation script**, not an automatic module data import. It must be invoked after deployment by an authorised operator, with a database backup/snapshot and target website verified.
- This avoids forcing arbitrary live website editor content to be replaced on every module upgrade and avoids production downtime from unnecessary `facodi-deploy` pushes.
- Example Odoo shell invocation: `exec(compile(open('/mnt/addons/theme_facodi/scripts/apply_navigation_editorial.py').read(), '/mnt/addons/theme_facodi/scripts/apply_navigation_editorial.py', 'exec'))`. Adjust path to installed addon. Ensure `env` is available.
- The snapshot is versioned without private credentials.

## Acceptance and follow-ups

1. Re-read website.menu: no legal entries under About; exactly one Explore and one Learn.
2. Re-read website.page: About and Partnerships published; former institutional pages preserved.
3. Browser-test desktop/tablet/mobile menu, footer legal links, `/explore`, `/about`, `/partnerships`, CTA destinations and translations (PT/EN).
4. Test legacy URLs and configure **301 redirects only after** identifying the intended canonical target and confirming no lost SEO / localisation. Candidate mappings: `/academic-model → /about#academic-model`, `/infrastructure → /about#technology`, `/about-marcelo → /about#team`, `/about-ualg → /partnerships`. Fragment redirects may require special care.
5. Verify and expand footer with permanent legal links.
6. Validate site through external browser/network; the authoring environment could read Odoo RPC but could not access facodi.com over HTTP, so visual/render testing is outstanding.

## Rollback

Restore previous menu names, sequences, URLs and About view from an Odoo snapshot. Remove the new Explore menu and Partnerships page only if confirmed unused; never delete legal pages. Reconciliation script can reapply the desired versioned snapshot after recovery.
