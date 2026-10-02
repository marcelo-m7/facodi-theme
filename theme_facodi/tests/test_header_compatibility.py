from odoo.tests import HttpCase, tagged
from lxml import html


@tagged("-at_install", "post_install")
class TestFacodiHeaderCompatibility(HttpCase):
    def test_mobile_navigation_renders_one_control_per_group(self):
        website = self.env["website"].get_current_website()
        theme = self.env["ir.module.module"].search([("name", "=", "theme_facodi")], limit=1)
        website.theme_id = theme
        theme._theme_get_stream_themes().with_context(
            load_all_views=True, apply_new_theme=True
        )._theme_load(website)
        Menu = self.env["website.menu"]
        parent = Menu.create({"name": "Learning", "url": "#", "parent_id": website.menu_id.id, "website_id": website.id})
        for name, url in (("Courses", "/courses"), ("Paths", "/roadmaps")):
            Menu.create({"name": name, "url": url, "parent_id": parent.id, "website_id": website.id})
        response = self.url_open("/")
        self.assertEqual(response.status_code, 200)
        mobile = html.fromstring(response.text).get_element_by_id("top_menu_collapse_mobile")
        self.assertFalse(mobile.xpath('.//*[@data-bs-toggle="dropdown" and @role="menuitem"]'))
        self.assertFalse(mobile.xpath('.//div[@class="facodi-split-menu"]'))
        self.assertEqual(len(mobile.xpath('.//a[contains(@href,"/explore") and normalize-space()="Learning"]')), 1)
        self.assertNotIn("555-555", mobile.text_content())
        self.assertNotIn("Contact Us", mobile.text_content())

        for width in (320, 390, 768):
            self.browser_size = f"{width}x844"
            self.browser_js("/", """
                (async () => {
                    const assert = (ok, message) => { if (!ok) throw new Error(message); };
                    const drawer = document.querySelector('#top_menu_collapse_mobile');
                    const waitEvent = (node, name, action) => new Promise(resolve => {
                        node.addEventListener(name, resolve, {once: true}); action();
                    });
                    const open = document.querySelector('[data-bs-target="#top_menu_collapse_mobile"]');
                    assert(open.getBoundingClientRect().width >= 44, 'Mobile toggle must have a 44px target');
                    await waitEvent(drawer, 'shown.bs.offcanvas', () => open.click());
                    assert(drawer.scrollWidth <= drawer.clientWidth + 1, 'Drawer must not overflow horizontally');
                    const link = [...drawer.querySelectorAll('.facodi-split-menu__link')].find(a => a.textContent.trim() === 'Learning');
                    const toggle = link.parentElement.querySelector('button');
                    const panel = document.getElementById(toggle.getAttribute('aria-controls'));
                    assert(toggle.getBoundingClientRect().width >= 44, 'Submenu target must be at least 44px');
                    await waitEvent(panel, 'shown.bs.collapse', () => toggle.click());
                    assert(toggle.getAttribute('aria-expanded') === 'true', 'Submenu expanded state');
                    assert(panel.querySelector('a[href$="/courses"]').getBoundingClientRect().height >= 44, 'Child links need a 44px target');
                    await waitEvent(panel, 'hidden.bs.collapse', () => toggle.click());
                    await waitEvent(drawer, 'hidden.bs.offcanvas', () => drawer.querySelector('[data-bs-dismiss="offcanvas"]').click());
                    assert(!drawer.classList.contains('show'), 'Close control must close the drawer');
                    console.log('test successful');
                })().catch(error => console.error(error));
            """, ready="!!document.querySelector('#top_menu_collapse_mobile')", timeout=60)

    def test_header_survives_existing_website_header_customization(self):
        website = self.env["website"].get_current_website()
        theme = self.env["ir.module.module"].search(
            [("name", "=", "theme_facodi")], limit=1
        )
        self.assertTrue(theme)

        website.theme_id = theme
        theme._theme_get_stream_themes().with_context(
            load_all_views=True, apply_new_theme=True
        )._theme_load(website)

        self.env["ir.ui.view"].create(
            {
                "name": "FACODI legacy header compatibility fixture",
                "type": "qweb",
                "key": "theme_facodi_test.header_without_nav",
                "inherit_id": self.env.ref("website.layout").id,
                "website_id": website.id,
                "priority": 10,
                "arch_db": (
                    '<xpath expr="//header//nav" position="replace">'
                    '<div class="legacy-header-shell"/>'
                    "</xpath>"
                ),
            }
        )

        response = self.url_open("/web/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn("facodi-header", response.text)
        self.assertIn("facodi-nav-shell", response.text)
        self.assertIn("o_header_mobile", response.text)
