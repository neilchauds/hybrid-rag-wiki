# Hybrid RAG Wiki Product Creation Outline

## 1. Markdown-Native Knowledge Graph MVP (Weeks 0-1)
- Build the first usable product slice before broader architecture work.
- Core MVP experience:
  - Upload markdown files.
  - Parse wiki links between files.
  - Build a graph from file nodes and link edges.
  - Visualize and explore the graph in an Obsidian-like interface.
- MVP users: single user in one workspace.
- Success metrics:
  - import success rate
  - link extraction accuracy
  - graph render performance
  - time-to-first-graph under 60 seconds for a starter vault

## 2. Architecture Foundation (Week 2)
- Stand up core services: PostgreSQL (system of record), Qdrant (semantic retrieval), API backend (FastAPI).
- Implement multi-tenant model with strict tenant isolation (RLS + auth-aware queries).
- Define canonical data contracts: documents, entities, links, communities, provenance.

## 3. Virtual Markdown Layer (Week 3)
- Build WebDAV gateway translating file ops (GET/PUT/MKCOL/DELETE) to DB operations.
- Make Obsidian/IDE mountable against virtual filesystem.
- Add optimistic versioning and transaction locking for collision-safe collaboration.

## 4. Ingestion + Compilation Engine (Weeks 4-5)
- Pipeline: source intake (/raw) -> chunking -> embeddings -> entity extraction -> wiki mutation.
- Deterministic entity resolution (alias + similarity checks) to prevent duplicate concept pages.
- Add contradiction detection and provenance linking to exact source spans/timestamps.

## 5. Knowledge Graph Intelligence (Week 6)
- Build k-NN adjacency graph from vectors.
- Run Leiden clustering in async jobs to form emergent topic communities.
- Auto-generate and maintain index/summary pages per community.

## 6. Hybrid Retrieval + Answer Conservation (Week 7)
- Unified query engine combines vector hits, structured wiki context, entity pages, and provenance.
- Exploratory answer conservation: valuable answers become first-class linked markdown nodes.
- Add challenge mode prompts for counter-evidence and weak-link detection.

## 7. Self-Healing Operations (Week 8)
- Scheduled lint passes: dead links, orphan entities, missing summary pages, unresolved conflicts.
- Automated repair suggestions and optional auto-fix routines.
- Quality dashboards for graph health and content freshness.

## 8. Security, Observability, and Governance (Week 9)
- Tenant-aware auth at WebDAV + API boundary; audit logs for every mutation.
- Monitoring: ingestion latency, query latency, hallucination/error rate, sync failures.
- Policy controls for write permissions (human vs agent), review gates, rollback/version history.

## 9. Pilot Launch and Iteration (Weeks 10-11)
- Launch with 3-5 pilot users (research + student + team use cases).
- Collect qualitative/quantitative feedback on trust, retrieval quality, and workflow speed.
- Prioritize V2 roadmap: agent workflows, richer UI graph operations, enterprise admin tooling.
