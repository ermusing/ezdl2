from fastmcp import FastMCP

from ezdl2 import fetch

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


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
