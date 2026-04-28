from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property

from bs4 import BeautifulSoup

from .browser_fetch import browser_fetch
from .content import extract_main_content, to_markdown
from .heuristics import is_failure
from .http_fetch import http_fetch
from .metadata import PageMetadata, extract_metadata


@dataclass
class FetchResult:
    html: str
    url: str
    method: str  # "http" | "browser"
    ok: bool
    failure_signals: list[str] = field(default_factory=list)

    @cached_property
    def soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.html, "lxml")

    @cached_property
    def metadata(self) -> PageMetadata:
        return extract_metadata(self.soup, self.url)

    @cached_property
    def content(self) -> str:
        return extract_main_content(self.soup, base_url=self.url)

    @cached_property
    def markdown(self) -> str:
        return to_markdown(self.content)


def fetch(url: str) -> FetchResult:
    response = http_fetch(url)
    failed, signals = is_failure(response)

    if not failed:
        return FetchResult(
            html=response.html,
            url=response.final_url,
            method="http",
            ok=True,
            failure_signals=[],
        )

    browser_response = browser_fetch(url)
    browser_failed, browser_signals = is_failure(browser_response)

    return FetchResult(
        html=browser_response.html,
        url=browser_response.final_url,
        method="browser",
        ok=not browser_failed,
        failure_signals=browser_signals,
    )


def fetch_soup(url: str) -> BeautifulSoup:
    return fetch(url).soup


def fetch_content(url: str) -> str:
    return fetch(url).content


def fetch_markdown(url: str) -> str:
    return fetch(url).markdown
