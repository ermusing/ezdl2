import json
from unittest.mock import patch

import pytest

from ezdl2.cli import _build_parser, main
from ezdl2.fetcher import FetchResult
from ezdl2.metadata import PageMetadata


def _make_result(
    html="<html><head><title>Test</title></head><body><main><h1>Hello</h1><p>content</p></main></body></html>",
    url="https://example.com/",
    method="http",
    ok=True,
    signals=None,
):
    return FetchResult(html=html, url=url, method=method, ok=ok, failure_signals=signals or [])


@pytest.fixture()
def good_result():
    return _make_result()


def _run(argv: list[str], capsys, result=None):
    if result is None:
        result = _make_result()
    with patch("ezdl2.cli.fetch", return_value=result):
        parser = _build_parser()
        args = parser.parse_args(argv)
        args.func(args)
    return capsys.readouterr()


# --- html ---

def test_html_prints_raw_html(capsys):
    out, _ = _run(["html", "https://example.com"], capsys)
    assert "<html>" in out


# --- content ---

def test_content_prints_extracted_html(capsys):
    out, _ = _run(["content", "https://example.com"], capsys)
    assert "Hello" in out
    assert "<nav>" not in out


# --- markdown ---

def test_markdown_prints_markdown(capsys):
    out, _ = _run(["markdown", "https://example.com"], capsys)
    assert "# Hello" in out


# --- metadata ---

def test_metadata_prints_json(capsys):
    out, _ = _run(["metadata", "https://example.com"], capsys)
    data = json.loads(out)
    assert data["title"] == "Test"
    assert data["domain"] == "example.com"
    assert data["url"] == "https://example.com/"


def test_metadata_missing_fields_are_null(capsys):
    out, _ = _run(["metadata", "https://example.com"], capsys)
    data = json.loads(out)
    assert "author" in data
    assert "description" in data


# --- fetch ---

def test_fetch_returns_json_envelope(capsys):
    out, _ = _run(["fetch", "https://example.com"], capsys)
    data = json.loads(out)
    assert data["url"] == "https://example.com/"
    assert data["method"] == "http"
    assert data["ok"] is True
    assert "metadata" in data
    assert "markdown" in data


def test_fetch_no_html_by_default(capsys):
    out, _ = _run(["fetch", "https://example.com"], capsys)
    data = json.loads(out)
    assert "html" not in data


def test_fetch_include_html_flag(capsys):
    out, _ = _run(["fetch", "https://example.com", "--include-html"], capsys)
    data = json.loads(out)
    assert "html" in data
    assert "<html>" in data["html"]


def test_fetch_include_content_flag(capsys):
    out, _ = _run(["fetch", "https://example.com", "--include-content"], capsys)
    data = json.loads(out)
    assert "content" in data


def test_fetch_failure_signals_in_json(capsys):
    result = _make_result(ok=False, signals=["http_403"])
    out, err = _run(["fetch", "https://example.com"], capsys, result=result)
    data = json.loads(out)
    assert data["ok"] is False
    assert "http_403" in data["failure_signals"]
    assert "warning" in err


# --- warning on failed fetch ---

def test_warning_printed_to_stderr_on_failure(capsys):
    result = _make_result(ok=False, signals=["empty_body"])
    _run(["markdown", "https://example.com"], capsys, result=result)
    _, err = capsys.readouterr()
    # warning already captured in _run; re-check via direct call
    with patch("ezdl2.cli.fetch", return_value=result):
        args = _build_parser().parse_args(["markdown", "https://example.com"])
        args.func(args)
    _, err = capsys.readouterr()
    assert "warning" in err
    assert "empty_body" in err
