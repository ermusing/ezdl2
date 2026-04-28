"""Integration test for browser_fetch using a real local HTTP server."""
import pytest

pytest.importorskip("pytest_httpserver")

from pytest_httpserver import HTTPServer

from ezdl2.browser_fetch import browser_fetch


@pytest.fixture(scope="session")
def httpserver_listen_address():
    return ("127.0.0.1", 0)


def test_browser_fetch_simple_page(httpserver: HTTPServer):
    httpserver.expect_request("/").respond_with_data(
        "<html><body><h1>Hello from test server</h1></body></html>",
        content_type="text/html",
    )
    url = httpserver.url_for("/")
    result = browser_fetch(url)
    assert result.error is None
    assert "Hello from test server" in result.html
    assert result.status_code == 200


def test_browser_fetch_captures_final_url(httpserver: HTTPServer):
    httpserver.expect_request("/page").respond_with_data(
        "<html><body>Content</body></html>",
        content_type="text/html",
    )
    url = httpserver.url_for("/page")
    result = browser_fetch(url)
    assert result.final_url.endswith("/page")


def test_browser_fetch_bad_host_returns_error():
    result = browser_fetch("http://this-host-does-not-exist-ezdl2-test.local/")
    assert result.error is not None
    assert result.html == ""
