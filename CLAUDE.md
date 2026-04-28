# ezdl2

A Python library for robust web page fetching with automatic fallback from plain HTTP to headless browser rendering, plus main-content extraction and markdown conversion.

## Purpose

Fetch web pages reliably by:
1. Attempting a fast `requests`-based fetch with realistic browser headers
2. Detecting failures via heuristics (bot blocks, CAPTCHAs, JS-only pages, etc.)
3. Falling back to Playwright (headless Chromium) with `playwright-stealth` if the first attempt fails
4. Extracting main content (strips nav/header/footer/scripts) and converting to clean markdown

## Project Structure

```
ezdl2/
├── ezdl2/
│   ├── __init__.py         # Public API: fetch, fetch_soup, fetch_content, fetch_markdown
│   ├── fetcher.py          # FetchResult dataclass + orchestrates the two-stage fetch
│   ├── http_fetch.py       # Stage 1: requests-based fetch
│   ├── browser_fetch.py    # Stage 2: Playwright + stealth fetch
│   ├── heuristics.py       # Bot-block / failure detection logic
│   ├── headers.py          # Realistic browser header pools
│   ├── content.py          # Main-content extraction and markdown conversion
│   ├── metadata.py         # PageMetadata extraction (title, author, description, og:*)
│   └── cli.py              # CLI entry point (ezdl2 command)
├── tests/
│   ├── test_heuristics.py
│   ├── test_http_fetch.py
│   ├── test_browser_fetch.py
│   └── test_cli.py
├── pyproject.toml
└── CLAUDE.md
```

## Dependencies

- `requests` — HTTP fetching
- `playwright` — headless browser automation
- `playwright-stealth` — anti-detection patches for Playwright
- `beautifulsoup4` + `lxml` — HTML parsing
- `markdownify` — HTML-to-markdown conversion

## Public API

```python
from ezdl2 import fetch, fetch_soup, fetch_content, fetch_markdown, FetchResult, PageMetadata

# Full result object
result = fetch("https://example.com")
result.html             # raw HTML string
result.url              # final URL after redirects
result.method           # "http" or "browser"
result.ok               # True if content looks valid
result.failure_signals  # list of heuristic signal names that triggered
result.soup             # BeautifulSoup object (cached_property)
result.metadata         # PageMetadata (cached_property)
result.content          # extracted main-content HTML (cached_property)
result.markdown         # clean markdown string (cached_property)

# Convenience shortcuts
fetch_soup(url)     -> BeautifulSoup
fetch_content(url)  -> str   # extracted main-content HTML
fetch_markdown(url) -> str   # clean markdown

# Metadata fields
result.metadata.title
result.metadata.author
result.metadata.description
result.metadata.site_name   # og:site_name
result.metadata.domain
result.metadata.url
```

## CLI

```bash
ezdl2 html <url>          # print raw HTML
ezdl2 content <url>       # print extracted main-content HTML
ezdl2 markdown <url>      # print page as clean markdown
ezdl2 metadata <url>      # print metadata as JSON
ezdl2 fetch <url>         # JSON envelope: metadata + markdown (+ optional html/content)
  --include-html          # add raw HTML to fetch JSON output
  --include-content       # add content HTML to fetch JSON output
```

## Key Design Decisions

- `fetch()` is synchronous from the caller's perspective; Playwright is driven via `asyncio.run()` internally.
- `FetchResult` properties (`soup`, `metadata`, `content`, `markdown`) are `cached_property` — computed once on first access.
- Heuristics are a scored list of signals, not a single check. Tune thresholds in `heuristics.py`.
- Header pools rotate User-Agent and Accept-Language to avoid fingerprinting patterns.
- No retry loops — each stage gets one attempt; the caller decides on retries.
- Content extraction removes `script`, `style`, `nav`, `header`, `footer` then finds `<main>`, content-id/class, `<article>`, or falls back to `<body>`.
- Relative URLs in extracted content are resolved to absolute using the page's final URL.

## Development Commands

```bash
pip install -e ".[dev]"
playwright install chromium
pytest
```
