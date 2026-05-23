from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from hybrid_rag_wiki.api.schemas import (
    DocumentResponse,
    GraphMetrics,
    GraphResponse,
    ImportRequest,
    ImportResponse,
    SearchResponse,
    UnresolvedLinkResponse,
)
from hybrid_rag_wiki.api.service import GraphQueryService
from hybrid_rag_wiki.ingestion import InMemoryIngestionRepository, IngestionInputFile, MarkdownIngestionPipeline

def create_app() -> FastAPI:
    app = FastAPI(title="Hybrid RAG Wiki API", version="0.1.0")
    web_dir = Path(__file__).resolve().parents[1] / "web"

    repo = InMemoryIngestionRepository()
    pipeline = MarkdownIngestionPipeline(repository=repo)
    graph_service = GraphQueryService(repository=repo)
    app.mount("/web", StaticFiles(directory=str(web_dir)), name="web")

    @app.get("/")
    def home() -> FileResponse:
        return FileResponse(web_dir / "index.html")

    @app.post("/api/import/markdown", response_model=ImportResponse)
    def import_markdown(payload: ImportRequest) -> ImportResponse:
        files = [
            IngestionInputFile(path=item.path, raw_markdown=item.raw_markdown)
            for item in payload.files
        ]
        result = pipeline.ingest(files)
        return ImportResponse(
            imported_document_count=result.imported_document_count,
            parsed_link_count=result.parsed_link_count,
            resolved_link_count=result.resolved_link_count,
            unresolved_link_count=result.unresolved_link_count,
            unresolved_links=[
                UnresolvedLinkResponse(
                    source_path=link.source_path,
                    target_path_raw=link.target_path_raw,
                    target_path_normalized=link.target_path_normalized,
                    link_type=link.link_type,
                )
                for link in result.diagnostics.unresolved_links
            ],
            orphan_document_paths=result.diagnostics.orphan_document_paths,
        )

    @app.get("/api/graph", response_model=GraphResponse)
    def get_graph() -> GraphResponse:
        payload = graph_service.build_graph()
        return GraphResponse(
            nodes=payload.nodes,
            edges=payload.edges,
            metrics=GraphMetrics(**payload.metrics),
        )

    @app.get("/api/documents/{document_id}", response_model=DocumentResponse)
    def get_document(document_id: int) -> DocumentResponse:
        doc = repo.get_document_by_id(document_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")

        return DocumentResponse(
            id=doc.id,
            title=doc.title,
            path=doc.path,
            raw_markdown=doc.raw_markdown,
        )

    @app.get("/api/search", response_model=SearchResponse)
    def search_documents(q: str = Query(default="", min_length=0), limit: int = Query(default=20, ge=1, le=100)) -> SearchResponse:
        rows = repo.search_documents(query=q, limit=limit)
        return SearchResponse(
            results=[
                DocumentResponse(
                    id=doc.id,
                    title=doc.title,
                    path=doc.path,
                    raw_markdown=doc.raw_markdown,
                )
                for doc in rows
            ]
        )

    return app


app = create_app()
