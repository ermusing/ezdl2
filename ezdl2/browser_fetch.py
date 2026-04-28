from __future__ import annotations

import asyncio

from .http_fetch import RawResponse


async def _do_browser_fetch(url: str) -> RawResponse:
    from playwright.async_api import async_playwright
    from playwright_stealth import Stealth

    stealth = Stealth()
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            timezone_id="America/New_York",
        )
        page = await context.new_page()
        await stealth.apply_stealth_async(page)
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            html = await page.content()
            final_url = page.url
            status = response.status if response else None
            headers = dict(await response.all_headers()) if response else {}
        finally:
            await browser.close()

    return RawResponse(
        status_code=status,
        headers=headers,
        html=html,
        final_url=final_url,
    )


def browser_fetch(url: str) -> RawResponse:
    try:
        return asyncio.run(_do_browser_fetch(url))
    except Exception as exc:
        return RawResponse(status_code=None, headers={}, html="", final_url=url, error=f"browser_error: {exc}")
