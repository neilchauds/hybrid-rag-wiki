# Hybrid RAG Wiki MVP

## Run the app

1. Install dependencies:

```bash
pip install -e .
```

2. Start the API + graph viewer:

```bash
uvicorn hybrid_rag_wiki.api.app:app --reload
```

3. Open:

- http://127.0.0.1:8000/

## Implemented MVP steps

- Step 1.1: Data model (SQL migrations)
- Step 1.2: Ingestion pipeline
- Step 1.3: API endpoints
- Step 1.4: Graph viewer UI (interactive canvas + node inspector)

## API endpoints

- `POST /api/import/markdown`
- `GET /api/graph`
- `GET /api/documents/{document_id}`
- `GET /api/search?q=...`
