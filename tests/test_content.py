from bs4 import BeautifulSoup

from ezdl2.content import extract_main_content


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def test_prefers_main_tag():
    soup = _soup("<html><body><nav>nav</nav><main><p>Main content</p></main></body></html>")
    result = extract_main_content(soup)
    assert "Main content" in result
    assert "nav" not in result


def test_prefers_article_when_no_main():
    soup = _soup("<html><body><article><p>Article text</p></article></body></html>")
    result = extract_main_content(soup)
    assert "Article text" in result


def test_finds_content_by_id():
    soup = _soup('<html><body><div id="main-content"><p>Found it</p></div></body></html>')
    result = extract_main_content(soup)
    assert "Found it" in result


def test_finds_content_by_class():
    soup = _soup('<html><body><div class="content-area"><p>Class match</p></div></body></html>')
    result = extract_main_content(soup)
    assert "Class match" in result


def test_falls_back_to_body():
    soup = _soup("<html><body><p>Only body</p></body></html>")
    result = extract_main_content(soup)
    assert "Only body" in result


def test_strips_scripts_and_styles():
    soup = _soup(
        "<html><body><script>alert(1)</script><style>body{}</style><main><p>Clean</p></main></body></html>"
    )
    result = extract_main_content(soup)
    assert "alert" not in result
    assert "body{}" not in result
    assert "Clean" in result


def test_strips_nav_header_footer():
    soup = _soup(
        "<html><body><header>HDR</header><nav>NAV</nav><main><p>Content</p></main><footer>FTR</footer></body></html>"
    )
    result = extract_main_content(soup)
    assert "HDR" not in result
    assert "NAV" not in result
    assert "FTR" not in result
    assert "Content" in result


def test_does_not_mutate_original_soup():
    html = "<html><body><script>alert(1)</script><main><p>Hi</p></main></body></html>"
    soup = _soup(html)
    extract_main_content(soup)
    assert soup.find("script") is not None


def test_fetch_result_content_property():
    from unittest.mock import patch
    from ezdl2.fetcher import fetch
    from ezdl2.http_fetch import RawResponse

    html = "<html><body><main><p>" + "x" * 600 + "</p></main></body></html>"
    with patch("ezdl2.fetcher.http_fetch", return_value=RawResponse(200, {}, html, "https://example.com")):
        result = fetch("https://example.com")
        assert "<main>" in result.content or "<p>" in result.content
