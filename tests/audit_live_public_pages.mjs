// rerun-after-deploy: 2026-09-26T14:40Z
import fs from "node:fs/promises";
import path from "node:path";
import { chromium } from "playwright-core";

const base = "https://facodi.com";
const executablePath = process.env.FACODI_BROWSER_CHROME_BIN;
if (!executablePath) throw new Error("FACODI_BROWSER_CHROME_BIN missing");
const outDir = process.env.FACODI_LIVE_AUDIT_DIR || "live-audit";
await fs.mkdir(outDir, { recursive: true });

const browser = await chromium.launch({
  executablePath,
  headless: true,
  args: ["--no-sandbox", "--disable-dev-shm-usage"],
});

const seedPaths = [
  "/pt/",
  "/pt/sobre",
  "/pt/facodi",
  "/pt/contribuir",
  "/pt/blog",
  "/pt/contactus",
  "/pt/slides",
  "/pt/roadmaps",
  "/pt/unidades-curriculares",
  "/pt/privacy",
  "/pt/cookie-policy",
  "/pt/terms",
];

const normalize = (href) => {
  try {
    const u = new URL(href, base);
    if (u.origin !== base) return null;
    if (!u.pathname.startsWith("/pt/") && u.pathname !== "/pt") return null;
    if (/\.(pdf|png|jpe?g|webp|svg|zip|xml)$/i.test(u.pathname)) return null;
    u.hash = "";
    u.search = "";
    return u.pathname.replace(/\/$/, "") || "/pt";
  } catch {
    return null;
  }
};

const discovered = new Set(seedPaths.map(x => x.replace(/\/$/, "") || "/pt"));

async function crawlLinks() {
  const context = await browser.newContext({ viewport: { width: 1440, height: 1200 } });
  const page = await context.newPage();
  for (const route of ["/pt/", "/pt/sobre", "/pt/contribuir"]) {
    try {
      const res = await page.goto(base + route, { waitUntil: "domcontentloaded", timeout: 30000 });
      if (!res || res.status() >= 400) continue;
      const hrefs = await page.locator("a[href]").evaluateAll(nodes => nodes.map(n => n.getAttribute("href")));
      for (const href of hrefs) {
        const normalized = normalize(href);
        if (normalized) discovered.add(normalized);
      }
    } catch {}
  }
  await context.close();
}
await crawlLinks();

const routes = [...discovered]
  .filter(Boolean)
  .filter(route => !route.includes("/web/"))
  .slice(0, 60)
  .sort();

const viewports = {
  desktop: { width: 1440, height: 1200 },
  mobile: { width: 390, height: 844 },
  narrow: { width: 320, height: 700 },
};

const report = [];
for (const route of routes) {
  for (const [sizeName, viewport] of Object.entries(viewports)) {
    if (sizeName === "narrow" && !["/pt", "/pt/contribuir", "/pt/sobre", "/pt/blog", "/pt/contactus"].includes(route)) continue;
    const context = await browser.newContext({ viewport });
    const page = await context.newPage();
    const consoleErrors = [];
    const failedRequests = [];
    page.on("console", msg => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });
    page.on("requestfailed", req => {
      const failure = req.failure();
      failedRequests.push({ url: req.url(), error: failure?.errorText || "unknown" });
    });

    let status = null;
    let loadError = null;
    try {
      const response = await page.goto(base + route, { waitUntil: "domcontentloaded", timeout: 30000 });
      status = response?.status() ?? null;
      await page.waitForLoadState("networkidle", { timeout: 5000 }).catch(() => {});
    } catch (err) {
      loadError = String(err);
    }

    const audit = await page.evaluate(() => {
      const root = document.documentElement;
      const body = document.body;
      const allFacodi = [...document.querySelectorAll('[class*="facodi-"]')];
      const visibleFacodi = allFacodi
        .filter(el => {
          const r = el.getBoundingClientRect();
          const s = getComputedStyle(el);
          return s.display !== "none" && s.visibility !== "hidden" && r.width > 1 && r.height > 1;
        })
        .slice(0, 120)
        .map(el => {
          const r = el.getBoundingClientRect();
          const s = getComputedStyle(el);
          return {
            tag: el.tagName.toLowerCase(),
            cls: [...el.classList].filter(c => c.startsWith("facodi-")).join(" "),
            width: Math.round(r.width),
            height: Math.round(r.height),
            bg: s.backgroundColor,
            borderTop: s.borderTop,
            borderRadius: s.borderRadius,
            boxShadow: s.boxShadow,
            transform: s.transform,
            position: s.position,
          };
        });

      const footer = document.querySelector("footer#bottom, .facodi-footer-campus, .facodi-footer");
      const footerStyle = footer ? getComputedStyle(footer) : null;
      const sections = [...document.querySelectorAll("#wrap > section, #wrap > main, #wrap > div, main > section")]
        .slice(0, 80)
        .map(el => {
          const r = el.getBoundingClientRect();
          return {
            tag: el.tagName.toLowerCase(),
            id: el.id || "",
            cls: el.className?.toString().slice(0, 240) || "",
            height: Math.round(r.height),
          };
        });

      const suspect = allFacodi
        .filter(el => {
          const r = el.getBoundingClientRect();
          const s = getComputedStyle(el);
          if (s.display === "none" || s.visibility === "hidden") return false;
          if (el.hasAttribute("aria-hidden")) return false;
          return (r.width > 0 && r.width < 8) || (r.height > 0 && r.height < 8);
        })
        .slice(0, 40)
        .map(el => ({ tag: el.tagName.toLowerCase(), cls: el.className?.toString() || "" }));

      return {
        title: document.title,
        lang: document.documentElement.lang,
        textLength: body?.innerText?.trim().length || 0,
        scrollWidth: root.scrollWidth,
        viewportWidth: window.innerWidth,
        overflow: root.scrollWidth > window.innerWidth + 1,
        footerBackground: footerStyle?.backgroundColor || null,
        footerColor: footerStyle?.color || null,
        facodiCount: allFacodi.length,
        visibleFacodi,
        sections,
        suspect,
      };
    }).catch(() => ({
      title: "",
      textLength: 0,
      scrollWidth: 0,
      viewportWidth: viewport.width,
      overflow: false,
      footerBackground: null,
      footerColor: null,
      facodiCount: 0,
      visibleFacodi: [],
      sections: [],
      suspect: [],
    }));

    const item = {
      route,
      sizeName,
      viewport,
      status,
      loadError,
      consoleErrors: consoleErrors.slice(0, 20),
      failedRequests: failedRequests.slice(0, 20),
      ...audit,
    };
    report.push(item);

    if (route === "/pt/contribuir" || route === "/pt/sobre" || route === "/pt" || route === "/pt/blog") {
      const file = path.join(outDir, `${route.replaceAll("/", "_").replace(/^_+/, "") || "pt"}-${sizeName}.png`);
      await page.screenshot({ path: file, fullPage: true }).catch(() => {});
    }

    console.log("AUDIT", JSON.stringify({
      route,
      sizeName,
      finalUrl: page.url(),
      status,
      overflow: item.overflow,
      footerBackground: item.footerBackground,
      facodiCount: item.facodiCount,
      consoleErrors: item.consoleErrors.length,
      failedRequests: item.failedRequests.length,
      title: item.title,
      finalUrl: item.finalUrl,
      contributionClasses: route === "/pt/contribuir"
        ? item.visibleFacodi.map(x => x.cls).filter(Boolean).slice(0, 40)
        : undefined,
      sections: route === "/pt/contribuir" ? item.sections : undefined,
    }));

    await context.close();
  }
}

await fs.writeFile(path.join(outDir, "report.json"), JSON.stringify({ routes, report }, null, 2));

const failures = report.filter(item =>
  (item.status !== null && item.status >= 400) ||
  item.loadError ||
  item.overflow ||
  item.footerBackground && item.footerBackground !== "rgb(11, 19, 37)"
);

console.log("SUMMARY", JSON.stringify({
  routes,
  checked: report.length,
  failures: failures.map(x => ({
    route: x.route,
    sizeName: x.sizeName,
    status: x.status,
    overflow: x.overflow,
    footerBackground: x.footerBackground,
    loadError: x.loadError,
  })),
}, null, 2));

await browser.close();
