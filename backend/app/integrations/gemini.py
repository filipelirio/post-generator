import os

from google import genai

from app.core.config import settings
from app.schemas.gemini_response import PlannerResponse, RevisionResponse, WriterResponse


class GeminiClient:
    def __init__(self):
        self.client = None
        self.model = settings.GEMINI_MODEL

    def _get_client(self):
        if self.client is None:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY nao configurada no .env")
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self.client

    def _get_prompt_template(self, filename: str) -> str:
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        prompt_path = os.path.join(current_dir, "prompts", filename)
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_plan(self, pauta_data: dict) -> PlannerResponse:
        template = self._get_prompt_template("planner_prompt.txt")
        prompt = template.format(**pauta_data)
        client = self._get_client()

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=dict(
                response_mime_type="application/json",
                response_schema=PlannerResponse,
                temperature=0.7,
            ),
        )
        return PlannerResponse.model_validate_json(response.text)

    def generate_article(self, plan: PlannerResponse, pauta_data: dict) -> WriterResponse:
        template = self._get_prompt_template("writer_prompt.txt")
        context = {
            **pauta_data,
            "human_title": plan.human_title,
            "seo_title": plan.seo_title,
            "editorial_strategy": plan.editorial_strategy,
            "outline": plan.outline,
        }
        prompt = template.format(**context)
        client = self._get_client()

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=dict(
                response_mime_type="application/json",
                response_schema=WriterResponse,
                temperature=0.5,
            ),
        )
        return WriterResponse.model_validate_json(response.text)

    def generate_revision(self, article_html: str, plan: PlannerResponse) -> RevisionResponse:
        template = self._get_prompt_template("revision_prompt.txt")
        context = {
            "article_html": article_html,
            "meta_description": plan.meta_description,
            "excerpt": plan.excerpt,
        }
        prompt = template.format(**context)
        client = self._get_client()

        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=dict(
                response_mime_type="application/json",
                response_schema=RevisionResponse,
                temperature=0.3,
            ),
        )
        return RevisionResponse.model_validate_json(response.text)


gemini_client = GeminiClient()
