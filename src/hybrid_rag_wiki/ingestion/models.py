from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IngestionInputFile:
    path: str
    raw_markdown: str


@dataclass(frozen=True)
class ParsedLink:
    source_path: str
    target_path_raw: str
    target_path_normalized: str | None
    link_type: str


@dataclass(frozen=True)
class LinkRecord:
    source_document_id: int
    target_path_raw: str
    target_document_id: int | None
    link_type: str


@dataclass(frozen=True)
class IngestionDiagnostics:
    unresolved_links: list[ParsedLink]
    orphan_document_paths: list[str]


@dataclass(frozen=True)
class IngestionResult:
    imported_document_count: int
    parsed_link_count: int
    resolved_link_count: int
    unresolved_link_count: int
    diagnostics: IngestionDiagnostics
