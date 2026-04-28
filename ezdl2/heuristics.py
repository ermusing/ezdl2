from __future__ import annotations

import re
from urllib.parse import urlparse

from .http_fetch import RawResponse

THRESHOLD = 8

_LOGIN_URL_PATTERNS = re.compile(
    r"/(login|signin|sign-in|challenge|captcha|verify|auth|checkpoint)",
    re.IGNORECASE,
)

_TITLE_FAILURE_RE = re.compile(
    r"access.?denied|bot.?detect|captcha|verify.?you|are.?you.?human|just.?a.?moment|security.?check",
    re.IGNORECASE,
)

_CAPTCHA_MARKERS = ("cf-challenge", "g-recaptcha", "hcaptcha", "turnstile")

_JS_FRAMEWORK_RE = re.compile(r'<script[^>]+src=["\'][^"\']*(?:react|vue|angular|next|nuxt)', re.IGNORECASE)

_NOSCRIPT_DOMINANT_RE = re.compile(r"<noscript[^>]*>([\s\S]{200,}?)</noscript>", re.IGNORECASE)


def _extract_title(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return m.group(1).strip() if m else ""


def is_failure(response: RawResponse) -> tuple[bool, list[str]]:
    signals: list[str] = []
    score = 0

    if response.error:
        return True, [f"network_error:{response.error}"]

    html = response.html or ""
    status = response.status_code

    if status is not None and status >= 400:
        signals.append(f"http_{status}")
        score += 10

    if not html.strip():
        signals.append("empty_body")
        score += 10
    elif len(html) < 500:
        signals.append("body_too_short")
        score += 5

    title = _extract_title(html)
    if title and _TITLE_FAILURE_RE.search(title):
        signals.append("suspicious_title")
        score += 8

    for marker in _CAPTCHA_MARKERS:
        if marker in html:
            signals.append(f"captcha_marker:{marker}")
            score += 9
            break

    if _JS_FRAMEWORK_RE.search(html) and _NOSCRIPT_DOMINANT_RE.search(html):
        signals.append("js_only_page")
        score += 7

    meta_robots = re.search(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
    if meta_robots and "noindex" in meta_robots.group(1).lower() and status not in (None, 200):
        signals.append("noindex_unusual_status")
        score += 3

    final_url = response.final_url or ""
    path = urlparse(final_url).path
    if _LOGIN_URL_PATTERNS.search(path):
        signals.append("redirect_to_challenge_url")
        score += 6

    return score >= THRESHOLD, signals
