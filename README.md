# ezdl2

Robust web page fetching with automatic HTTP-to-browser fallback, main-content extraction, and markdown conversion.

## How it works

1. Tries a fast `requests`-based fetch with realistic browser headers
2. Scores the response with heuristics (bot blocks, CAPTCHAs, JS-only pages, etc.)
3. Falls back to headless Chromium via Playwright + playwright-stealth if the first attempt fails
4. Extracts the main content area and converts it to clean markdown

## Installation

```bash
pip install ezdl2
playwright install chromium
```

## Python API

```python
from ezdl2 import fetch, fetch_soup, fetch_content, fetch_markdown

# Full result
result = fetch("https://example.com")
print(result.method)    # "http" or "browser"
print(result.ok)        # True if content looks valid
print(result.markdown)  # clean markdown of the main content
print(result.metadata)  # PageMetadata(title, author, description, site_name, domain, url)

# Convenience shortcuts
soup     = fetch_soup("https://example.com")     # BeautifulSoup
content  = fetch_content("https://example.com")  # extracted main-content HTML
markdown = fetch_markdown("https://example.com") # clean markdown string
```

### `FetchResult` attributes

| Attribute | Type | Description |
|---|---|---|
| `html` | `str` | Raw HTML |
| `url` | `str` | Final URL after redirects |
| `method` | `str` | `"http"` or `"browser"` |
| `ok` | `bool` | `True` if content looks valid |
| `failure_signals` | `list[str]` | Heuristic signals that triggered |
| `soup` | `BeautifulSoup` | Parsed HTML (cached) |
| `metadata` | `PageMetadata` | Title, author, description, etc. (cached) |
| `content` | `str` | Extracted main-content HTML (cached) |
| `markdown` | `str` | Clean markdown (cached) |

### `PageMetadata` fields

`title`, `author`, `description`, `site_name` (og:site_name), `domain`, `url`

## CLI

```bash
# Print raw HTML
ezdl2 html https://example.com

# Print extracted main-content HTML
ezdl2 content https://example.com

# Print page as clean markdown
ezdl2 markdown https://example.com

# Print metadata as JSON
ezdl2 metadata https://example.com

# JSON envelope with metadata + markdown
ezdl2 fetch https://example.com
ezdl2 fetch https://example.com --include-html
ezdl2 fetch https://example.com --include-content
```

## MCP Server

ezdl2 ships an [MCP](https://modelcontextprotocol.io/) server so AI assistants (Claude, Cursor, etc.) can fetch web pages as a tool call.

### Tools exposed

| Tool | Description |
|---|---|
| `web_fetch` | Fetch a page and return clean markdown (+ URL, title, method) |
| `web_fetch_light_html` | Fetch a page and return extracted main-content HTML |
| `web_fetch_raw_html` | Fetch a page and return the raw HTML |

All three tools accept:
- `url` — the page to fetch
- `force_browser` *(optional, default `false`)* — skip the HTTP stage and go straight to headless Chromium

### Starting the server

```bash
ezdl2-mcp
```

The server speaks the MCP stdio protocol and is installed as the `ezdl2-mcp` script when you `pip install ezdl2`.

### Connecting to Claude Code / Claude Desktop

Add the server to your `.mcp.json` (project-level) or `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ezdl2": {
      "type": "stdio",
      "command": "ezdl2-mcp"
    }
  }
}
```

If you are using a virtual environment, point `command` at the venv script instead:

```json
{
  "mcpServers": {
    "ezdl2": {
      "type": "stdio",
      "command": ".venv/Scripts/ezdl2-mcp"
    }
  }
}
```

## Development

```bash
pip install -e ".[dev]"
playwright install chromium
pytest
```

## Dependencies

- [requests](https://requests.readthedocs.io/) — fast HTTP fetching
- [playwright](https://playwright.dev/python/) — headless browser automation
- [playwright-stealth](https://github.com/AtuboDad/playwright_stealth) — anti-detection patches
- [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) + [lxml](https://lxml.de/) — HTML parsing
- [markdownify](https://github.com/matthewwithanm/python-markdownify) — HTML-to-markdown
