/** @odoo-module **/

const STORAGE_KEY = "facodi.study.panel";

function readPreferredPanel() {
    try {
        return window.localStorage.getItem(STORAGE_KEY);
    } catch {
        return null;
    }
}

function writePreferredPanel(name) {
    try {
        window.localStorage.setItem(STORAGE_KEY, name);
    } catch {
        // Storage is optional. The study surface remains fully usable without it.
    }
}

function initStudyPlayer(root) {
    if (root.dataset.facodiStudyEnhanced === "true") {
        return;
    }
    root.dataset.facodiStudyEnhanced = "true";
    root.classList.add("facodi-study-player--enhanced");
    document.body.classList.add("o_wslides_body");

    const sidebar = root.querySelector(".facodi-study-player__index");
    const nativeToggles = root.querySelectorAll(".o_wslides_fs_toggle_sidebar");

    const syncSidebarState = () => {
        if (!sidebar) {
            return;
        }
        const expanded = !sidebar.classList.contains("o_wslides_fs_sidebar_hidden");
        nativeToggles.forEach((toggle) => {
            toggle.setAttribute("aria-controls", sidebar.id || "facodi-study-index");
            toggle.setAttribute("aria-expanded", String(expanded));
        });
    };

    if (sidebar) {
        syncSidebarState();
        const sidebarObserver = new MutationObserver(syncSidebarState);
        sidebarObserver.observe(sidebar, {
            attributes: true,
            attributeFilter: ["class"],
        });
        nativeToggles.forEach((toggle) => {
            toggle.addEventListener("click", () => {
                window.requestAnimationFrame(syncSidebarState);
            });
        });
    }

    const tabs = Array.from(root.querySelectorAll("[data-facodi-study-tab]"));
    const panels = Array.from(root.querySelectorAll("[data-facodi-study-panel]"));
    const panelNames = new Set(panels.map((panel) => panel.dataset.facodiStudyPanel));

    const setActivePanel = (name, persist = true) => {
        if (!panelNames.has(name)) {
            return;
        }

        tabs.forEach((tab) => {
            const active = tab.dataset.facodiStudyTab === name;
            tab.classList.toggle("is-active", active);
            tab.setAttribute("aria-selected", String(active));
            tab.setAttribute("tabindex", active ? "0" : "-1");
        });

        panels.forEach((panel) => {
            const active = panel.dataset.facodiStudyPanel === name;
            panel.hidden = !active;
            panel.setAttribute("aria-hidden", String(!active));
        });

        if (persist) {
            writePreferredPanel(name);
        }
    };

    if (tabs.length && panels.length) {
        const defaultPanel =
            readPreferredPanel() && panelNames.has(readPreferredPanel())
                ? readPreferredPanel()
                : tabs.find((tab) => tab.getAttribute("aria-selected") === "true")
                    ?.dataset.facodiStudyTab || tabs[0].dataset.facodiStudyTab;

        setActivePanel(defaultPanel, false);

        tabs.forEach((tab, index) => {
            tab.addEventListener("click", () => {
                setActivePanel(tab.dataset.facodiStudyTab);
            });

            tab.addEventListener("keydown", (event) => {
                let targetIndex = null;
                if (event.key === "ArrowRight") {
                    targetIndex = (index + 1) % tabs.length;
                } else if (event.key === "ArrowLeft") {
                    targetIndex = (index - 1 + tabs.length) % tabs.length;
                } else if (event.key === "Home") {
                    targetIndex = 0;
                } else if (event.key === "End") {
                    targetIndex = tabs.length - 1;
                }

                if (targetIndex !== null) {
                    tabs[targetIndex].focus();
                    setActivePanel(tabs[targetIndex].dataset.facodiStudyTab);
                }
            });
        });
    }

    const activeLesson = root.querySelector(".o_wslides_fs_sidebar_list_item.active");
    if (activeLesson) {
        window.requestAnimationFrame(() => {
            activeLesson.scrollIntoView({
                block: "nearest",
                inline: "nearest",
                behavior: "auto",
            });
        });
    }
}

function initStudyPlayers() {
    document.querySelectorAll(".facodi-study-player").forEach(initStudyPlayer);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initStudyPlayers, { once: true });
} else {
    initStudyPlayers();
}
