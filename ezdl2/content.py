from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from markdownify import markdownify


def _resolve_relative_urls(soup: BeautifulSoup, base_url: str) -> None:
    for tag in soup.find_all("a", href=True):
        tag["href"] = urljoin(base_url, tag["href"])
    for tag in soup.find_all("img", src=True):
        tag["src"] = urljoin(base_url, tag["src"])


def _clean_markdown(md: str) -> str:
    md = re.sub(r"\n\s*\n\s*\n", "\n\n", md)
    md = "\n".join(line.rstrip() for line in md.splitlines())
    return md.strip() + "\n"


def extract_main_content(soup: BeautifulSoup, base_url: str | None = None) -> str:
    soup = BeautifulSoup(str(soup), "lxml")

    if base_url:
        _resolve_relative_urls(soup, base_url)

    for element in soup.find_all(["script", "style", "nav", "header", "footer"]):
        element.decompose()

    content_candidates = [
        soup.find("main"),
        soup.find(id=re.compile(r"content|main", re.I)),
        soup.find(class_=re.compile(r"content|main", re.I)),
        soup.find("article"),
    ]

    main_content = next((c for c in content_candidates if c), None)

    if not main_content:
        main_content = soup.find("body")

    return str(main_content) if main_content else str(soup)


def to_markdown(html: str) -> str:
    md = markdownify(
        html,
        strip=["script", "style"],
        heading_style="ATX",
        bullets="-",
    )
    return _clean_markdown(md)
