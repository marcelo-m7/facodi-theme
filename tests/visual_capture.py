#!/usr/bin/env python3
"""Capture real Chromium screenshots and check page-level overflow on Odoo CI.

Run inside tests/Dockerfile.browser with the Odoo HTTP server already listening
on localhost:8069. Only captures routes that exist in the disposable test DB.
Never targets production or sends page data to external services.
"""
import base64
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request

import websocket

OUTPUT = Path(os.environ.get("FACODI_VISUAL_DIR", "/tmp/facodi-visual"))
BASE = os.environ.get("FACODI_VISUAL_BASE", "http://127.0.0.1:8069").rstrip("/")
PAGES = [("/", "home"), ("/about", "about"), ("/partnerships", "partnerships"), ("/blog", "blog"), ("/slides", "slides")]
WIDTHS = [320, 390, 768, 1440]
HEIGHT = 900


def request(url, method="GET", timeout=10):
    with urllib.request.urlopen(urllib.request.Request(url, method=method), timeout=timeout) as r:
        return r.read()


def wait_for_odoo():
    for _ in range(90):
        try:
            request(BASE, timeout=2)
            return
        except Exception:
            time.sleep(2)
    raise RuntimeError(f"Odoo did not respond: {BASE}")


class Browser:
    def __init__(self):
        self.profile = tempfile.TemporaryDirectory(prefix="facodi-visual-")
        self.proc = subprocess.Popen([
            "google-chrome", "--headless=new", "--no-sandbox",
            "--disable-gpu", "--disable-dev-shm-usage", "--no-first-run",
            "--no-default-browser-check", "--remote-allow-origins=*",
            "--remote-debugging-port=9222",
            f"--user-data-dir={self.profile.name}", "about:blank",
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(70):
            try:
                target = json.loads(request("http://127.0.0.1:9222/json/new?about:blank", method="PUT"))
                self.ws = websocket.create_connection(target["webSocketDebuggerUrl"], timeout=15, suppress_origin=True)
                self.id = 0
                self.call("Page.enable")
                self.call("Runtime.enable")
                return
            except Exception:
                time.sleep(.2)
        raise RuntimeError("Chrome DevTools did not start")

    def call(self, method, params=None):
        self.id += 1
        ident = self.id
        self.ws.send(json.dumps({"id": ident, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self.ws.recv())
            if message.get("id") == ident:
                if "error" in message:
                    raise RuntimeError(f"CDP {method}: {message['error']}")
                return message.get("result", {})

    def close(self):
        if hasattr(self, "ws"):
            self.ws.close()
        self.proc.terminate()
        try:
            self.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.proc.kill()
        self.profile.cleanup()


AUDIT_JS = r"""(() => {
 const viewport = window.innerWidth; // include scrollbar gutter; clientWidth may be 15px smaller
 const pageWidth = document.documentElement.scrollWidth;
 const selectors = ['#wrap', '#footer', '.facodi-footer', '.facodi-header', '.facodi-partner-grid', '.o_wslides', '.container-fluid'];
 const boxes = selectors.flatMap(selector => Array.from(document.querySelectorAll(selector)).slice(0, 4).map(el => {
    const r = el.getBoundingClientRect();
    return {selector, right: Math.round(r.right), left: Math.round(r.left), width: Math.round(r.width)};
 }));
 const offenders = Array.from(document.querySelectorAll('body *')).filter(el => {
    const style = window.getComputedStyle(el);
    if (style.display === 'none' || style.visibility === 'hidden' || style.position === 'fixed') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && (r.right > viewport + 3 || r.left < -3) &&
           style.position !== 'absolute';
 }).slice(0, 12).map(el => ({
    tag: el.tagName.toLowerCase(), className: typeof el.className === 'string' ? el.className.slice(0, 110) : '',
    right: Math.round(el.getBoundingClientRect().right),
    left: Math.round(el.getBoundingClientRect().left),
 }));
 return {viewport, pageWidth, overflow:pageWidth > viewport + 2, boxes, offenders,
         title:document.title, pathname:location.pathname, hasFooter:!!document.querySelector('#footer.facodi-footer'), themeActive:!!document.querySelector('.facodi-site'), genericLogo:document.body.innerText.includes('Your Logo')};
})()"""


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    wait_for_odoo()
    browser = Browser()
    report = []
    try:
        for path, slug in PAGES:
            for width in WIDTHS:
                browser.call("Emulation.setDeviceMetricsOverride", {
                    "width": width, "height": HEIGHT, "deviceScaleFactor": 1,
                    "mobile": width <= 768,
                })
                browser.call("Page.navigate", {"url": BASE + path})
                time.sleep(2)
                state = browser.call("Runtime.evaluate", {
                    "expression": AUDIT_JS, "returnByValue": True,
                })["result"]["value"]
                png = browser.call("Page.captureScreenshot", {
                    "format": "png", "captureBeyondViewport": True,
                })["data"]
                filename = f"{slug}-{width}.png"
                (OUTPUT / filename).write_bytes(base64.b64decode(png))
                report.append({"route": path, "width": width, "screenshot": filename, **state})
                print(f"{path} {width}px: scrollWidth={state['pageWidth']} viewport={state['viewport']} overflow={state['overflow']}", flush=True)
    finally:
        browser.close()
        (OUTPUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    failures = [r for r in report if r["overflow"] or not r["hasFooter"] or not r["themeActive"] or r["genericLogo"] or "Page Not Found" in r["title"]]
    if failures:
        for r in failures:
            print(f"FAIL: {r['route']} @ {r['width']}px: overflow={r['overflow']} footer={r['hasFooter']} theme={r['themeActive']} title={r['title']} offenders={r['offenders']}")
        raise SystemExit(1)
    print(f"PASS: {len(report)} Chromium screenshots and layout audits")


if __name__ == "__main__":
    main()
