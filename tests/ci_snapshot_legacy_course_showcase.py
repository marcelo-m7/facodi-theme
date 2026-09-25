"""Snapshot repaired translated course-showcase state before idempotency CI."""

import hashlib
import json

FIXTURE_KEY = "theme_facodi.ci_legacy_course_showcase"
SNAPSHOT_KEY = "theme_facodi.ci_legacy_course_showcase_digest"

view = env["ir.ui.view"].with_context(active_test=False).search([("key", "=", FIXTURE_KEY)], limit=1)
assert view, "legacy course showcase CI fixture is missing"
stored = view._fields["arch_db"]._get_stored_translations(view) or {}
digest = hashlib.sha256(json.dumps(stored, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
env["ir.config_parameter"].sudo().set_param(SNAPSHOT_KEY, digest)
env.cr.commit()
