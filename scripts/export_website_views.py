#!/usr/bin/env python3
"""Export FACODI critical QWeb views from a running Odoo shell (read-only).

Execute inside the deployed container or staging environment:
  FACODI_EXPORT_PATH=/tmp/facodi-live-views.json \
    odoo shell -d facodi --no-http \
    < scripts/export_website_views.py

Never store this export in a public repository. It can contain editorial text.
No database writes are performed.
"""
import json
import os
from pathlib import Path

ids = [5176, 6144, 2669, 6140, 6141, 6142, 6143]
path = Path(os.environ.get("FACODI_EXPORT_PATH", "/tmp/facodi-live-views.json"))
if path.exists():
    raise RuntimeError(f"Refusing to overwrite existing export: {path}")

records = env["ir.ui.view"].sudo().browse(ids)
if len(records.exists()) != len(ids):
    raise RuntimeError("Critical FACODI view IDs missing; abort export")
views = [
    {"id": r.id, "key": r.key, "arch_db": r.with_context(lang="en_US").arch_db,
     "write_date": str(r.write_date), "website_id": r.website_id.id or None}
    for r in records
]
themes = env["theme.ir.ui.view"].sudo().search(
    [("key", "=", "theme_facodi.facodi_footer")]
)
theme_templates = [
    {"key": r.key, "arch": r.with_context(lang="en_US").arch}
    for r in themes
]
data = {"views": views, "theme_templates": theme_templates}
path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
path.chmod(0o600)
print(f"READ-ONLY export: {len(views)} views, {len(theme_templates)} theme templates -> {path}")
