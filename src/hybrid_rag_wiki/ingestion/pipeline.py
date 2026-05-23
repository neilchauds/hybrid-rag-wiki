from __future__ import annotations

from .models import IngestionDiagnostics, IngestionInputFile, IngestionResult, LinkRecord, ParsedLink
from .normalize import build_title_from_path, normalize_document_path
from .parser import parse_links
from .repository import IngestionRepository


class MarkdownIngestionPipeline:
    def __init__(self, repository: IngestionRepository) -> None:
        self._repo = repository

    def ingest(self, files: list[IngestionInputFile]) -> IngestionResult:
        if not files:
            return IngestionResult(
                imported_document_count=0,
                parsed_link_count=0,
                resolved_link_count=0,
                unresolved_link_count=0,
                diagnostics=IngestionDiagnostics(unresolved_links=[], orphan_document_paths=[]),
            )

        upserted_ids: set[int] = set()

        for file in files:
            normalized_path = normalize_document_path(file.path)
            title = build_title_from_path(normalized_path)
            document = self._repo.upsert_document(
                path=normalized_path,
                title=title,
                raw_markdown=file.raw_markdown,
            )
            upserted_ids.add(document.id)

        documents_by_path = self._repo.list_documents_by_path()

        parsed_links: list[ParsedLink] = []
        for file in files:
            source_path = normalize_document_path(file.path)
            parsed_links.extend(parse_links(source_path, file.raw_markdown))

        link_rows: list[LinkRecord] = []
        unresolved_links: list[ParsedLink] = []
        inbound_counts: dict[int, int] = {doc.id: 0 for doc in documents_by_path.values()}

        for parsed in parsed_links:
            source_doc = documents_by_path[parsed.source_path]
            target_doc_id = None

            if parsed.target_path_normalized:
                target_doc = documents_by_path.get(parsed.target_path_normalized)
                if target_doc is not None:
                    target_doc_id = target_doc.id
                    inbound_counts[target_doc_id] = inbound_counts.get(target_doc_id, 0) + 1

            if target_doc_id is None:
                unresolved_links.append(parsed)

            link_rows.append(
                LinkRecord(
                    source_document_id=source_doc.id,
                    target_path_raw=parsed.target_path_raw,
                    target_document_id=target_doc_id,
                    link_type=parsed.link_type,
                )
            )

        self._repo.replace_links_for_sources(source_document_ids=upserted_ids, links=link_rows)

        orphan_paths = [
            doc.path
            for doc in documents_by_path.values()
            if inbound_counts.get(doc.id, 0) == 0
        ]

        resolved_count = len([row for row in link_rows if row.target_document_id is not None])

        return IngestionResult(
            imported_document_count=len(files),
            parsed_link_count=len(parsed_links),
            resolved_link_count=resolved_count,
            unresolved_link_count=len(unresolved_links),
            diagnostics=IngestionDiagnostics(
                unresolved_links=unresolved_links,
                orphan_document_paths=sorted(orphan_paths),
            ),
        )
