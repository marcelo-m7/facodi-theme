/** @odoo-module **/

/**
 * FACODI Dot Grid
 *
 * A dependency-free Odoo port of the interaction model used by React Bits'
 * Dot Grid: a canvas dot field reacts to pointer proximity and click shocks.
 *
 * The implementation is intentionally native rather than mounting React/GSAP
 * inside Website. This keeps the theme standard-first, compatible with the
 * Odoo asset pipeline and cheap to ship on every public page load.
 */

const SELECTOR = "[data-facodi-dot-grid]";

function hexToRgb(hex) {
    const match = String(hex || "").trim().match(
        /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i
    );
    if (!match) {
        return { r: 20, g: 40, b: 70 };
    }
    return {
        r: Number.parseInt(match[1], 16),
        g: Number.parseInt(match[2], 16),
        b: Number.parseInt(match[3], 16),
    };
}

function mixColor(a, b, amount) {
    const t = Math.max(0, Math.min(1, amount));
    const channel = (from, to) => Math.round(from + (to - from) * t);
    return `rgb(${channel(a.r, b.r)}, ${channel(a.g, b.g)}, ${channel(a.b, b.b)})`;
}

class FacodiDotGrid {
    constructor(root) {
        this.root = root;
        this.canvas = root.querySelector("canvas");
        this.context = this.canvas?.getContext("2d") || null;
        this.host = root.closest(".facodi-hero") || root.parentElement;
        this.dots = [];
        this.pointer = { x: -10000, y: -10000, active: false };
        this.frame = null;
        this.resizeObserver = null;
        this.intersectionObserver = null;
        this.isVisible = true;
        this.animate = true;

        this.dotSize = Number(root.dataset.dotSize || 3);
        this.gap = Number(root.dataset.gap || 24);
        this.proximity = Number(root.dataset.proximity || 125);
        this.shockRadius = Number(root.dataset.shockRadius || 180);
        this.shockStrength = Number(root.dataset.shockStrength || 4.5);
        this.base = hexToRgb(root.dataset.baseColor || "#3979C8");
        this.active = hexToRgb(root.dataset.activeColor || "#37BED2");
        this.reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        this.coarsePointer = window.matchMedia("(pointer: coarse)").matches;
        this.animate = !this.reducedMotion && !this.coarsePointer;

        this.onPointerMove = this.onPointerMove.bind(this);
        this.onPointerLeave = this.onPointerLeave.bind(this);
        this.onPointerDown = this.onPointerDown.bind(this);
        this.resize = this.resize.bind(this);
        this.draw = this.draw.bind(this);
    }

    start() {
        if (!this.canvas || !this.context || this.root.dataset.facodiDotGridReady === "true") {
            return;
        }
        this.root.dataset.facodiDotGridReady = "true";

        this.resize();
        if ("ResizeObserver" in window) {
            this.resizeObserver = new ResizeObserver(this.resize);
            this.resizeObserver.observe(this.root);
        } else {
            window.addEventListener("resize", this.resize, { passive: true });
        }

        if (this.animate && this.host) {
            this.host.addEventListener("pointermove", this.onPointerMove, { passive: true });
            this.host.addEventListener("pointerleave", this.onPointerLeave, { passive: true });
            this.host.addEventListener("pointerdown", this.onPointerDown, { passive: true });
        }

        if ("IntersectionObserver" in window && this.animate) {
            this.isVisible = false;
            this.intersectionObserver = new IntersectionObserver(
                (entries) => {
                    const entry = entries[0];
                    this.isVisible = Boolean(entry?.isIntersecting);
                    if (this.isVisible && this.frame === null) {
                        this.draw();
                    } else if (!this.isVisible && this.frame !== null) {
                        window.cancelAnimationFrame(this.frame);
                        this.frame = null;
                    }
                },
                { rootMargin: "120px 0px" }
            );
            this.intersectionObserver.observe(this.root);
        } else {
            this.draw();
        }
    }

    resize() {
        const rect = this.root.getBoundingClientRect();
        if (!rect.width || !rect.height || !this.canvas || !this.context) {
            return;
        }
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        this.canvas.width = Math.round(rect.width * dpr);
        this.canvas.height = Math.round(rect.height * dpr);
        this.canvas.style.width = `${rect.width}px`;
        this.canvas.style.height = `${rect.height}px`;
        this.context.setTransform(dpr, 0, 0, dpr, 0, 0);

        const cell = this.dotSize + this.gap;
        const columns = Math.max(1, Math.floor((rect.width + this.gap) / cell));
        const rows = Math.max(1, Math.floor((rect.height + this.gap) / cell));
        const gridWidth = columns * cell - this.gap;
        const gridHeight = rows * cell - this.gap;
        const startX = (rect.width - gridWidth) / 2 + this.dotSize / 2;
        const startY = (rect.height - gridHeight) / 2 + this.dotSize / 2;

        this.dots = [];
        for (let row = 0; row < rows; row++) {
            for (let column = 0; column < columns; column++) {
                this.dots.push({
                    x: startX + column * cell,
                    y: startY + row * cell,
                    offsetX: 0,
                    offsetY: 0,
                    velocityX: 0,
                    velocityY: 0,
                });
            }
        }
    }

    localPointer(event) {
        const rect = this.root.getBoundingClientRect();
        return {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top,
        };
    }

    onPointerMove(event) {
        const pointer = this.localPointer(event);
        this.pointer.x = pointer.x;
        this.pointer.y = pointer.y;
        this.pointer.active = true;
    }

    onPointerLeave() {
        this.pointer.active = false;
    }

    onPointerDown(event) {
        const pointer = this.localPointer(event);
        for (const dot of this.dots) {
            const dx = dot.x - pointer.x;
            const dy = dot.y - pointer.y;
            const distance = Math.hypot(dx, dy);
            if (!distance || distance >= this.shockRadius) {
                continue;
            }
            const falloff = 1 - distance / this.shockRadius;
            const force = this.shockStrength * falloff;
            dot.velocityX += (dx / distance) * force;
            dot.velocityY += (dy / distance) * force;
        }
    }

    draw() {
        const context = this.context;
        const canvas = this.canvas;
        if (!context || !canvas) {
            return;
        }

        const width = Number.parseFloat(canvas.style.width) || 0;
        const height = Number.parseFloat(canvas.style.height) || 0;
        context.clearRect(0, 0, width, height);

        const proximity = this.proximity;
        const spring = this.reducedMotion ? 0 : 0.055;
        const damping = 0.86;

        for (const dot of this.dots) {
            let intensity = 0;
            let targetX = 0;
            let targetY = 0;

            if (this.pointer.active && !this.reducedMotion) {
                const dx = dot.x - this.pointer.x;
                const dy = dot.y - this.pointer.y;
                const distance = Math.hypot(dx, dy);
                if (distance < proximity) {
                    intensity = 1 - distance / proximity;
                    const safeDistance = Math.max(distance, 1);
                    const displacement = intensity * 10;
                    targetX = (dx / safeDistance) * displacement;
                    targetY = (dy / safeDistance) * displacement;
                }
            }

            if (!this.reducedMotion) {
                dot.velocityX += (targetX - dot.offsetX) * spring;
                dot.velocityY += (targetY - dot.offsetY) * spring;
                dot.velocityX *= damping;
                dot.velocityY *= damping;
                dot.offsetX += dot.velocityX;
                dot.offsetY += dot.velocityY;
            }

            context.beginPath();
            context.arc(
                dot.x + dot.offsetX,
                dot.y + dot.offsetY,
                this.dotSize / 2,
                0,
                Math.PI * 2
            );
            context.fillStyle = mixColor(this.base, this.active, intensity);
            context.globalAlpha = 0.22 + intensity * 0.58;
            context.fill();
        }

        context.globalAlpha = 1;
        if (this.animate && this.isVisible) {
            this.frame = window.requestAnimationFrame(this.draw);
        } else {
            this.frame = null;
        }
    }
}

function initFacodiDotGrids() {
    document.querySelectorAll(SELECTOR).forEach((root) => {
        new FacodiDotGrid(root).start();
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initFacodiDotGrids, { once: true });
} else {
    initFacodiDotGrids();
}
