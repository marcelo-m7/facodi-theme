/** @odoo-module **/

const SWITCHER_SELECTOR = "[data-facodi-catalogue-switcher]";
const STAGE_SELECTOR = "[data-facodi-catalogue-stage]";
const ENDPOINT = "/facodi/home/catalogue-fragment";

function initCatalogueSwitcher(root) {
    const section = root.closest(".s_facodi_course_showcase");
    const stage = section?.querySelector(STAGE_SELECTOR);
    if (!stage || root.dataset.facodiCatalogueReady === "true") {
        return;
    }
    root.dataset.facodiCatalogueReady = "true";

    const buttons = [...root.querySelectorAll("[data-facodi-content-type]")];
    const cache = new Map();
    const coursePanel = stage.querySelector('[data-facodi-catalogue-panel="courses"]');
    if (coursePanel) {
        cache.set("courses", coursePanel.innerHTML);
    }

    const setActiveButton = (type) => {
        buttons.forEach((button) => {
            const active = button.dataset.facodiContentType === type;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-pressed", active ? "true" : "false");
        });
    };

    const showPanel = (type, html = null) => {
        let panel = stage.querySelector(`[data-facodi-catalogue-panel="${type}"]`);
        if (!panel) {
            return;
        }
        if (html !== null) {
            panel.innerHTML = html;
        }
        stage.querySelectorAll("[data-facodi-catalogue-panel]").forEach((candidate) => {
            const active = candidate === panel;
            candidate.hidden = !active;
            candidate.classList.toggle("is-active", active);
        });
        panel.classList.remove("facodi-catalogue-panel--enter");
        void panel.offsetWidth;
        panel.classList.add("facodi-catalogue-panel--enter");
        setActiveButton(type);
    };

    const load = async (type) => {
        if (cache.has(type)) {
            showPanel(type, cache.get(type));
            return;
        }

        const controller = new AbortController();
        stage._facodiAbortController?.abort();
        stage._facodiAbortController = controller;
        stage.setAttribute("aria-busy", "true");
        root.classList.add("is-loading");

        try {
            const response = await fetch(`${ENDPOINT}?type=${encodeURIComponent(type)}`, {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept": "text/html",
                },
                credentials: "same-origin",
                signal: controller.signal,
            });
            if (!response.ok) {
                throw new Error(`Catalogue fragment failed with ${response.status}`);
            }
            const html = await response.text();
            cache.set(type, html);
            showPanel(type, html);
        } catch (error) {
            if (error.name !== "AbortError") {
                const panel = stage.querySelector(`[data-facodi-catalogue-panel="${type}"]`);
                if (panel) {
                    panel.innerHTML = '<div class="facodi-empty-state"><h3>Could not load this catalogue view</h3><p>Please try again in a moment.</p></div>';
                    showPanel(type, panel.innerHTML);
                }
            }
        } finally {
            if (stage._facodiAbortController === controller) {
                stage.removeAttribute("aria-busy");
                root.classList.remove("is-loading");
            }
        }
    };

    buttons.forEach((button) => {
        button.addEventListener("click", () => load(button.dataset.facodiContentType || "courses"));
    });
}

function init() {
    document.querySelectorAll(SWITCHER_SELECTOR).forEach(initCatalogueSwitcher);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
} else {
    init();
}
