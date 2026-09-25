# SDD ledger — plan: docs/superpowers/plans/2026-09-25-facodi-campus-paper-global-surfaces.md

Pre-flight: Task 1 produces global shell hooks consumed only by rendered/visual acceptance; Task 2 and Task 3 both consume Phase A tokens but do not depend on each other; Task 4 consumes only existing paper primitives; Task 5 normalizes shared geometry after Tasks 1–4; Task 6 consumes the complete Phase B surface. No interface conflict found.

Ruling: this harness cannot create a network-backed local git worktree because the container cannot resolve github.com. Execution therefore uses an isolated GitHub feature branch and exact-head GitHub Actions as the integration workspace. Cost if wrong: slower RED/GREEN feedback; mitigated by explicit failing branch CI before implementation and exact-head green CI after each gate.

Ruling: CI invocation for new static contracts is moved forward to the task that introduces each contract, rather than waiting for Task 6, so TDD RED can be observed on the real branch. Cost if wrong: workflow diff appears earlier than planned, but behavior and final scope remain identical.
