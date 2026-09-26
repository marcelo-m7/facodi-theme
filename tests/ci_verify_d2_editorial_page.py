"""Verify a D2 editor-owned page survives a subsequent theme upgrade."""

KEY = "theme_facodi.ci_d2_editorial_page"
MARKER = "D2 editor-owned preservation marker"

page = env["website.page"].with_context(active_test=False).search(
    [("key", "=", KEY)],
    limit=1,
)
assert page, "D2 editor-owned page fixture disappeared after upgrade"
assert page.url == "/d2-editorial-ci"
assert MARKER in page.arch, "theme upgrade overwrote editor-authored D2 content"
assert "facodi-project-story" in page.arch, "D2 component markup disappeared after upgrade"
assert 'data-snippet="s_facodi_project_story"' in page.arch
