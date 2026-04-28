from unittest.mock import MagicMock, patch

import pytest
import requests.exceptions

from ezdl2.http_fetch import http_fetch


def _make_response(status=200, text="<html>ok</html>", url="https://example.com"):
    r = MagicMock()
    r.status_code = status
    r.text = text
    r.url = url
    r.headers = {"content-type": "text/html"}
    return r


@patch("ezdl2.http_fetch.requests.Session")
def test_successful_fetch(MockSession):
    session = MockSession.return_value
    session.get.return_value = _make_response()
    result = http_fetch("https://example.com")
    assert result.status_code == 200
    assert result.html == "<html>ok</html>"
    assert result.final_url == "https://example.com"
    assert result.error is None


@patch("ezdl2.http_fetch.requests.Session")
def test_headers_are_set(MockSession):
    session = MockSession.return_value
    session.get.return_value = _make_response()
    http_fetch("https://example.com")
    session.headers.update.assert_called_once()
    headers_used = session.headers.update.call_args[0][0]
    assert "user-agent" in headers_used


@patch("ezdl2.http_fetch.requests.Session")
def test_captures_redirect_final_url(MockSession):
    session = MockSession.return_value
    session.get.return_value = _make_response(url="https://example.com/final")
    result = http_fetch("https://example.com/start")
    assert result.final_url == "https://example.com/final"


@patch("ezdl2.http_fetch.requests.Session")
def test_timeout_returns_error(MockSession):
    session = MockSession.return_value
    session.get.side_effect = requests.exceptions.Timeout()
    result = http_fetch("https://example.com")
    assert result.error == "timeout"
    assert result.status_code is None
    assert result.html == ""


@patch("ezdl2.http_fetch.requests.Session")
def test_connection_error_returns_error(MockSession):
    session = MockSession.return_value
    session.get.side_effect = requests.exceptions.ConnectionError("DNS failed")
    result = http_fetch("https://example.com")
    assert result.error is not None
    assert "connection_error" in result.error


@patch("ezdl2.http_fetch.requests.Session")
def test_ssl_error_returns_error(MockSession):
    session = MockSession.return_value
    session.get.side_effect = requests.exceptions.SSLError("cert error")
    result = http_fetch("https://example.com")
    assert result.error is not None
    assert "ssl_error" in result.error


@patch("ezdl2.http_fetch.requests.Session")
def test_4xx_status_is_returned(MockSession):
    session = MockSession.return_value
    session.get.return_value = _make_response(status=403, text="Forbidden")
    result = http_fetch("https://example.com")
    assert result.status_code == 403
    assert result.error is None
