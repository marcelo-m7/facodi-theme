# FACODI × SEA-EU 2026 — Gdańsk follow-up campaign

**Status (20 October 2026):** Editorial assets drafted; Odoo website.page **19**, route **/sea-eu**, QWeb view **6761** (key: website.facodi_seaeu_2026). Confirm live publishing and browser QA status in Odoo before distributing any campaign URL.

## Purpose and source of truth

After FACODI's presentation at the 3rd Being SEA-EU Conference, invite interested students and educators to discover the platform voluntarily, without extracting the conference participant list or treating event registration as newsletter consent. The FACODI Odoo database owns the website page. This repository stores a **read-only recovery snapshot**, not a deployable page record.

The campaign is **separate** from recovering accounts lost before the post-Gdańsk database reset.

## Content and approval

- PT/EN editorial kit: https://docs.google.com/document/d/1MG2yH9vTXsScBF_QZmjl-bwynIMLrvFG-rkLjv29CUc/edit
- Institutional cooperation proposals: https://docs.google.com/document/d/1bvd4ae9D6uRsG_A78hnQE745rGskxz5myMrGhGfkwZs/edit
- Odoo parent task **287**; subtasks **288–294**; institutional organiser follow-up **285**.
- Editorial review: Gustavo and Marcelo. Institutional logo use, attribution, announcement approval and external email sending must be reviewed separately.
- Organizer (Gdańsk) and SEA-EU/UAlg invitation emails were drafted in Gmail but **not sent**.

## Landing route and standard forms

- /sea-eu is one Odoo website page, not a new controller.
- /web/signup: native Odoo account registration (auth_signup.invitation_scope = b2c, verified on 20 Oct).
- /slides: native Odoo eLearning.
- Newsletter: separate optional website_mass_mailing.s_newsletter_block_form_template from installed module. The standard form includes an explicit consent checkbox, and the mailing.contact model was verified to allow website form submissions. Actual submission and unsubscribe must still be tested.
- /privacy-policy and /terms-of-use are native website legal pages. Signup must not auto-enrol users in marketing.
- The snapshot is intentionally PT/EN; this website also has FR/ES language support. Verify language fallback/translation policy before multilingual promotion.

## Tracking and data minimisation

Reuse utm.campaign **2** (FACODI · Divulgação SEA-EU 2026). The following utm.source records were created: **19** Gdańsk Organisers, **20** SEA-EU/UAlg Communications, **21** partner institutions, **22** FACODI LinkedIn. Existing utm.medium **4** Email, **11** FACODI Social, **12** QR print.

Example tagged URLs (only after public page QA):
- /sea-eu?utm_source=seaeu_organizers&utm_medium=email&utm_campaign=facodi_gdansk_2026
- /sea-eu?utm_source=seaeu_ualg&utm_medium=email&utm_campaign=facodi_gdansk_2026
- /sea-eu?utm_source=seaeu_partners&utm_medium=email&utm_campaign=facodi_gdansk_2026
- /sea-eu?utm_source=instagram&utm_medium=social&utm_campaign=facodi_gdansk_2026
- /sea-eu?utm_source=poster_qr&utm_medium=qr&utm_campaign=facodi_gdansk_2026

Use aggregated analytics and separate signup and email-consent metrics. Never put personal data in UTM links or claim that conversion tracking exists until separately verified.

## Acceptance checklist

1. Preserve the current production database and filestore before applying any disaster-recovery import or redeploy.
2. Confirm Odoo page #19 and view #6761 binding and validate the QWeb rendering, not only the saved view XML.
3. Render desktop and mobile, PT and EN and verify FR/ES fallbacks.
4. From a public browser, follow /web/signup, /slides, /privacy-policy and /terms-of-use.
5. Verify registration and optional newsletter subscription separately with a controlled test account and email. Test unsubscribe and audit opt-in evidence; do not import conference participants.
6. Publish only after QA passes; then verify HTTP 200 and server logs. QR/email distribution remains blocked until independently checked.
7. Once approved, update the snapshot from the actual production ir.ui.view.arch_db and compare before future upgrades.
8. Track institutional approvals and aggregate engagement in Odoo.

## Deployment safety

The file theme_facodi/data/website_snapshots/sea_eu_2026.xml is intentionally **not in the module manifest**. Theme install/upgrade must not import it or edit website.page. Drift is reconciled manually through an explicit controlled process; this PR does not automatically recreate, overwrite, redeploy or publish the production website.
