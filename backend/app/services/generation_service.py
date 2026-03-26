from sqlalchemy.orm import Session
from app.repositories.pauta_repository import pauta_repo
from app.repositories.article_repository import article_repo
from app.integrations.gemini import gemini_client
from app.models.pauta import PautaStatus
from app.schemas.article import ArticleDraftCreate
import json

class GenerationService:
    def generate_article_flow(self, db: Session, pauta_id: int):
        """
        Executa o fluxo completo de geração com IA:
        1. Planejamento (Planner)
        2. Redação (Writer)
        """
        # 1. Buscar Pauta
        pauta = pauta_repo.get(db, id=pauta_id)
        if not pauta:
            raise ValueError("Pauta não encontrada.")

        # Converter pauta para dict dinamicamente (todos os campos do modelo)
        pauta_dict = {
            c.name: getattr(pauta, c.name) or "" 
            for c in pauta.__table__.columns 
            if c.name not in ["id", "created_at", "updated_at"]
        }

        try:
            # 2. Etapa 1: Planejamento Editorial
            plan = gemini_client.generate_plan(pauta_data=pauta_dict)

            # 3. Criar ou Atualizar ArticleDraft
            draft = article_repo.get_by_pauta_id(db, pauta_id=pauta_id)
            draft_data = {
                "pauta_id": pauta_id,
                "editorial_strategy": plan.editorial_strategy,
                "seo_title": plan.seo_title,
                "human_title": plan.human_title,
                "slug": plan.slug,
                "meta_title": plan.meta_title,
                "meta_description": plan.meta_description,
                "excerpt": plan.excerpt,
                "outline": plan.outline
            }

            if not draft:
                draft = article_repo.create(db, obj_in=ArticleDraftCreate(**draft_data))
            else:
                draft = article_repo.update(db, db_obj=draft, obj_in=draft_data)

            # 4. Etapa 2: Redação do Artigo
            article = gemini_client.generate_article(plan=plan, pauta_data=pauta_dict)

            # Converter FAQ para JSON String para salvar no banco
            faq_list = [item.model_dump() for item in article.faq_json]
            faq_str = json.dumps(faq_list, ensure_ascii=False)

            # Atualizar Draft com conteúdo
            update_data = {
                "article_html": article.article_html,
                "faq_json": faq_str,
                "cta": article.cta,
                "internal_link_suggestions": article.internal_link_suggestions,
                "external_link_suggestions": article.external_link_suggestions,
                "cover_image_prompt": article.cover_image_prompt,
                "cover_image_alt": article.cover_image_alt
            }
            draft = article_repo.update(db, db_obj=draft, obj_in=update_data)

            # 5. Criar Versão do Histórico
            # Descobrir número da versão
            versions = article_repo.get_versions(db, draft_id=draft.id)
            next_version = len(versions) + 1

            version_in = {
                "draft_id": draft.id,
                "version_number": next_version,
                "article_html": article.article_html,
                "meta_description": plan.meta_description,
                "faq_json": faq_str,
                "ai_response_raw": json.dumps(article.model_dump(), ensure_ascii=False) # Log retroativo
            }
            article_repo.create_version(db, version_in=version_in)

            # 6. Atualizar Status da Pauta
            pauta_repo.update(db, db_obj=pauta, obj_in={"status": PautaStatus.GERADA})

            return draft

        except Exception as e:
            # Se falhar, registra o erro na pauta
            pauta_repo.update(db, db_obj=pauta, obj_in={
                "status": PautaStatus.ERRO,
                "error_message": str(e)
            })
            raise e

# Instância global
generation_service = GenerationService()
