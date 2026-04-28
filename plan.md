# Implementation Plan

## Phase 1 — Project Scaffold

- [ ] Create `pyproject.toml` with metadata, dependencies (`requests`, `playwright`, `playwright-stealth`), and dev deps (`pytest`, `pytest-asyncio`)
- [ ] Create `ezdl2/__init__.py` exporting `fetch()` and `FetchResult`
- [ ] Stub all modules with placeholder implementations so imports work

## Phase 2 — Header Pool (`headers.py`)

- [ ] Build a pool of realistic Chrome User-Agent strings (Windows, macOS, Linux)
- [ ] Include matching `Accept`, `Accept-Language`, `Accept-Encoding`, `Sec-Fetch-*`, and `Cache-Control` headers per UA
- [ ] Expose `get_headers() -> dict` that returns a randomly sampled, consistent header set

## Phase 3 — HTTP Fetch (`http_fetch.py`)

- [ ] Implement `http_fetch(url) -> RawResponse` using `requests.Session`
  - Set headers from `headers.py`
  - Follow redirects, capture final URL
  - 15 s timeout
  - Return status code, response headers, HTML body, final URL
- [ ] Handle network-level errors (DNS failure, timeout, SSL error) — return them as structured errors, not exceptions

## Phase 4 — Failure Heuristics (`heuristics.py`)

Define a scored set of signals. If total score exceeds threshold, mark fetch as failed.

| Signal | Score |
|---|---|
| HTTP status 4xx/5xx | 10 |
| Response body < 500 bytes | 5 |
| Title contains "access denied", "bot", "captcha", "verify" (case-insensitive) | 8 |
| Body contains CAPTCHA widget markers (`cf-challenge`, `g-recaptcha`, `hcaptcha`) | 9 |
| Body is empty or only whitespace | 10 |
| JS framework present but `<noscript>` fallback dominates body | 7 |
| Meta `robots` tag set to `noindex` + unusual status | 3 |
| Redirect chain ended at a login/challenge page (URL heuristic) | 6 |

- [ ] Implement `is_failure(response) -> (bool, list[str])` returning the verdict and matched signals
- [ ] Expose `THRESHOLD = 8` as a tunable constant

## Phase 5 — Browser Fetch (`browser_fetch.py`)

- [ ] Implement `browser_fetch(url) -> RawResponse` using Playwright async API, called via `asyncio.run()`
  - Launch headless Chromium
  - Apply `playwright-stealth` patches
  - Set viewport to 1280×800, realistic locale and timezone
  - Navigate with `networkidle` wait condition (30 s timeout)
  - Capture final URL and `page.content()`
  - Close browser on exit (use `async with` context managers)
- [ ] Return same `RawResponse` shape as `http_fetch` for uniform downstream handling

## Phase 6 — Orchestrator (`fetcher.py`)

- [ ] Implement `fetch(url) -> FetchResult`
  1. Call `http_fetch(url)`
  2. Call `is_failure(response)` on result
  3. If failure, call `browser_fetch(url)`
  4. Return `FetchResult(html, url, method, ok, failure_signals)`
- [ ] `FetchResult` is a `dataclass` with fields: `html`, `url`, `method` (`"http"` | `"browser"`), `ok`, `failure_signals`

## Phase 7 — Tests

- [ ] `test_heuristics.py` — unit test each signal with fixture HTML snippets
- [ ] `test_http_fetch.py` — mock `requests.Session` to test header setting, redirect capture, error handling
- [ ] `test_browser_fetch.py` — integration test against a local HTTP server (use `pytest-httpserver` or similar)
- [ ] `test_fetcher.py` — end-to-end: verify fallback is triggered when http stage fails

## Open Questions

1. **Async public API?** Current plan is sync-only. Could expose `async_fetch()` later without breaking changes.
2. **Stealth library choice:** `playwright-stealth` (Python port) vs injecting the JS from `puppeteer-extra-plugin-stealth` directly — evaluate evasion quality.
3. **Caching:** Out of scope for v1; could add optional `cache_dir` param to `fetch()`.
4. **Proxy support:** Useful for resilience; add `proxy` kwarg in Phase 6 or as a follow-up.
