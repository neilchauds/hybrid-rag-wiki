# Step 1 Outline: Markdown-Native Knowledge Graph MVP

## Goal
Deliver a usable MVP where a user can upload markdown notes, the system extracts links, and an interactive graph visualizes relationships between notes.

## User Stories
- As a user, I can upload a folder or batch of `.md` files.
- As a user, I can see all notes as nodes in an interactive graph.
- As a user, I can see links (`[[Wiki Links]]` and markdown links) as edges.
- As a user, I can click a node and preview the note content.
- As a user, I can search/filter notes and highlight neighborhoods.

## MVP Scope (In)
- Single-tenant local workspace.
- Markdown ingestion (drag-and-drop or file picker).
- Link extraction:
  - `[[Wiki Links]]`
  - `[label](path/to/file.md)` internal links
- Graph visualization with pan/zoom, node select, edge highlight.
- Basic stats panel: node count, edge count, orphan notes.

## MVP Scope (Out)
- LLM compilation, embeddings, semantic clustering.
- Multi-user collaboration.
- WebDAV sync.
- Advanced permissions and enterprise auth.

## Technical Design

### 1. Data Model (MVP-Simple)
- `documents`
  - id
  - title
  - path
  - raw_markdown
  - updated_at
- `links`
  - id
  - source_document_id
  - target_path_raw
  - target_document_id (nullable until resolved)
  - link_type (`wiki` or `markdown`)
- Optional denormalized `graph_nodes`/`graph_edges` API response model.

### 2. Ingestion Pipeline
- Upload `.md` files.
- Normalize file paths and titles.
- Parse outbound links per file.
- Resolve target links to known documents.
- Persist docs + links.
- Compute orphan/unresolved link diagnostics.

### 3. API Endpoints
- `POST /api/import/markdown` -> batch import files.
- `GET /api/graph` -> graph payload (nodes + edges + metrics).
- `GET /api/documents/:id` -> document detail for preview panel.
- `GET /api/search?q=` -> quick node search.

### 4. Frontend Graph Viewer
- Graph canvas library: Cytoscape.js or React Flow + force layout.
- Node styling:
  - size by degree
  - color by folder/path prefix
- Interactions:
  - zoom/pan
  - select node
  - focus neighborhood depth 1-2
  - click opens right-side markdown preview

### 5. Performance Targets
- 1,000 documents and 5,000 edges load under 2 seconds on modern laptop.
- Incremental re-import should only re-parse changed files.

## Implementation Steps
1. Create ingestion parser module for wiki links + markdown links.
2. Create lightweight DB schema and migration.
3. Build import endpoint and graph endpoint.
4. Build graph UI with node inspector panel.
5. Add unresolved link handling and orphan diagnostics.
6. Add smoke tests with sample vault fixtures.
7. Ship internal alpha and validate UX against Obsidian expectations.

## Acceptance Criteria
- Importing a markdown vault produces visible graph nodes/edges.
- Clicking a node shows corresponding markdown content.
- Broken/unresolved links are surfaced in diagnostics.
- Re-import updates graph accurately without full reset.
- Demoable end-to-end flow in under 5 minutes.

## Risks and Mitigations
- Path resolution mismatch across link formats:
  - use a robust path normalization and alias resolution layer.
- Large graph UI lag:
  - progressive rendering + layout caching.
- Inconsistent markdown syntax in real notes:
  - tolerant parser with clear import warnings.
