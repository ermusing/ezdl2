import pytest
from ezdl2.http_fetch import RawResponse
from ezdl2.heuristics import THRESHOLD, is_failure


def _resp(html="<html><body>" + "Hello world, this is a clean response with plenty of content. " * 10 + "</body></html>", status=200, url="https://example.com", error=None):
    return RawResponse(status_code=status, headers={}, html=html, final_url=url, error=error)


def test_clean_response_passes():
    failed, signals = is_failure(_resp())
    assert not failed
    assert signals == []


def test_network_error_is_failure():
    failed, signals = is_failure(_resp(error="timeout"))
    assert failed
    assert any("network_error" in s for s in signals)


def test_http_4xx_scores_10():
    failed, signals = is_failure(_resp(status=403))
    assert failed
    assert "http_403" in signals


def test_http_5xx_scores_10():
    failed, signals = is_failure(_resp(status=503))
    assert failed
    assert "http_503" in signals


def test_empty_body_is_failure():
    failed, signals = is_failure(_resp(html="   "))
    assert failed
    assert "empty_body" in signals


def test_short_body_contributes_score():
    short_html = "<html><body>Hi</body></html>"
    _, signals = is_failure(_resp(html=short_html))
    assert "body_too_short" in signals


def test_captcha_cf_challenge():
    html = "<html><body><div class='cf-challenge'>please wait</div></body></html>"
    failed, signals = is_failure(_resp(html=html))
    assert failed
    assert any("captcha_marker" in s for s in signals)


def test_captcha_grecaptcha():
    html = "<html><body><div class='g-recaptcha'></div></body></html>"
    failed, signals = is_failure(_resp(html=html))
    assert failed


def test_captcha_hcaptcha():
    html = "<html><body><div class='hcaptcha'></div></body></html>"
    failed, signals = is_failure(_resp(html=html))
    assert failed


def test_suspicious_title_access_denied():
    html = "<html><head><title>Access Denied</title></head><body>x</body></html>"
    failed, signals = is_failure(_resp(html=html))
    assert failed
    assert "suspicious_title" in signals


def test_suspicious_title_just_a_moment():
    html = "<html><head><title>Just a moment...</title></head><body>x</body></html>"
    failed, signals = is_failure(_resp(html=html))
    assert failed
    assert "suspicious_title" in signals


def test_redirect_to_login_url():
    html = "<html><body>" + "a" * 600 + "</body></html>"
    failed, signals = is_failure(_resp(html=html, url="https://example.com/login"))
    assert "redirect_to_challenge_url" in signals


def test_redirect_to_captcha_url():
    html = "<html><body>" + "a" * 600 + "</body></html>"
    _, signals = is_failure(_resp(html=html, url="https://example.com/captcha"))
    assert "redirect_to_challenge_url" in signals


def test_threshold_constant_is_8():
    assert THRESHOLD == 8
