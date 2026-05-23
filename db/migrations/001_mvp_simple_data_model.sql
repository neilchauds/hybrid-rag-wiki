-- MVP Step 1: Markdown-native knowledge graph core model
-- Tables: documents, links

BEGIN;

CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    path TEXT NOT NULL,
    raw_markdown TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT documents_path_nonempty CHECK (length(trim(path)) > 0),
    CONSTRAINT documents_title_nonempty CHECK (length(trim(title)) > 0)
);

-- One canonical document row per normalized path.
CREATE UNIQUE INDEX IF NOT EXISTS documents_path_unique_idx
    ON documents (path);

CREATE TABLE IF NOT EXISTS links (
    id BIGSERIAL PRIMARY KEY,
    source_document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    target_path_raw TEXT NOT NULL,
    target_document_id BIGINT REFERENCES documents(id) ON DELETE SET NULL,
    link_type TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT links_target_path_raw_nonempty CHECK (length(trim(target_path_raw)) > 0),
    CONSTRAINT links_link_type_valid CHECK (link_type IN ('wiki', 'markdown'))
);

-- Fast traversal and link-resolution helpers.
CREATE INDEX IF NOT EXISTS links_source_document_id_idx
    ON links (source_document_id);

CREATE INDEX IF NOT EXISTS links_target_document_id_idx
    ON links (target_document_id);

CREATE INDEX IF NOT EXISTS links_target_path_raw_idx
    ON links (target_path_raw);

-- Avoid accidental duplicate edges from parser re-runs in same import behavior.
CREATE UNIQUE INDEX IF NOT EXISTS links_unique_edge_idx
    ON links (source_document_id, target_path_raw, link_type);

-- Helpful update trigger for documents.updated_at
CREATE OR REPLACE FUNCTION set_documents_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_set_documents_updated_at ON documents;

CREATE TRIGGER trg_set_documents_updated_at
BEFORE UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION set_documents_updated_at();

COMMIT;
