import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import settings
from app.integrations.wordpress import WordPressClient
from app.main import app
from app.schemas.editorial import PublishArticleRequest, SheetPauta
from app.services.editorial_publish_service import EditorialPublishService
from app.services.excel_editorial_service import ExcelEditorialService
from app.services.html_sanitizer_service import sanitize_html


def build_pauta(pauta_id: str = "1") -> SheetPauta:
    return SheetPauta(**{"ID": pauta_id, "Tema": "Pauta de teste"})


class HtmlSanitizerTests(unittest.TestCase):
    def test_removes_unsafe_markup_and_anchor_attributes(self) -> None:
        result = sanitize_html(
            '<script>alert(1)</script><p>Texto <a href="javascript:alert(1)" target="_blank">link</a></p>'
        )

        self.assertNotIn("<script", result)
        self.assertNotIn("javascript:", result)
        self.assertNotIn("target=", result)
        self.assertIn("<p>Texto <a>link</a></p>", result)


class SecurityConfigurationTests(unittest.TestCase):
    def test_cors_allows_local_dashboard_but_not_unknown_origin(self) -> None:
        client = TestClient(app)
        allowed = client.get("/health", headers={"Origin": "http://localhost:3000"})
        unknown = client.get("/health", headers={"Origin": "https://attacker.example"})

        self.assertEqual(allowed.headers.get("access-control-allow-origin"), "http://localhost:3000")
        self.assertIsNone(unknown.headers.get("access-control-allow-origin"))


class PublishSchemaTests(unittest.TestCase):
    def test_rejects_unknown_wordpress_status(self) -> None:
        with self.assertRaises(ValidationError):
            PublishArticleRequest(pauta_id="1", publish_status="delete")


class WordPressClientTests(unittest.TestCase):
    def test_does_not_retry_post_requests_that_could_duplicate_content(self) -> None:
        client = WordPressClient()
        with patch("app.integrations.wordpress.requests.request", side_effect=requests.ConnectionError("falha")) as request:
            with self.assertRaises(Exception):
                client.create_post({"title": "Teste"})

        self.assertEqual(request.call_count, 1)


class ExcelServiceTests(unittest.TestCase):
    def test_assigns_ids_at_write_time_and_creates_unique_backups(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_dir:
            root = Path(temporary_dir)
            with (
                patch.object(settings, "EXCEL_PAUTAS_PATH", str(root / "pautas.xlsx")),
                patch.object(settings, "EXCEL_BACKUPS_DIR", str(root / "backups")),
            ):
                service = ExcelEditorialService()
                first = service.append_pautas([build_pauta("99")], assign_new_ids=True)
                second = service.append_pautas([build_pauta("99")], assign_new_ids=True)

                self.assertEqual(first[0].id, "1")
                self.assertEqual(second[0].id, "2")
                self.assertEqual(len(list((root / "backups").glob("*.xlsx"))), 2)


class PublishServiceTests(unittest.TestCase):
    def test_draft_reuses_existing_slug_and_does_not_set_publish_date(self) -> None:
        service = EditorialPublishService()
        package = {
            "slug": "artigo-existente",
            "pauta_id": "7",
            "title": "Titulo",
            "content_html": "<p>Conteudo</p>",
            "seo_title": "SEO",
            "meta_desc": "Meta",
            "focus_kw": "keyword",
            "category": "",
            "tags": [],
            "image": {},
        }
        pauta = build_pauta("7")

        class FakeWordPress:
            def get_post_by_slug(self, slug, status="any"):
                return {"id": 42}

            def update_post(self, post_id, payload):
                return {"id": post_id, "link": "https://example.test/post", "featured_media": 0}

            def create_post(self, payload):
                raise AssertionError("Nao deveria criar novo post.")

            def update_yoast(self, **kwargs):
                return {}

        class FakeExcel:
            def __init__(self):
                self.updates = {}

            def get_pauta_by_id(self, pauta_id):
                return pauta

            def update_row(self, pauta_id, updates):
                self.updates = updates

        fake_excel = FakeExcel()
        with (
            patch("app.services.editorial_publish_service.editorial_file_service.find_slug_by_pauta_id", return_value="artigo-existente"),
            patch("app.services.editorial_publish_service.editorial_file_service.load_package", return_value=package),
            patch("app.services.editorial_publish_service.wordpress_client", FakeWordPress()),
            patch("app.services.editorial_publish_service.excel_editorial_service", fake_excel),
        ):
            result = service.publish(pauta_id="7", publish_status="draft")

        self.assertEqual(result["post_id"], 42)
        self.assertNotIn("Data publicacao", fake_excel.updates)
        self.assertEqual(fake_excel.updates["WordPress Post ID"], "42")


if __name__ == "__main__":
    unittest.main()
