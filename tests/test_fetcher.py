from unittest.mock import patch

import pytest

from ezdl2.fetcher import fetch
from ezdl2.http_fetch import RawResponse


def _good_response(url="https://example.com"):
    html = "<html><head><title>Good Page</title></head><body>" + "a" * 600 + "</body></html>"
    return RawResponse(status_code=200, headers={}, html=html, final_url=url)


def _bad_response(url="https://example.com"):
    return RawResponse(status_code=403, headers={}, html="Forbidden", final_url=url)


def _browser_good_response(url="https://example.com"):
    html = "<html><head><title>Rendered</title></head><body>" + "b" * 600 + "</body></html>"
    return RawResponse(status_code=200, headers={}, html=html, final_url=url)


@patch("ezdl2.fetcher.http_fetch")
def test_http_success_no_browser(mock_http):
    mock_http.return_value = _good_response()
    result = fetch("https://example.com")
    assert result.method == "http"
    assert result.ok is True
    assert result.failure_signals == []


@patch("ezdl2.fetcher.browser_fetch")
@patch("ezdl2.fetcher.http_fetch")
def test_http_failure_triggers_browser(mock_http, mock_browser):
    mock_http.return_value = _bad_response()
    mock_browser.return_value = _browser_good_response()
    result = fetch("https://example.com")
    assert result.method == "browser"
    assert result.ok is True
    mock_browser.assert_called_once_with("https://example.com")


@patch("ezdl2.fetcher.browser_fetch")
@patch("ezdl2.fetcher.http_fetch")
def test_both_fail_ok_is_false(mock_http, mock_browser):
    mock_http.return_value = _bad_response()
    mock_browser.return_value = RawResponse(
        status_code=503, headers={}, html="error", final_url="https://example.com"
    )
    result = fetch("https://example.com")
    assert result.method == "browser"
    assert result.ok is False


@patch("ezdl2.fetcher.http_fetch")
def test_result_html_and_url_populated(mock_http):
    mock_http.return_value = _good_response(url="https://example.com/final")
    result = fetch("https://example.com")
    assert result.url == "https://example.com/final"
    assert len(result.html) > 0
