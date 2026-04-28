# ezdl2

A Python library for robust web page fetching with automatic fallback from plain HTTP to headless browser rendering.

## Purpose

Fetch web pages reliably by:
1. Attempting a fast `requests`-based fetch with realistic browser headers
2. Detecting failures via heuristics (bot blocks, CAPTCHAs, JS-only pages, etc.)
3. Falling back to Playwright (headless Chromium) with `playwright-stealth` if the first attempt fails

## Project Structure

```
ezdl2/
├── ezdl2/
│   ├── __init__.py         # Public API: fetch()
│   ├── fetcher.py          # Orchestrates the two-stage fetch
│   ├── http_fetch.py       # Stage 1: requests-based fetch
│   ├── browser_fetch.py    # Stage 2: Playwright + stealth fetch
│   ├── heuristics.py       # Bot-block / failure detection logic
│   └── headers.py          # Realistic browser header pools
├── tests/
│   ├── test_heuristics.py
│   ├── test_http_fetch.py
│   └── test_browser_fetch.py
├── pyproject.toml
├── plan.md
└── CLAUDE.md
```

## Dependencies

- `requests` — HTTP fetching
- `playwright` — headless browser automation
- `playwright-stealth` — anti-detection patches for Playwright

## Public API

```python
from ezdl2 import fetch

result = fetch("https://example.com")
# result.html      — final HTML string
# result.url       — final URL (after redirects)
# result.method    — "http" or "browser"
# result.ok        — True if content looks valid
```

## Key Design Decisions

- `fetch()` is synchronous from the caller's perspective; Playwright is driven via `asyncio.run()` internally.
- Heuristics are a scored list of signals, not a single check. Tune thresholds in `heuristics.py`.
- Header pools rotate User-Agent and Accept-Language to avoid fingerprinting patterns.
- No retry loops — each stage gets one attempt; the caller decides on retries.

## Development Commands

```bash
pip install -e ".[dev]"
playwright install chromium
pytest
```
