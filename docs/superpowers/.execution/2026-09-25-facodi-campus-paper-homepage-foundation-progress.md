# SDD ledger — plan: docs/superpowers/plans/2026-09-25-facodi-campus-paper-homepage-foundation.md

Pre-flight: Tasks 2–5 consume the semantic token/primitives produced by Task 1; Tasks 3–5 consume stable snippet IDs preserved by earlier tasks; Task 6 consumes all new English source copy; Task 7 consumes the complete Phase A surface. No interface conflict found.

Ruling: isolated GitHub feature branch is the execution workspace because this harness cannot create a network-backed local git worktree; production remains untouched. Cost if wrong: branch-level conflicts discovered later rather than locally; mitigated by exact-head GitHub CI before any PR/merge.

Ruling: RED/GREEN fast contracts are exercised in disposable local fixtures and the exact remote branch is then subjected to the repository CI gate. Cost if wrong: a local fixture could miss integration behavior; mitigated by the full Odoo clean-install/upgrade job before completion.

Task 1: complete (RED: Campus Paper token file missing; GREEN: PASS Campus Paper design-system contract; remote files created on feat/facodi-campus-paper-homepage).
