from bs4 import BeautifulSoup

from ezdl2.metadata import extract_metadata


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


def test_extracts_title():
    soup = _soup("<html><head><title>My Page</title></head><body></body></html>")
    m = extract_metadata(soup, "https://example.com/page")
    assert m.title == "My Page"


def test_extracts_description():
    soup = _soup('<html><head><meta name="description" content="A great page"></head></html>')
    m = extract_metadata(soup, "https://example.com/")
    assert m.description == "A great page"


def test_extracts_author():
    soup = _soup('<html><head><meta name="author" content="Jane Doe"></head></html>')
    m = extract_metadata(soup, "https://example.com/")
    assert m.author == "Jane Doe"


def test_extracts_site_name():
    soup = _soup('<html><head><meta property="og:site_name" content="Example Site"></head></html>')
    m = extract_metadata(soup, "https://example.com/")
    assert m.site_name == "Example Site"


def test_extracts_domain():
    soup = _soup("<html></html>")
    m = extract_metadata(soup, "https://sub.example.com/path")
    assert m.domain == "sub.example.com"


def test_url_preserved():
    soup = _soup("<html></html>")
    m = extract_metadata(soup, "https://example.com/article/1")
    assert m.url == "https://example.com/article/1"


def test_missing_fields_are_none():
    soup = _soup("<html><body></body></html>")
    m = extract_metadata(soup, "https://example.com/")
    assert m.title is None
    assert m.author is None
    assert m.description is None
    assert m.site_name is None
