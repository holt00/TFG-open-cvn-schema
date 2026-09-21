"""Take a full-page screenshot of the TFM dashboard with a headless Chromium (issue #100, Task 9).

Evidence for the memoria that the dashboard renders in a real browser. Playwright is not a
dependency of the repository; run it from a throwaway environment:

    uvx --from playwright playwright install chromium
    SUPERSET_URL=http://localhost:8088 SUPERSET_ADMIN_PASSWORD=... \\
        uvx --from playwright python infra/superset/screenshot_dashboard.py out.png

Environment:
    SUPERSET_URL: Superset root URL (default ``http://localhost:8088``, a ``kubectl port-forward``).
    SUPERSET_ADMIN_USER: admin user (default ``admin``).
    SUPERSET_ADMIN_PASSWORD: its password (key ``admin-password`` of the Secret ``superset-secrets``).
"""

from __future__ import annotations

import logging
import os
import sys

from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

DASHBOARD_SLUG = "tfm-gold-indicators"
CHART_SELECTOR = ".dashboard-component-chart-holder canvas, .dashboard-component-chart-holder table"


def main(output: str) -> int:
    """Log in, open the dashboard, wait for its charts and save a screenshot.

    Args:
        output: Path of the PNG to write.

    Returns:
        Process exit code: 1 when a chart shows an error, otherwise 0.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    base_url = os.environ.get("SUPERSET_URL", "http://localhost:8088").rstrip("/")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1500, "height": 1100})
        page.goto(f"{base_url}/login/", wait_until="networkidle")
        page.fill("#username", os.environ.get("SUPERSET_ADMIN_USER", "admin"))
        page.fill("#password", os.environ["SUPERSET_ADMIN_PASSWORD"])
        page.click("button[type=submit]")
        page.wait_for_load_state("networkidle")
        page.goto(f"{base_url}/superset/dashboard/{DASHBOARD_SLUG}/", wait_until="networkidle")
        page.wait_for_selector(CHART_SELECTOR, timeout=60000)
        page.wait_for_timeout(6000)
        page.screenshot(path=output, full_page=True)
        canvases = page.locator(".dashboard-component-chart-holder canvas").count()
        errors = page.locator(".error-message, .alert-danger").count()
        browser.close()
    logger.info(f"screenshot written to {output}: {canvases} rendered charts, {errors} chart errors")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "dashboard.png"))
