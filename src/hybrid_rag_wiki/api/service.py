from __future__ import annotations

from dataclasses import dataclass

from hybrid_rag_wiki.ingestion.repository import IngestionRepository


@dataclass(frozen=True)
class GraphPayload:
    nodes: list[dict]
    edges: list[dict]
    metrics: dict


class GraphQueryService:
    def __init__(self, repository: IngestionRepository) -> None:
        self._repo = repository

    def build_graph(self) -> GraphPayload:
        documents = self._repo.list_documents()
        links = self._repo.list_links()

        nodes = [
            {
                "id": doc.id,
                "title": doc.title,
                "path": doc.path,
            }
            for doc in sorted(documents, key=lambda d: d.path)
        ]

        edges = [
            {
                "source_document_id": link.source_document_id,
                "target_document_id": link.target_document_id,
                "target_path_raw": link.target_path_raw,
                "link_type": link.link_type,
            }
            for link in links
        ]

        inbound_counts: dict[int, int] = {doc.id: 0 for doc in documents}
        unresolved = 0
        for link in links:
            if link.target_document_id is None:
                unresolved += 1
                continue
            inbound_counts[link.target_document_id] = inbound_counts.get(link.target_document_id, 0) + 1

        orphan_node_count = sum(1 for doc_id in inbound_counts if inbound_counts[doc_id] == 0)

        metrics = {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "unresolved_edge_count": unresolved,
            "orphan_node_count": orphan_node_count,
        }

        return GraphPayload(nodes=nodes, edges=edges, metrics=metrics)
