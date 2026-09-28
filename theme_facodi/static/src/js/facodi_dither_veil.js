/** @odoo-module **/

/**
 * FACODI Dither Veil
 *
 * Native Odoo/Canvas adaptation of the interaction idea behind React Bits'
 * Dither Veil: an image is rendered as a coarse duotone dither and pointer
 * movement reveals the original colour underneath for a short-lived trail.
 *
 * No React/WebGL runtime is mounted in Website. The effect is deliberately
 * scoped to the hero visual stage, pauses offscreen and becomes static on
 * coarse pointers or when reduced motion is requested.
 */

const SELECTOR = "[data-facodi-dither-veil]";

function hexToRgb(hex) {
    const value = String(hex || "").trim().replace("#", "");
    const normalized = value.length === 3
        ? value.split("").map((part) => part + part).join("")
        : value.slice(0, 6);
    const parsed = Number.parseInt(normalized, 16);
    if (!Number.isFinite(parsed)) {
        return { r: 20, g: 40, b: 70 };
    }
    return {
        r: (parsed >> 16) & 255,
        g: (parsed >> 8) & 255,
        b: parsed & 255,
    };
}

function coverRect(width, height, imageWidth, imageHeight) {
    const scale = Math.max(width / imageWidth, height / imageHeight);
    const drawWidth = imageWidth * scale;
    const drawHeight = imageHeight * scale;
    return {
        x: (width - drawWidth) / 2,
        y: (height - drawHeight) / 2,
        width: drawWidth,
        height: drawHeight,
    };
}

class FacodiDitherVeil {
    constructor(root) {
        this.root = root;
        this.canvas = root.querySelector("canvas");
        this.context = this.canvas?.getContext("2d") || null;
        this.source = root.dataset.src || "";
        this.pixelSize = Math.max(3, Number(root.dataset.pixelSize || 5));
        this.radius = Math.max(80, Number(root.dataset.revealRadius || 170));
        this.linger = Math.max(250, Number(root.dataset.linger || 1050));
        this.ink = hexToRgb(root.dataset.inkColor || "#142846");
        this.paper = hexToRgb(root.dataset.paperColor || "#F9FAFB");
        this.rim = root.dataset.rimColor || "#37BED2";
        this.reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        this.coarsePointer = window.matchMedia("(pointer: coarse)").matches;

        this.image = null;
        this.width = 0;
        this.height = 0;
        this.dpr = 1;
        this.visible = true;
        this.frame = null;
        this.trail = [];
        this.resizeObserver = null;
        this.intersectionObserver = null;

        this.colorCanvas = document.createElement("canvas");
        this.ditherCanvas = document.createElement("canvas");
        this.maskCanvas = document.createElement("canvas");
        this.revealCanvas = document.createElement("canvas");

        this.onPointerMove = this.onPointerMove.bind(this);
        this.onPointerDown = this.onPointerDown.bind(this);
        this.resize = this.resize.bind(this);
        this.render = this.render.bind(this);
    }

    start() {
        if (!this.canvas || !this.context || !this.source || this.root.dataset.facodiDitherVeilReady === "true") {
            return;
        }
        this.root.dataset.facodiDitherVeilReady = "true";

        if ("ResizeObserver" in window) {
            this.resizeObserver = new ResizeObserver(this.resize);
            this.resizeObserver.observe(this.root);
        } else {
            window.addEventListener("resize", this.resize, { passive: true });
        }

        if ("IntersectionObserver" in window) {
            this.intersectionObserver = new IntersectionObserver(([entry]) => {
                this.visible = entry.isIntersecting;
                if (this.visible) {
                    this.wake();
                } else if (this.frame) {
                    window.cancelAnimationFrame(this.frame);
                    this.frame = null;
                }
            }, { rootMargin: "120px" });
            this.intersectionObserver.observe(this.root);
        }

        if (!this.reducedMotion && !this.coarsePointer) {
            this.root.addEventListener("pointermove", this.onPointerMove, { passive: true });
            this.root.addEventListener("pointerdown", this.onPointerDown, { passive: true });
        }

        const image = new Image();
        image.decoding = "async";
        image.onload = () => {
            this.image = image;
            this.resize();
            this.wake();
        };
        image.src = this.source;
    }

    resize() {
        if (!this.image || !this.canvas || !this.context) {
            return;
        }
        const rect = this.root.getBoundingClientRect();
        if (!rect.width || !rect.height) {
            return;
        }

        this.width = Math.round(rect.width);
        this.height = Math.round(rect.height);
        this.dpr = Math.min(window.devicePixelRatio || 1, this.coarsePointer ? 1.25 : 1.75);

        this.canvas.width = Math.round(this.width * this.dpr);
        this.canvas.height = Math.round(this.height * this.dpr);
        this.canvas.style.width = `${this.width}px`;
        this.canvas.style.height = `${this.height}px`;
        this.context.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);

        for (const layer of [this.colorCanvas, this.maskCanvas, this.revealCanvas]) {
            layer.width = this.width;
            layer.height = this.height;
        }

        this.buildColorLayer();
        this.buildDitherLayer();
        this.drawBase();
    }

    buildColorLayer() {
        const context = this.colorCanvas.getContext("2d");
        if (!context || !this.image) {
            return;
        }
        const rect = coverRect(
            this.width,
            this.height,
            this.image.naturalWidth || this.image.width,
            this.image.naturalHeight || this.image.height
        );
        context.clearRect(0, 0, this.width, this.height);
        context.drawImage(this.image, rect.x, rect.y, rect.width, rect.height);

        // A restrained FACODI cyan wash keeps arbitrary source imagery inside
        // the theme palette while preserving enough original colour to reveal.
        context.globalCompositeOperation = "soft-light";
        context.fillStyle = "rgba(55, 190, 210, 0.20)";
        context.fillRect(0, 0, this.width, this.height);
        context.globalCompositeOperation = "source-over";
    }

    buildDitherLayer() {
        const columns = Math.max(1, Math.ceil(this.width / this.pixelSize));
        const rows = Math.max(1, Math.ceil(this.height / this.pixelSize));
        this.ditherCanvas.width = columns;
        this.ditherCanvas.height = rows;

        const sample = document.createElement("canvas");
        sample.width = columns;
        sample.height = rows;
        const sampleContext = sample.getContext("2d", { willReadFrequently: true });
        const ditherContext = this.ditherCanvas.getContext("2d");
        if (!sampleContext || !ditherContext) {
            return;
        }

        sampleContext.drawImage(this.colorCanvas, 0, 0, columns, rows);
        const imageData = sampleContext.getImageData(0, 0, columns, rows);
        const data = imageData.data;
        const luminance = new Float32Array(columns * rows);

        for (let index = 0; index < luminance.length; index++) {
            const offset = index * 4;
            luminance[index] =
                (0.2126 * data[offset] + 0.7152 * data[offset + 1] + 0.0722 * data[offset + 2]) / 255;
        }

        // Floyd-Steinberg error diffusion, serpentine to reduce directional bias.
        for (let y = 0; y < rows; y++) {
            const reverse = Boolean(y & 1);
            for (let step = 0; step < columns; step++) {
                const x = reverse ? columns - 1 - step : step;
                const index = y * columns + x;
                const oldValue = luminance[index];
                const nextValue = oldValue >= 0.52 ? 1 : 0;
                const error = oldValue - nextValue;
                luminance[index] = nextValue;

                const spread = (nx, ny, weight) => {
                    if (nx < 0 || nx >= columns || ny < 0 || ny >= rows) {
                        return;
                    }
                    luminance[ny * columns + nx] += error * weight;
                };
                const direction = reverse ? -1 : 1;
                spread(x + direction, y, 7 / 16);
                spread(x - direction, y + 1, 3 / 16);
                spread(x, y + 1, 5 / 16);
                spread(x + direction, y + 1, 1 / 16);
            }
        }

        const output = ditherContext.createImageData(columns, rows);
        for (let index = 0; index < luminance.length; index++) {
            const color = luminance[index] >= 0.5 ? this.paper : this.ink;
            const offset = index * 4;
            output.data[offset] = color.r;
            output.data[offset + 1] = color.g;
            output.data[offset + 2] = color.b;
            output.data[offset + 3] = 255;
        }
        ditherContext.putImageData(output, 0, 0);
    }

    localPointer(event) {
        const rect = this.root.getBoundingClientRect();
        return {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top,
        };
    }

    onPointerMove(event) {
        const point = this.localPointer(event);
        const now = performance.now();
        const last = this.trail[this.trail.length - 1];
        if (!last || Math.hypot(point.x - last.x, point.y - last.y) > 8 || now - last.time > 45) {
            this.trail.push({ ...point, time: now, strength: 1 });
            if (this.trail.length > 44) {
                this.trail.splice(0, this.trail.length - 44);
            }
        }
        this.wake();
    }

    onPointerDown(event) {
        if (event.pointerType === "mouse" && event.button !== 0) {
            return;
        }
        const point = this.localPointer(event);
        const now = performance.now();
        this.trail.push({ ...point, time: now, strength: 1.35 });
        this.trail.push({ ...point, time: now + 35, strength: 1.1 });
        this.wake();
    }

    wake() {
        if (!this.visible || this.frame || !this.image) {
            return;
        }
        this.frame = window.requestAnimationFrame(this.render);
    }

    drawBase() {
        if (!this.context || !this.width || !this.height) {
            return;
        }
        this.context.clearRect(0, 0, this.width, this.height);
        this.context.imageSmoothingEnabled = false;
        this.context.drawImage(this.ditherCanvas, 0, 0, this.width, this.height);
        this.context.imageSmoothingEnabled = true;
    }

    render(now) {
        this.frame = null;
        if (!this.visible || !this.context) {
            return;
        }

        this.drawBase();

        if (this.reducedMotion || this.coarsePointer || !this.trail.length) {
            return;
        }

        this.trail = this.trail.filter((point) => now - point.time < this.linger);
        if (!this.trail.length) {
            return;
        }

        const mask = this.maskCanvas.getContext("2d");
        const reveal = this.revealCanvas.getContext("2d");
        if (!mask || !reveal) {
            return;
        }

        mask.clearRect(0, 0, this.width, this.height);
        for (const point of this.trail) {
            const age = Math.max(0, now - point.time);
            const life = Math.max(0, 1 - age / this.linger);
            const radius = this.radius * (0.55 + 0.45 * point.strength);
            const gradient = mask.createRadialGradient(point.x, point.y, 0, point.x, point.y, radius);
            gradient.addColorStop(0, `rgba(255,255,255,${Math.min(1, life * point.strength)})`);
            gradient.addColorStop(0.58, `rgba(255,255,255,${life * 0.78})`);
            gradient.addColorStop(1, "rgba(255,255,255,0)");
            mask.fillStyle = gradient;
            mask.fillRect(point.x - radius, point.y - radius, radius * 2, radius * 2);
        }

        reveal.clearRect(0, 0, this.width, this.height);
        reveal.drawImage(this.colorCanvas, 0, 0);
        reveal.globalCompositeOperation = "destination-in";
        reveal.drawImage(this.maskCanvas, 0, 0);
        reveal.globalCompositeOperation = "source-over";

        this.context.drawImage(this.revealCanvas, 0, 0);

        const head = this.trail[this.trail.length - 1];
        const headLife = Math.max(0, 1 - (now - head.time) / this.linger);
        if (headLife > 0.05) {
            this.context.beginPath();
            this.context.arc(head.x, head.y, this.radius * 0.58, 0, Math.PI * 2);
            this.context.strokeStyle = this.rim;
            this.context.globalAlpha = headLife * 0.38;
            this.context.lineWidth = 1.5;
            this.context.stroke();
            this.context.globalAlpha = 1;
        }

        this.wake();
    }
}

function initFacodiDitherVeils() {
    document.querySelectorAll(SELECTOR).forEach((root) => {
        new FacodiDitherVeil(root).start();
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initFacodiDitherVeils, { once: true });
} else {
    initFacodiDitherVeils();
}
