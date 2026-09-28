/** @odoo-module **/

const MOTION_SELECTOR = ".facodi-home-v4 [data-facodi-motion]";

function initFacodiMotion() {
    const items = [...document.querySelectorAll(MOTION_SELECTOR)];
    if (!items.length) {
        return;
    }

    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || !("IntersectionObserver" in window)) {
        items.forEach((item) => item.classList.add("is-visible"));
        return;
    }

    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) {
                    return;
                }
                const item = entry.target;
                const delay = Number(item.dataset.facodiMotionDelay || 0);
                window.setTimeout(() => item.classList.add("is-visible"), Math.max(0, delay));
                observer.unobserve(item);
            });
        },
        {
            rootMargin: "0px 0px -8% 0px",
            threshold: 0.12,
        }
    );

    items.forEach((item) => observer.observe(item));
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initFacodiMotion, { once: true });
} else {
    initFacodiMotion();
}
