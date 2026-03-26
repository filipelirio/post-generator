from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.integrations.wordpress import wordpress_client
from app.repositories.article_repository import article_repo
from app.repositories.pauta_repository import pauta_repo
from app.repositories.publication_repository import publication_repo
from app.models.pauta import PautaStatus
import json

router = APIRouter()

@router.post("/test-connection")
def test_connection():
    """Testa a conexão com o WordPress"""
    is_connected = wordpress_client.test_connection()
    if is_connected:
        return {"status": "success", "message": "Conectado ao WordPress com sucesso!"}
    raise HTTPException(status_code=400, detail="Falha na conexão com o WordPress. Verifique as credenciais.")

from datetime import datetime, timezone
import os

@router.post("/{pauta_id}/publish")
def publish_article(pauta_id: int, db: Session = Depends(get_db)):
    """Publica o artigo no WordPress com SEO (Yoast), Agendamento e Mídia"""
    pauta = pauta_repo.get(db, id=pauta_id)
    if not pauta:
        raise HTTPException(status_code=404, detail="Pauta não encontrada")
    
    draft = article_repo.get_by_pauta_id(db, pauta_id=pauta_id)
    if not draft or not draft.article_html:
        raise HTTPException(status_code=400, detail="Artigo não foi gerado ainda.")

    # 1. Preparar Categorias e Tags
    category_id = wordpress_client.get_or_create_category(pauta.categoria_wordpress or pauta.area)
    
    tag_ids = []
    if pauta.tags_wordpress:
        tags = [t.strip() for t in pauta.tags_wordpress.split(",") if t.strip()]
        for tag_name in tags:
            tid = wordpress_client.get_or_create_tag(tag_name)
            if tid: tag_ids.append(tid)

    # 2. Upload de Imagem de Capa (Featured Media)
    featured_media_id = None
    if draft.cover_image_url and os.path.exists(draft.cover_image_url):
        try:
            with open(draft.cover_image_url, "rb") as f:
                file_bytes = f.read()
                filename = os.path.basename(draft.cover_image_url)
                featured_media_id = wordpress_client.upload_media(file_bytes, filename)
        except Exception as e:
            print(f"Erro ao carregar imagem de capa: {e}")

    # 3. Lógica de Agendamento
    now = datetime.now() # Usando local conforme solicitado
    status = "draft"
    publish_date = None

    if pauta.data_planejada:
        if pauta.data_planejada > now:
            status = "future"
            publish_date = pauta.data_planejada.isoformat()
        else:
            status = "publish" # Se a data já passou, publica imediatamente

    # 4. Preparar Payload para o WordPress (com Yoast SEO)
    post_data = {
        "title": draft.human_title or draft.seo_title,
        "content": draft.article_html,
        "slug": draft.slug,
        "excerpt": draft.excerpt,
        "status": status,
        "categories": [category_id] if category_id else [],
        "tags": tag_ids,
        "meta": {
            "_yoast_wpseo_title": draft.meta_title or draft.human_title,
            "_yoast_wpseo_metadesc": draft.meta_description or draft.excerpt,
            "_yoast_wpseo_focuskw": pauta.palavra_chave_principal or ""
        }
    }

    if featured_media_id:
        post_data["featured_media"] = featured_media_id
    
    if publish_date:
        post_data["date"] = publish_date

    try:
        # 5. Criar/Agendar Post
        response = wordpress_client.create_post(post_data)
        
        # 6. Registrar Publicação no Banco
        publication_repo.create(db, obj_in={
            "pauta_id": pauta_id,
            "wordpress_post_id": response.get("id"),
            "wordpress_url": response.get("link"),
            "status": status,
            "raw_response_json": json.dumps(response, ensure_ascii=False)
        })

        # 7. Atualizar Status da Pauta
        pauta_repo.update(db, db_obj=pauta, obj_in={"status": PautaStatus.PUBLICADA})

        msg = "Artigo agendado para " + pauta.data_planejada.strftime("%d/%m/%Y %H:%M") if status == "future" else "Artigo publicado com sucesso!"
        
        return {
            "status": "success",
            "message": msg,
            "url": response.get("link"),
            "wp_status": status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao publicar: {str(e)}")
