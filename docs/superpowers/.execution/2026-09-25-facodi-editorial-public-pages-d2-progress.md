# SDD ledger — plan: docs/superpowers/plans/2026-09-25-facodi-editorial-public-pages-d2.md

Pre-flight: Task 1 components are consumed by Tasks 2, 5 and 6; class/XML IDs match the approved D2 spec.
Pre-flight: Task 3 Blog and Task 4 Contact consume native Odoo templates and remain theme-owned; no domain model changes.
Pre-flight: Task 8 consumes the exact merged D2 theme SHA; Task 9 performs live Website mutation only after production code is healthy.
Ruling: this harness uses isolated GitHub feature branches rather than a local worktree; exact-head GitHub Actions are the per-task execution gate. Cost if wrong: slower feedback, but no production side effect.
