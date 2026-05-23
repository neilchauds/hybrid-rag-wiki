-- Optional read model for graph rendering payload assembly

BEGIN;

CREATE OR REPLACE VIEW graph_edges AS
SELECT
    l.id,
    l.source_document_id,
    sd.path AS source_path,
    l.target_path_raw,
    l.target_document_id,
    td.path AS target_path,
    l.link_type
FROM links l
JOIN documents sd ON sd.id = l.source_document_id
LEFT JOIN documents td ON td.id = l.target_document_id;

COMMIT;
