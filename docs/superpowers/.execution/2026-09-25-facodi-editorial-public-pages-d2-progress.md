# SDD ledger — plan: docs/superpowers/plans/2026-09-25-facodi-editorial-public-pages-d2.md

Pre-flight: Task 1 components are consumed by Tasks 2, 5 and 6; class/XML IDs match the approved D2 spec.
Pre-flight: Task 3 Blog and Task 4 Contact consume native Odoo templates and remain theme-owned; no domain model changes.
Pre-flight: Task 8 consumes the exact merged D2 theme SHA; Task 9 performs live Website mutation only after production code is healthy.
Ruling: this harness uses isolated GitHub feature branches rather than a local worktree; exact-head GitHub Actions are the per-task execution gate. Cost if wrong: slower feedback, but no production side effect.

Task 1: complete (CI run 36200433083 → success; D2 component registry, release/dependency, static contracts, legacy install/upgrade and Odoo regression gates passed).

Task 2: Ruling: seed the D2 editor-owned persistence fixture after the first D2 upgrade, then verify it after the second upgrade, because D2 snippet XML IDs do not exist in the legacy 19.0.5.0.1 baseline. Cost if wrong: this proves D2-to-D2 upgrade persistence rather than pre-D2 page migration; the existing native page-preservation Odoo test separately proves theme loading does not overwrite editor-owned content.

Task 2: complete (CI run 36200983706 → success; D2 page-picker compositions render, no fixed editorial pages are imported, and the editor-owned D2 fixture survives a second theme upgrade).

Task 3: complete (CI run 36223790333 → success; native Blog index/article hooks, sparse/rich metadata, custom covers, assets, upgrade and Odoo regression gates passed).

Task 4: complete (CI run 36224266192 → success; native website.contactus inheritance, single native form, required fields/action, assets, upgrade and Odoo regression gates passed).
