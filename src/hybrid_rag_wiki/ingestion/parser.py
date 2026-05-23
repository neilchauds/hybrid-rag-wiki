from __future__ import annotations

import re

from .models import ParsedLink
from .normalize import normalize_link_target

WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^\)]+)\)")


def parse_links(source_path: str, raw_markdown: str) -> list[ParsedLink]:
    links: list[ParsedLink] = []

    for match in WIKI_LINK_RE.finditer(raw_markdown):
        raw = match.group(1).strip()
        target_raw = raw.split("|", 1)[0].strip()
        normalized = normalize_link_target(source_path, target_raw)
        links.append(
            ParsedLink(
                source_path=source_path,
                target_path_raw=target_raw,
                target_path_normalized=normalized,
                link_type="wiki",
            )
        )

    for match in MARKDOWN_LINK_RE.finditer(raw_markdown):
        target_raw = match.group(1).strip()
        normalized = normalize_link_target(source_path, target_raw)
        if normalized is None:
            continue
        links.append(
            ParsedLink(
                source_path=source_path,
                target_path_raw=target_raw,
                target_path_normalized=normalized,
                link_type="markdown",
            )
        )

    return links
