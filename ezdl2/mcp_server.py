from typing import Literal

from fastmcp import FastMCP

from ezdl2 import fetch
from ezdl2.http_fetch import raw_download

mcp = FastMCP(name="ezdl2")


@mcp.tool()
def web_fetch(url: str, force_browser: bool = False) -> str:
    """Fetch a web page and return its content as clean markdown.
    Tries a fast HTTP request first, falls back to headless Chromium if blocked.
    Set force_browser=True to skip HTTP and use the browser directly."""
    result = fetch(url, force_browser=force_browser)
    lines = [
        f"URL: {result.url}",
        f"Title: {result.metadata.title}",
        f"Method: {result.method}",
        "",
        result.markdown,
    ]
    return "\n".join(lines)

@mcp.tool()
def web_fetch_light_html(url: str, force_browser: bool = False) -> str:
    """Fetch a minimized HTML content from the web page and returns the html text.
    Set force_browser=True to skip HTTP and use the browser directly."""
    result = fetch(url, force_browser=force_browser)
    lines = [
        f"URL: {result.url}",
        f"Title: {result.metadata.title}",
        f"Method: {result.method}",
        "",
        result.content,
    ]
    return "\n".join(lines)

@mcp.tool()
def web_fetch_raw_html(url: str, force_browser: bool = False) -> str:
    """Fetch the raw HTML content from the web page in url and returns it.
    Set force_browser=True to skip HTTP and use the browser directly."""
    result = fetch(url, force_browser=force_browser)
    lines = [
        f"URL: {result.url}",
        f"Title: {result.metadata.title}",
        f"Method: {result.method}",
        "",
        result.html,
    ]
    return "\n".join(lines)


@mcp.tool()
def web_fetch_to_file(
    url: str,
    output_path: str,
    mode: Literal["markdown", "html", "content", "raw"] = "markdown",
    force_browser: bool = False,
) -> str:
    """Fetch a web page and save it to a file.

    output_path MUST be an absolute path (e.g. /home/user/page.md or C:/Users/me/page.html).
    mode controls what is saved:
      - markdown: clean markdown (default)
      - content:  extracted main-content HTML
      - html:     full raw HTML
      - raw:      unmodified HTTP response bytes (ignores force_browser)
    """
    if mode not in ["markdown", "html", "content"]:
        return f"Invalid mode: {mode}. Must be one of 'markdown', 'html', 'content', or 'raw'."

    if mode == "raw":
        resp = raw_download(url)
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=65536):
                f.write(chunk)
        return f"Saved raw bytes to {output_path}"

    result = fetch(url, force_browser=force_browser)
    if not result.ok:
        return f"Failed to fetch {url}. Signals: {result.failure_signals}"
    
    if mode == "markdown":
        content = result.markdown
    elif mode == "html":
        content = result.html
    elif mode == "content":        
        content = result.content
    else:
        return f"Invalid mode: {mode}. Must be one of 'markdown', 'html', 'content', or 'raw'."
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return f"Saved {mode} ({len(content)} chars) from {result.url} to {output_path}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
