from __future__ import annotations

from pydantic import BaseModel, Field


class ImportFilePayload(BaseModel):
    path: str = Field(min_length=1)
    raw_markdown: str


class ImportRequest(BaseModel):
    files: list[ImportFilePayload] = Field(default_factory=list)


class UnresolvedLinkResponse(BaseModel):
    source_path: str
    target_path_raw: str
    target_path_normalized: str | None
    link_type: str


class ImportResponse(BaseModel):
    imported_document_count: int
    parsed_link_count: int
    resolved_link_count: int
    unresolved_link_count: int
    unresolved_links: list[UnresolvedLinkResponse]
    orphan_document_paths: list[str]


class GraphNode(BaseModel):
    id: int
    title: str
    path: str


class GraphEdge(BaseModel):
    source_document_id: int
    target_document_id: int | None
    target_path_raw: str
    link_type: str


class GraphMetrics(BaseModel):
    node_count: int
    edge_count: int
    unresolved_edge_count: int
    orphan_node_count: int


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    metrics: GraphMetrics


class DocumentResponse(BaseModel):
    id: int
    title: str
    path: str
    raw_markdown: str


class SearchResponse(BaseModel):
    results: list[DocumentResponse]
