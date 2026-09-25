# SDD ledger — plan: docs/superpowers/plans/2026-09-25-facodi-learning-interfaces-d1.md

Pre-flight: Task 1 produces reusable D1 classes consumed by Tasks 2 and 6; names match the plan/spec.
Pre-flight: Tasks 3-5 in facodi-learning produce semantic QWeb hooks consumed by theme Task 6; exact class names match.
Pre-flight: Task 8 consumes exact green SHAs from both owner repositories; no production merge is part of D1.
Ruling: this harness cannot create a local network-backed git worktree, so isolated GitHub feature branches plus exact-head GitHub Actions are the execution workspace. Cost if wrong: slower feedback; mitigated by observing RED/GREEN on branch CI.

Task 1: Ruling: the CI release grep moved from Task 6 into Task 1 because the manifest version is bumped when the new asset is loaded; leaving the old grep would make the task's integration gate fail for a bookkeeping mismatch. Cost if wrong: release guard changes earlier than planned, with no runtime behavior change.

Task 1: complete (CI run 36185027249 on exact branch head after implementation → success; D1 primitive, mobile, module, install/upgrade and builder-preservation gates all passed).

Task 2: Ruling: Odoo 19 course_card root is an <a class="o_wslides_course_card">, not a div; target the stable native class on the anchor. Root cause confirmed from Odoo 19 upstream and CI traceback. Cost if wrong: course catalogue rendering would return HTTP 500, covered by exact-head Odoo tests.

Task 2: complete (CI run 36186275344 → success; native catalogue/course shell, install/upgrade, custom-cover contract and Website Builder gates passed).

Task 6: Ruling: facodi-theme/main advanced with PR #25 while D1 was in progress. Carried the stronger rendered/default custom-cover regression into the D1 branch before final styling verification. Cost if wrong: duplicated test drift; exact-head theme CI now exercises the combined suite.
Task 6: complete (CI run 36190206579 → success; D1 compiled assets, Roadmap/UC/module selectors, 8/4 unit layout, rendered cover preservation, install/upgrade and builder-preservation gates passed).
