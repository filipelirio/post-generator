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
from app.schemas.editorial import AutomationRunRequest, AutomationRunResponse, PublishArticleRequest, SheetPauta
from app.services.editorial_cron_service import EditorialCronService
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

    def test_publication_stores_wordpress_date_and_time(self) -> None:
        service = EditorialPublishService()
        package = {
            "slug": "artigo-publicado",
            "pauta_id": "8",
            "title": "Titulo",
            "content_html": "<p>Conteudo</p>",
            "seo_title": "SEO",
            "meta_desc": "Meta",
            "focus_kw": "keyword",
            "category": "",
            "tags": [],
            "image": {},
        }
        pauta = build_pauta("8")

        class FakeWordPress:
            def get_post_by_slug(self, slug, status="any"):
                return None

            def create_post(self, payload):
                return {
                    "id": 88,
                    "link": "https://example.test/publicado",
                    "featured_media": 0,
                    "date": "2026-05-27T09:42:00",
                }

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
            patch("app.services.editorial_publish_service.editorial_file_service.find_slug_by_pauta_id", return_value="artigo-publicado"),
            patch("app.services.editorial_publish_service.editorial_file_service.load_package", return_value=package),
            patch("app.services.editorial_publish_service.wordpress_client", FakeWordPress()),
            patch("app.services.editorial_publish_service.excel_editorial_service", fake_excel),
        ):
            service.publish(pauta_id="8", publish_status="publish")

        self.assertEqual(fake_excel.updates["Data publicacao"], "2026-05-27T09:42:00")

    def test_sync_refreshes_legacy_date_with_wordpress_publication_time(self) -> None:
        service = EditorialPublishService()
        pauta = build_pauta("1").model_copy(
            update={
                "status": "Publicado",
                "url_wordpress": "https://example.test/artigo",
                "data_publicacao": "2026-04-30",
            }
        )

        class FakeWordPress:
            def get_post_by_url(self, url):
                return {
                    "id": 1,
                    "status": "publish",
                    "link": url,
                    "date": "2026-04-30T16:25:00",
                }

        class FakeExcel:
            def __init__(self):
                self.updates = {}

            def list_pautas(self):
                return [pauta]

            def update_row(self, pauta_id, updates):
                self.updates = updates

        fake_excel = FakeExcel()
        with (
            patch("app.services.editorial_publish_service.wordpress_client", FakeWordPress()),
            patch("app.services.editorial_publish_service.excel_editorial_service", fake_excel),
        ):
            service.sync_wordpress_status()

        self.assertEqual(fake_excel.updates["Data publicacao"], "2026-04-30T16:25:00")


class CronServiceTests(unittest.TestCase):
    class FakeExcel:
        def __init__(self, pautas):
            self.pautas = pautas

        def list_pautas(self):
            return self.pautas

    class FakeArticle:
        def __init__(self):
            self.generated = []

        def generate(self, pauta_id):
            self.generated.append(pauta_id)

    class FakePublish:
        def __init__(self):
            self.published = []

        def publish(self, pauta_id, publish_status):
            self.published.append((pauta_id, publish_status))
            return {"message": "ok"}

    def test_dry_run_has_no_side_effects(self) -> None:
        article = self.FakeArticle()
        publisher = self.FakePublish()
        service = EditorialCronService(
            excel_service=self.FakeExcel([build_pauta("1")]),
            article_service=article,
            publish_service=publisher,
        )

        result = service.run(AutomationRunRequest(mode="draft", dry_run=True))

        self.assertEqual(result.actions[0].action, "would_create_wordpress_draft")
        self.assertEqual(article.generated, [])
        self.assertEqual(publisher.published, [])

    def test_publish_only_selects_existing_draft_by_default(self) -> None:
        article = self.FakeArticle()
        publisher = self.FakePublish()
        pending = build_pauta("1")
        draft = build_pauta("2").model_copy(update={"status": "Rascunho"})
        service = EditorialCronService(
            excel_service=self.FakeExcel([pending, draft]),
            article_service=article,
            publish_service=publisher,
        )

        result = service.run(AutomationRunRequest(mode="publish", dry_run=False))

        self.assertEqual(result.actions[0].pauta_id, "2")
        self.assertEqual(publisher.published, [("2", "publish")])
        self.assertEqual(article.generated, [])

    def test_draft_generates_pending_article_before_creating_wordpress_draft(self) -> None:
        article = self.FakeArticle()
        publisher = self.FakePublish()
        service = EditorialCronService(
            excel_service=self.FakeExcel([build_pauta("3")]),
            article_service=article,
            publish_service=publisher,
        )

        result = service.run(AutomationRunRequest(mode="draft", dry_run=False))

        self.assertEqual(result.actions[0].resulting_status, "Rascunho")
        self.assertEqual(article.generated, ["3"])
        self.assertEqual(publisher.published, [("3", "draft")])

    def test_direct_publish_generates_pending_article_and_publishes_in_same_cycle(self) -> None:
        article = self.FakeArticle()
        publisher = self.FakePublish()
        service = EditorialCronService(
            excel_service=self.FakeExcel([build_pauta("4")]),
            article_service=article,
            publish_service=publisher,
        )

        result = service.run(
            AutomationRunRequest(mode="publish", dry_run=False, allow_unreviewed_publish=True)
        )

        self.assertEqual(result.actions[0].resulting_status, "Publicado")
        self.assertEqual(article.generated, ["4"])
        self.assertEqual(publisher.published, [("4", "publish")])

    def test_direct_publish_dry_run_describes_generation_and_publication(self) -> None:
        service = EditorialCronService(
            excel_service=self.FakeExcel([build_pauta("5")]),
            article_service=self.FakeArticle(),
            publish_service=self.FakePublish(),
        )

        result = service.run(
            AutomationRunRequest(mode="publish", dry_run=True, allow_unreviewed_publish=True)
        )

        self.assertEqual(result.actions[0].action, "would_generate_and_publish_wordpress_post")


class CronEndpointTests(unittest.TestCase):
    def test_automation_endpoint_requires_token(self) -> None:
        client = TestClient(app)
        with (
            patch.object(settings, "CRON_ENABLED", True),
            patch.object(settings, "CRON_TOKEN", "segredo"),
        ):
            response = client.post("/api/v1/editorial/automation/run", json={"dry_run": True})

        self.assertEqual(response.status_code, 401)

    def test_automation_endpoint_runs_with_valid_token(self) -> None:
        client = TestClient(app)
        expected = AutomationRunResponse(mode="generate_only", dry_run=True, processed_count=0)
        with (
            patch.object(settings, "CRON_ENABLED", True),
            patch.object(settings, "CRON_TOKEN", "segredo"),
            patch("app.api.v1.editorial.editorial_cron_service.run", return_value=expected),
        ):
            response = client.post(
                "/api/v1/editorial/automation/run",
                json={"dry_run": True},
                headers={"X-Cron-Token": "segredo"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["dry_run"])

    def test_automation_endpoint_blocks_execution_while_dry_run_setting_is_enabled(self) -> None:
        client = TestClient(app)
        with (
            patch.object(settings, "CRON_ENABLED", True),
            patch.object(settings, "CRON_TOKEN", "segredo"),
            patch.object(settings, "CRON_DRY_RUN", True),
        ):
            response = client.post(
                "/api/v1/editorial/automation/run",
                json={"dry_run": False},
                headers={"X-Cron-Token": "segredo"},
            )

        self.assertEqual(response.status_code, 409)

    def test_automation_endpoint_blocks_unreviewed_publication_by_default(self) -> None:
        client = TestClient(app)
        with (
            patch.object(settings, "CRON_ENABLED", True),
            patch.object(settings, "CRON_TOKEN", "segredo"),
            patch.object(settings, "CRON_ALLOW_UNREVIEWED_PUBLISH", False),
        ):
            response = client.post(
                "/api/v1/editorial/automation/run",
                json={"dry_run": True, "mode": "publish", "allow_unreviewed_publish": True},
                headers={"X-Cron-Token": "segredo"},
            )

        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main()
