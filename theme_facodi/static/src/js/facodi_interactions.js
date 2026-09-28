/** @odoo-module **/

const REDUCED_QUERY = "(prefers-reduced-motion: reduce)";
const SPOTLIGHT_SELECTOR = ".facodi-site [data-facodi-spotlight='1']";

function initFacodiSpotlight() {
    const cards = [...document.querySelectorAll(SPOTLIGHT_SELECTOR)];
    if (!cards.length || window.matchMedia(REDUCED_QUERY).matches) {
        return;
    }

    cards.forEach((card) => {
        let frame = null;
        const update = (event) => {
            const rect = card.getBoundingClientRect();
            const x = ((event.clientX - rect.left) / rect.width) * 100;
            const y = ((event.clientY - rect.top) / rect.height) * 100;
            if (frame) {
                cancelAnimationFrame(frame);
            }
            frame = requestAnimationFrame(() => {
                card.style.setProperty("--facodi-spotlight-x", `${x}%`);
                card.style.setProperty("--facodi-spotlight-y", `${y}%`);
            });
        };
        const clear = () => {
            card.style.removeProperty("--facodi-spotlight-x");
            card.style.removeProperty("--facodi-spotlight-y");
        };
        card.addEventListener("pointermove", update, { passive: true });
        card.addEventListener("pointerleave", clear, { passive: true });
        card.addEventListener("blur", clear, true);
    });
}

function initFacodiScramble() {
    const items = [...document.querySelectorAll(".facodi-site [data-facodi-scramble='1']")];
    if (!items.length || window.matchMedia(REDUCED_QUERY).matches) {
        return;
    }
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    items.forEach((item) => {
        const original = item.textContent.trim();
        if (!original || original.length > 28) {
            return;
        }
        let running = false;
        const run = () => {
            if (running) {
                return;
            }
            running = true;
            let step = 0;
            const total = Math.max(8, Math.min(16, original.length));
            const timer = window.setInterval(() => {
                step += 1;
                const reveal = Math.floor((step / total) * original.length);
                item.textContent = original
                    .split("")
                    .map((char, index) => {
                        if (char === " " || index < reveal) {
                            return char;
                        }
                        return chars[Math.floor(Math.random() * chars.length)];
                    })
                    .join("");
                if (step >= total) {
                    window.clearInterval(timer);
                    item.textContent = original;
                    running = false;
                }
            }, 32);
        };
        item.addEventListener("mouseenter", run, { passive: true });
        item.addEventListener("focus", run);
    });
}

function initFacodiInteractions() {
    initFacodiSpotlight();
    initFacodiScramble();
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initFacodiInteractions, { once: true });
} else {
    initFacodiInteractions();
}
