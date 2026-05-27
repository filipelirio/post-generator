from app.schemas.editorial import ArticlePackageResponse
from app.services.article_package_service import article_package_service
from app.services.excel_editorial_service import excel_editorial_service
from app.services.openai_editorial_service import openai_editorial_service
from app.services.openai_image_service import openai_image_service


class PautaNotFoundError(ValueError):
    pass


class EditorialArticleService:
    def generate(self, pauta_id: str) -> ArticlePackageResponse:
        pauta = excel_editorial_service.get_pauta_by_id(pauta_id)
        if not pauta:
            raise PautaNotFoundError("Pauta nao encontrada na planilha Excel")

        article_payload = openai_editorial_service.generate_article_package(pauta)
        article_payload["pauta_id"] = article_payload.get("pauta_id") or pauta.id
        article_payload["categoria"] = pauta.categoria
        image_prompt = article_payload.get("imagem_prompt", "").strip()
        if image_prompt:
            image_path = openai_image_service.generate_cover(article_payload["slug"], image_prompt)
            article_payload["imagem_tipo"] = "local"
            article_payload["imagem_caminho"] = image_path
            article_payload["imagem_url"] = ""

        written = article_package_service.write_package(article_payload)
        excel_editorial_service.update_row(pauta_id, {"Status": "Em producao"})
        return ArticlePackageResponse(
            slug=written["slug"],
            article_file=written["article_file"],
            seo_file=written["seo_file"],
            image_file=written["image_file"],
            preview_html=article_payload["preview_html"],
            title=article_payload["titulo"],
            focus_keyword=article_payload["focus_kw"],
        )


editorial_article_service = EditorialArticleService()
