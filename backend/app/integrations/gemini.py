from google import genai
from pydantic import BaseModel
from app.core.config import settings
from app.schemas.gemini_response import PlannerResponse, WriterResponse, RevisionResponse
import os

class GeminiClient:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY não configurada no .env")
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

    def _get_prompt_template(self, filename: str) -> str:
        """Lê o arquivo de prompt da pasta app/prompts/"""
        # Caminho absoluto para evitar erros
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_path = os.path.join(current_dir, "prompts", filename)
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_plan(self, pauta_data: dict) -> PlannerResponse:
        """Etapa 1: Planejamento Editorial"""
        template = self._get_prompt_template("planner_prompt.txt")
        # Injetar variáveis no template
        prompt = template.format(**pauta_data)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=dict(
                response_mime_type="application/json",
                response_schema=PlannerResponse,
                temperature=0.7 # Mais criativo para títulos
            ),
        )
        
        # O SDK já retorna o objeto parseado se usarmos response_schema?
        # Sim, o response.text será um JSON válido.
        return PlannerResponse.model_validate_json(response.text)

    def generate_article(self, plan: PlannerResponse, pauta_data: dict) -> WriterResponse:
        """Etapa 2: Redação do Artigo"""
        template = self._get_prompt_template("writer_prompt.txt")
        
        # Combinar dados do planejamento e todos os dados da pauta
        context = {
            **pauta_data,
            "human_title": plan.human_title,
            "seo_title": plan.seo_title,
            "editorial_strategy": plan.editorial_strategy,
            "outline": plan.outline
        }
        
        prompt = template.format(**context)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=dict(
                response_mime_type="application/json",
                response_schema=WriterResponse,
                temperature=0.5 # Mais conservador para redação técnica/médica
            ),
        )
        return WriterResponse.model_validate_json(response.text)

    def generate_revision(self, article_html: str, plan: PlannerResponse) -> RevisionResponse:
        """Etapa 3: Revisão e SEO"""
        template = self._get_prompt_template("revision_prompt.txt")
        
        context = {
            "article_html": article_html,
            "meta_description": plan.meta_description,
            "excerpt": plan.excerpt
        }
        
        prompt = template.format(**context)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=dict(
                response_mime_type="application/json",
                response_schema=RevisionResponse,
                temperature=0.3 # Mais focado em correção
            ),
        )
        return RevisionResponse.model_validate_json(response.text)

# Instância global
gemini_client = GeminiClient()
