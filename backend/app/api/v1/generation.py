from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.generation_service import generation_service
from app.repositories.article_repository import article_repo
from app.schemas.article import ArticleDraftResponse

router = APIRouter()

@router.post("/{pauta_id}/generate", response_model=ArticleDraftResponse)
def generate_article(pauta_id: int, db: Session = Depends(get_db)):
    """
    Dispara o fluxo de geração com IA para uma pauta.
    1. Planejamento
    2. Redação
    """
    try:
        draft = generation_service.generate_article_flow(db, pauta_id=pauta_id)
        return draft
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na geração: {str(e)}")

@router.get("/{pauta_id}/draft", response_model=ArticleDraftResponse)
def get_article_draft(pauta_id: int, db: Session = Depends(get_db)):
    """Buscar o rascunho gerado para uma pauta"""
    draft = article_repo.get_by_pauta_id(db, pauta_id=pauta_id)
    if not draft:
        raise HTTPException(status_code=404, detail="Rascunho não encontrado para esta pauta.")
    return draft
