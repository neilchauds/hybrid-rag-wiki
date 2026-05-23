from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import LinkRecord


@dataclass(frozen=True)
class DocumentRecord:
    id: int
    path: str
    title: str
    raw_markdown: str


class IngestionRepository(Protocol):
    def upsert_document(self, path: str, title: str, raw_markdown: str) -> DocumentRecord:
        raise NotImplementedError

    def list_documents_by_path(self) -> dict[str, DocumentRecord]:
        raise NotImplementedError

    def replace_links_for_sources(self, source_document_ids: set[int], links: list[LinkRecord]) -> None:
        raise NotImplementedError

    def list_documents(self) -> list[DocumentRecord]:
        raise NotImplementedError

    def list_links(self) -> list[LinkRecord]:
        raise NotImplementedError

    def get_document_by_id(self, document_id: int) -> DocumentRecord | None:
        raise NotImplementedError

    def search_documents(self, query: str, limit: int = 20) -> list[DocumentRecord]:
        raise NotImplementedError


class InMemoryIngestionRepository:
    """Test-friendly repository backing for the MVP ingestion pipeline."""

    def __init__(self) -> None:
        self._documents_by_path: dict[str, DocumentRecord] = {}
        self._documents_by_id: dict[int, DocumentRecord] = {}
        self._links_by_source_id: dict[int, list[LinkRecord]] = {}
        self._next_document_id = 1

    def upsert_document(self, path: str, title: str, raw_markdown: str) -> DocumentRecord:
        existing = self._documents_by_path.get(path)
        if existing is not None:
            updated = DocumentRecord(
                id=existing.id,
                path=path,
                title=title,
                raw_markdown=raw_markdown,
            )
            self._documents_by_path[path] = updated
            self._documents_by_id[existing.id] = updated
            return updated

        record = DocumentRecord(
            id=self._next_document_id,
            path=path,
            title=title,
            raw_markdown=raw_markdown,
        )
        self._next_document_id += 1
        self._documents_by_path[path] = record
        self._documents_by_id[record.id] = record
        return record

    def list_documents_by_path(self) -> dict[str, DocumentRecord]:
        return dict(self._documents_by_path)

    def replace_links_for_sources(self, source_document_ids: set[int], links: list[LinkRecord]) -> None:
        for source_id in source_document_ids:
            self._links_by_source_id[source_id] = []
        for link in links:
            self._links_by_source_id.setdefault(link.source_document_id, []).append(link)

    def list_links(self) -> list[LinkRecord]:
        all_links: list[LinkRecord] = []
        for rows in self._links_by_source_id.values():
            all_links.extend(rows)
        return all_links

    def list_documents(self) -> list[DocumentRecord]:
        return list(self._documents_by_id.values())

    def get_document_by_id(self, document_id: int) -> DocumentRecord | None:
        return self._documents_by_id.get(document_id)

    def search_documents(self, query: str, limit: int = 20) -> list[DocumentRecord]:
        needle = query.strip().lower()
        if not needle:
            return []
        ranked: list[tuple[int, DocumentRecord]] = []
        for doc in self._documents_by_id.values():
            score = 0
            if needle in doc.title.lower():
                score += 3
            if needle in doc.path.lower():
                score += 2
            if needle in doc.raw_markdown.lower():
                score += 1
            if score > 0:
                ranked.append((score, doc))
        ranked.sort(key=lambda x: (-x[0], x[1].path))
        return [doc for _, doc in ranked[:limit]]
