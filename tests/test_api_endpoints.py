import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

try:
    from fastapi.testclient import TestClient
    from hybrid_rag_wiki.api.app import create_app
except Exception:  # pragma: no cover - environment dependency fallback
    TestClient = None
    create_app = None


@unittest.skipIf(TestClient is None or create_app is None, "fastapi/testclient not installed")
class ApiEndpointTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def test_import_and_graph(self) -> None:
        payload = {
            "files": [
                {"path": "vault/a.md", "raw_markdown": "[[b]]"},
                {"path": "vault/b.md", "raw_markdown": "[to a](a.md)"},
            ]
        }
        import_res = self.client.post("/api/import/markdown", json=payload)
        self.assertEqual(import_res.status_code, 200)
        body = import_res.json()
        self.assertEqual(body["imported_document_count"], 2)

        graph_res = self.client.get("/api/graph")
        self.assertEqual(graph_res.status_code, 200)
        graph = graph_res.json()
        self.assertEqual(graph["metrics"]["node_count"], 2)
        self.assertEqual(graph["metrics"]["edge_count"], 2)

    def test_document_detail_and_search(self) -> None:
        payload = {
            "files": [
                {"path": "notes/topic_one.md", "raw_markdown": "hello"},
            ]
        }
        self.client.post("/api/import/markdown", json=payload)

        search_res = self.client.get("/api/search", params={"q": "topic"})
        self.assertEqual(search_res.status_code, 200)
        results = search_res.json()["results"]
        self.assertTrue(len(results) >= 1)

        doc_id = results[0]["id"]
        doc_res = self.client.get(f"/api/documents/{doc_id}")
        self.assertEqual(doc_res.status_code, 200)
        self.assertEqual(doc_res.json()["id"], doc_id)

    def test_document_not_found(self) -> None:
        res = self.client.get("/api/documents/999999")
        self.assertEqual(res.status_code, 404)


if __name__ == "__main__":
    unittest.main()
