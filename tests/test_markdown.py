from bs4 import BeautifulSoup

from ezdl2.content import extract_main_content, to_markdown


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


# --- relative URL resolution ---

def test_resolves_relative_href():
    soup = _soup('<html><body><main><a href="/about">About</a></main></body></html>')
    content = extract_main_content(soup, base_url="https://example.com/")
    assert 'href="https://example.com/about"' in content


def test_resolves_relative_img_src():
    soup = _soup('<html><body><main><img src="/logo.png"></main></body></html>')
    content = extract_main_content(soup, base_url="https://example.com/")
    assert 'src="https://example.com/logo.png"' in content


def test_leaves_absolute_urls_unchanged():
    soup = _soup('<html><body><main><a href="https://other.com/page">link</a></main></body></html>')
    content = extract_main_content(soup, base_url="https://example.com/")
    assert 'href="https://other.com/page"' in content


def test_no_base_url_leaves_links_unchanged():
    soup = _soup('<html><body><main><a href="/about">About</a></main></body></html>')
    content = extract_main_content(soup)
    assert 'href="/about"' in content


def test_resolves_relative_path_without_leading_slash():
    soup = _soup('<html><body><main><a href="page.html">page</a></main></body></html>')
    content = extract_main_content(soup, base_url="https://example.com/section/")
    assert 'href="https://example.com/section/page.html"' in content


# --- markdown conversion ---

def test_to_markdown_converts_heading():
    html = "<h1>Hello</h1>"
    md = to_markdown(html)
    assert "# Hello" in md


def test_to_markdown_converts_links():
    html = '<a href="https://example.com">Click</a>'
    md = to_markdown(html)
    assert "[Click](https://example.com)" in md


def test_to_markdown_strips_extra_blank_lines():
    html = "<p>First</p><p>Second</p>"
    md = to_markdown(html)
    assert "\n\n\n" not in md


def test_to_markdown_ends_with_newline():
    md = to_markdown("<p>text</p>")
    assert md.endswith("\n")


def test_fetch_result_markdown_property():
    from unittest.mock import patch
    from ezdl2.fetcher import fetch
    from ezdl2.http_fetch import RawResponse

    html = "<html><body><main><h1>Title</h1><p>" + "w" * 600 + "</p></main></body></html>"
    with patch("ezdl2.fetcher.http_fetch", return_value=RawResponse(200, {}, html, "https://example.com")):
        result = fetch("https://example.com")
        assert "# Title" in result.markdown


def test_fetch_result_metadata_property():
    from unittest.mock import patch
    from ezdl2.fetcher import fetch
    from ezdl2.http_fetch import RawResponse

    html = (
        "<html><head><title>Test Page</title>"
        '<meta name="description" content="desc"></head>'
        "<body><main><p>" + "w" * 600 + "</p></main></body></html>"
    )
    with patch("ezdl2.fetcher.http_fetch", return_value=RawResponse(200, {}, html, "https://example.com")):
        result = fetch("https://example.com")
        assert result.metadata.title == "Test Page"
        assert result.metadata.description == "desc"
        assert result.metadata.domain == "example.com"
