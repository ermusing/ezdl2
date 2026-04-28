from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from bs4 import BeautifulSoup


@dataclass
class PageMetadata:
    title: str | None
    author: str | None
    description: str | None
    site_name: str | None
    domain: str
    url: str


def extract_metadata(soup: BeautifulSoup, url: str) -> PageMetadata:
    domain = urlparse(url).netloc

    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    def _meta(name: str | None = None, prop: str | None = None) -> str | None:
        if name:
            tag = soup.find("meta", attrs={"name": name})
        else:
            tag = soup.find("meta", attrs={"property": prop})
        return tag.get("content") if tag else None

    return PageMetadata(
        title=title,
        author=_meta(name="author"),
        description=_meta(name="description"),
        site_name=_meta(prop="og:site_name"),
        domain=domain,
        url=url,
    )
