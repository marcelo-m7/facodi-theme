# SDD ledger — plan: docs/superpowers/plans/2026-09-25-facodi-learning-interfaces-d1.md

Pre-flight: Task 1 produces reusable D1 classes consumed by Tasks 2 and 6; names match the plan/spec.
Pre-flight: Tasks 3-5 in facodi-learning produce semantic QWeb hooks consumed by theme Task 6; exact class names match.
Pre-flight: Task 8 consumes exact green SHAs from both owner repositories; no production merge is part of D1.
Ruling: this harness cannot create a local network-backed git worktree, so isolated GitHub feature branches plus exact-head GitHub Actions are the execution workspace. Cost if wrong: slower feedback; mitigated by observing RED/GREEN on branch CI.
