from __future__ import annotations

import re

from bs4 import BeautifulSoup


def extract_main_content(soup: BeautifulSoup) -> str:
    soup = BeautifulSoup(str(soup), "lxml")

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
