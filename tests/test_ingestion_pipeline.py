import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hybrid_rag_wiki.ingestion import InMemoryIngestionRepository, IngestionInputFile, MarkdownIngestionPipeline


class IngestionPipelineTests(unittest.TestCase):
    def test_ingest_parses_and_resolves_links(self) -> None:
        repo = InMemoryIngestionRepository()
        pipeline = MarkdownIngestionPipeline(repo)

        files = [
            IngestionInputFile(
                path="notes/alpha.md",
                raw_markdown="See [[beta]] and [gamma](notes/gamma.md)",
            ),
            IngestionInputFile(
                path="notes/beta.md",
                raw_markdown="Backlink to [[alpha]]",
            ),
            IngestionInputFile(
                path="notes/gamma.md",
                raw_markdown="No links",
            ),
        ]

        result = pipeline.ingest(files)

        self.assertEqual(result.imported_document_count, 3)
        self.assertEqual(result.parsed_link_count, 3)
        self.assertEqual(result.resolved_link_count, 3)
        self.assertEqual(result.unresolved_link_count, 0)
        self.assertEqual(result.diagnostics.unresolved_links, [])

    def test_unresolved_and_external_links(self) -> None:
        repo = InMemoryIngestionRepository()
        pipeline = MarkdownIngestionPipeline(repo)

        files = [
            IngestionInputFile(
                path="A.md",
                raw_markdown=(
                    "[[Missing Page]] "
                    "[external](https://example.com) "
                    "[internal](B.md)"
                ),
            ),
        ]

        result = pipeline.ingest(files)

        self.assertEqual(result.parsed_link_count, 2)
        self.assertEqual(result.resolved_link_count, 0)
        self.assertEqual(result.unresolved_link_count, 2)
        self.assertEqual(len(result.diagnostics.unresolved_links), 2)
        self.assertIn("A.md", result.diagnostics.orphan_document_paths)


if __name__ == "__main__":
    unittest.main()
