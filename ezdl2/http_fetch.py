from __future__ import annotations

from dataclasses import dataclass

import requests
import requests.exceptions

from .headers import get_headers


@dataclass
class RawResponse:
    status_code: int | None
    headers: dict
    html: str
    final_url: str
    error: str | None = None


def http_fetch(url: str) -> RawResponse:
    session = requests.Session()
    session.headers.update(get_headers())
    try:
        resp = session.get(url, timeout=15, allow_redirects=True)
        return RawResponse(
            status_code=resp.status_code,
            headers=dict(resp.headers),
            html=resp.text,
            final_url=resp.url,
        )
    except requests.exceptions.SSLError as exc:
        return RawResponse(status_code=None, headers={}, html="", final_url=url, error=f"ssl_error: {exc}")
    except requests.exceptions.ConnectionError as exc:
        return RawResponse(status_code=None, headers={}, html="", final_url=url, error=f"connection_error: {exc}")
    except requests.exceptions.Timeout:
        return RawResponse(status_code=None, headers={}, html="", final_url=url, error="timeout")
    except requests.exceptions.RequestException as exc:
        return RawResponse(status_code=None, headers={}, html="", final_url=url, error=f"request_error: {exc}")
