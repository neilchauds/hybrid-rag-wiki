# Part 2 Outline: Designing the Core Data Model

## Objective
Design a multi-tenant, provenance-first core data model that supports:
- Virtual markdown files over WebDAV
- Hybrid retrieval (structured + vector)
- Deterministic entity resolution
- Graph relationships and clustering
- Safe concurrent collaboration

## 1. Design Principles
- Tenant isolation by default: every domain table is tenant-scoped.
- Provenance everywhere: every compiled assertion is traceable to source spans.
- Append + version strategy: preserve history while exposing latest materialized state.
- Deterministic before generative: use constraints and matching policies before LLM writes.
- Retrieval-ready schema: optimize for both transactional writes and query-time composition.

## 2. Core Domain Entities
- tenants: organization/workspace boundary.
- users: authenticated principals.
- memberships: user-to-tenant roles and permissions.
- raw_sources: immutable ingestion artifacts (PDF, transcript, URL clip, CSV).
- wiki_documents: virtual markdown file objects (path, content, frontmatter, version).
- document_versions: immutable snapshots per save/mutation.
- document_sections: parsed logical sections/chunks for targeting updates.
- entities: canonical concepts/people/projects with aliases.
- entity_mentions: source/document-level mentions linked to entities.
- relationships: typed edges between entities.
- claims: normalized assertions extracted/compiled from sources.
- claim_evidence: many-to-many mapping of claims to source spans.
- contradictions: tracked claim conflicts + resolution state.
- embeddings: vectors for chunks/entities/claims with model metadata.
- communities: cluster/group nodes from Leiden runs.
- community_membership: membership mapping for docs/entities/chunks to communities.
- jobs: async pipeline tasks and statuses.
- audit_events: immutable mutation and access log.

## 3. Key Relationship Map
- tenant 1->N wiki_documents, entities, raw_sources, jobs, audit_events.
- wiki_document 1->N document_versions and document_sections.
- raw_source 1->N source_spans/chunks.
- entity 1->N entity_mentions.
- entity N<->N entity via relationships.
- claim N<->N source evidence via claim_evidence.
- contradiction links claim <-> claim.
- embeddings attach polymorphically to sections, entities, and claims.
- community N<->N members via community_membership.

## 4. Schema Conventions and Constraints
- Primary keys: UUID v7 (sortable) for all major tables.
- Timestamps: created_at/updated_at (TIMESTAMPTZ).
- Soft delete where needed (deleted_at) for collaborative recovery.
- Uniques:
  - (tenant_id, virtual_path) on wiki_documents
  - (tenant_id, canonical_name) on entities
  - (tenant_id, external_source_fingerprint) on raw_sources
- Referential integrity with ON DELETE rules:
  - CASCADE for strongly-owned children
  - RESTRICT for governance-critical records (audit/provenance)
- Optimistic locking field on wiki_documents (version integer).

## 5. Provenance and Citation Model
- Introduce source_spans table:
  - source_id, locator_type (page/paragraph/timestamp/url_fragment), locator_value, text_excerpt_hash.
- claim_evidence joins claims -> source_spans with confidence and extraction metadata.
- Every generated wiki mutation stores:
  - triggering_job_id
  - source_span_ids used
  - model + prompt template version
- Outcome: each synthesized line can be traced and re-verified.

## 6. Multi-Tenant Security Model
- PostgreSQL Row Level Security on all tenant-scoped tables.
- Session context requires tenant_id and user_id claims.
- Security-definer functions for controlled cross-table writes.
- Separate service roles:
  - api_role (request-scoped)
  - worker_role (async ingestion/compilation)
  - admin_role (migration/ops only)

## 7. Retrieval-Oriented Read Models
- Transactional write tables remain normalized.
- Add derived/materialized views for query-time performance:
  - document_context_view (document + sections + entity refs)
  - entity_profile_view (entity + relationships + latest evidence-backed summary)
  - claim_conflict_view (active contradictions)
- Hybrid retrieval contract:
  - vector prefilter (embeddings)
  - relational expansion (claims/entities/sections)
  - provenance packaging for final prompt.

## 8. Concurrency and Versioning Strategy
- WebDAV PUT flow:
  - check version
  - SELECT ... FOR UPDATE wiki_documents row
  - persist document_versions snapshot
  - update latest wiki_documents content/version
- Conflict behavior:
  - return conflict on stale version
  - optional server-side merge job for non-overlapping section edits
- Maintain immutable history for rollback and audit.

## 9. Implementation Milestones (Part 2)
1. Draft ERD and validate with 3 representative workflows:
   - new source ingestion
   - wiki page compile/update
   - user query with citation trace
2. Author SQL migrations for base tables + constraints.
3. Implement RLS policies and role matrix tests.
4. Build seed data and fixtures for multi-tenant integration tests.
5. Add provenance and contradiction test cases.
6. Benchmark critical queries and add first materialized views.
7. Freeze v1 schema contract for Part 3 WebDAV gateway build.

## 10. Definition of Done for Part 2
- ERD reviewed and accepted.
- Migrations run cleanly in fresh environment.
- RLS tests pass (no cross-tenant leakage).
- Provenance trace works end-to-end for sample compiled answer.
- Core query paths meet baseline latency targets.
- Schema docs published for API and worker teams.
