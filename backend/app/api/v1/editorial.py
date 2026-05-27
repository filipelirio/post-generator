import secrets

from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings
from app.integrations.wordpress import wordpress_client
from app.schemas.editorial import (
    ArticleDetailResponse,
    ArticlePackageResponse,
    AutomationRunRequest,
    AutomationRunResponse,
    EditorialConfigurationResponse,
    EditorialConfigurationSaveResponse,
    EditorialConfigurationUpdateRequest,
    EditorialSystemStatusResponse,
    GeneratePautasRequest,
    GeneratePautasResponse,
    PublishArticleRequest,
    PublishArticleResponse,
    SyncWordPressStatusResponse,
)
from app.services.excel_editorial_service import excel_editorial_service
from app.services.editorial_file_service import editorial_file_service
from app.services.editorial_article_service import PautaNotFoundError, editorial_article_service
from app.services.editorial_configuration_service import editorial_configuration_service
from app.services.editorial_cron_service import editorial_cron_service
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
        cron_enabled=settings.CRON_ENABLED,
        cron_mode=settings.CRON_MODE,
        cron_dry_run=settings.CRON_DRY_RUN,
        cron_max_items=settings.CRON_MAX_ITEMS,
        cron_schedule=settings.CRON_SCHEDULE,
        cron_allow_unreviewed_publish=settings.CRON_ALLOW_UNREVIEWED_PUBLISH,
    )


@router.get("/configuration", response_model=EditorialConfigurationResponse)
def get_editorial_configuration():
    return editorial_configuration_service.get_configuration()


@router.put("/configuration", response_model=EditorialConfigurationSaveResponse)
def update_editorial_configuration(payload: EditorialConfigurationUpdateRequest):
    try:
        configuration = editorial_configuration_service.save_configuration(payload)
        return EditorialConfigurationSaveResponse(
            message="Configuracoes salvas. As integracoes ja usam os novos valores.",
            configuration=configuration,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar configuracoes: {exc}")


@router.get("/pautas")
def list_excel_pautas():
    try:
        return [pauta.model_dump(by_alias=True) for pauta in excel_editorial_service.list_pautas()]
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
        if not created:
            raise ValueError("O modelo nao retornou nenhuma pauta valida.")
        created = excel_editorial_service.append_pautas(created, assign_new_ids=True)
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
    try:
        return editorial_article_service.generate(pauta_id)
    except PautaNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
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


@router.post("/automation/run", response_model=AutomationRunResponse)
def run_editorial_automation(payload: AutomationRunRequest, x_cron_token: str | None = Header(default=None)):
    if not settings.CRON_ENABLED:
        raise HTTPException(status_code=503, detail="Automacao editorial desabilitada. Configure CRON_ENABLED=true.")
    if not settings.CRON_TOKEN:
        raise HTTPException(status_code=503, detail="CRON_TOKEN nao configurado no backend.")
    if not x_cron_token or not secrets.compare_digest(x_cron_token, settings.CRON_TOKEN):
        raise HTTPException(status_code=401, detail="Token da automacao invalido.")
    if not payload.dry_run and settings.CRON_DRY_RUN:
        raise HTTPException(
            status_code=409,
            detail="Execucao bloqueada por CRON_DRY_RUN=true. Valide a simulacao e altere a configuracao para executar.",
        )
    if payload.allow_unreviewed_publish and not settings.CRON_ALLOW_UNREVIEWED_PUBLISH:
        raise HTTPException(
            status_code=409,
            detail="Publicacao sem revisao bloqueada por CRON_ALLOW_UNREVIEWED_PUBLISH=false.",
        )
    try:
        return editorial_cron_service.run(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro ao executar automacao editorial: {exc}")
