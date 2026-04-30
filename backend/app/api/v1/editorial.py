from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings
from app.integrations.wordpress import wordpress_client
from app.schemas.editorial import (
    ArticleDetailResponse,
    ArticlePackageResponse,
    EditorialSystemStatusResponse,
    GeneratePautasRequest,
    GeneratePautasResponse,
    PublishArticleRequest,
    PublishArticleResponse,
    SyncWordPressStatusResponse,
)
from app.services.article_package_service import article_package_service
from app.services.excel_editorial_service import excel_editorial_service
from app.services.editorial_file_service import editorial_file_service
from app.services.openai_image_service import openai_image_service
from app.services.editorial_publish_service import editorial_publish_service
from app.services.openai_editorial_service import openai_editorial_service

router = APIRouter()


@router.get("/system/status", response_model=EditorialSystemStatusResponse)
def get_editorial_system_status():
    wordpress_configured = bool(
        settings.WORDPRESS_URL and settings.WORDPRESS_USERNAME and settings.WORDPRESS_APPLICATION_PASSWORD
    )
    return EditorialSystemStatusResponse(
        openai_configured=bool(settings.OPENAI_API_KEY),
        image_generation_enabled=bool(settings.OPENAI_API_KEY),
        websearch_enabled=settings.OPENAI_WEBSEARCH_ENABLED,
        wordpress_url=settings.WORDPRESS_URL,
        wordpress_configured=wordpress_configured,
        wordpress_connection_ok=wordpress_client.test_connection() if wordpress_configured else False,
        excel_path=settings.EXCEL_PAUTAS_PATH,
        generated_articles_dir=settings.GENERATED_ARTICLES_DIR,
        generated_images_dir=settings.GENERATED_IMAGES_DIR,
        backups_dir=settings.BACKUPS_DIR,
    )


@router.get("/pautas")
def list_excel_pautas():
    try:
        pautas = excel_editorial_service.list_pautas()
        if not pautas:
            pautas = excel_editorial_service.seed_initial_pautas()
        return [pauta.model_dump(by_alias=True) for pauta in pautas]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao ler planilha Excel: {exc}")


@router.get("/pautas/{pauta_id}")
def get_excel_pauta(pauta_id: str):
    pauta = excel_editorial_service.get_pauta_by_id(pauta_id)
    if not pauta:
        raise HTTPException(status_code=404, detail="Pauta nao encontrada na planilha Excel")
    return pauta.model_dump(by_alias=True)


@router.post("/pautas/generate", response_model=GeneratePautasResponse)
def generate_excel_pautas(payload: GeneratePautasRequest):
    try:
        existing = excel_editorial_service.list_pautas()
        next_id = excel_editorial_service.next_id()
        created = openai_editorial_service.generate_pautas(payload, existing, next_id)
        excel_editorial_service.append_pautas(created)
        return GeneratePautasResponse(created_count=len(created), pautas=created)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar pautas na planilha Excel: {exc}")


@router.post("/pautas/sync-wordpress", response_model=SyncWordPressStatusResponse)
def sync_excel_pautas_with_wordpress():
    try:
        result = editorial_publish_service.sync_wordpress_status()
        return SyncWordPressStatusResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao sincronizar status com o WordPress: {exc}")


@router.post("/articles/{pauta_id}/generate", response_model=ArticlePackageResponse)
def generate_article_from_excel(pauta_id: str):
    pauta = excel_editorial_service.get_pauta_by_id(pauta_id)
    if not pauta:
        raise HTTPException(status_code=404, detail="Pauta nao encontrada na planilha Excel")
    try:
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
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar artigo: {exc}")


@router.get("/articles/{pauta_id}", response_model=ArticleDetailResponse)
def get_generated_article(pauta_id: str):
    pauta = excel_editorial_service.get_pauta_by_id(pauta_id)
    if not pauta:
        raise HTTPException(status_code=404, detail="Pauta nao encontrada na planilha Excel")
    try:
        slug = editorial_file_service.find_slug_by_pauta_id(pauta_id)
        package = editorial_file_service.load_package(slug)
        return ArticleDetailResponse(**package)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao ler artigo gerado: {exc}")


@router.get("/articles/{pauta_id}/image")
def get_generated_article_image(pauta_id: str):
    try:
        image_path = editorial_file_service.get_image_path(pauta_id)
        media_type = "image/png"
        return FileResponse(path=image_path, media_type=media_type, filename=image_path.name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar imagem gerada: {exc}")


@router.post("/articles/publish", response_model=PublishArticleResponse)
def publish_article(payload: PublishArticleRequest):
    try:
        result = editorial_publish_service.publish(
            slug=payload.slug,
            pauta_id=payload.pauta_id,
            publish_status=payload.publish_status,
        )
        return PublishArticleResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao publicar artigo: {exc}")
