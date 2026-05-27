import json
import re
from datetime import datetime
from pathlib import Path
from typing import List

from openai import OpenAI

from app.core.config import settings
from app.schemas.editorial import GeneratePautasRequest, SheetPauta
from app.services.html_sanitizer_service import sanitize_html


class OpenAIEditorialService:
    def __init__(self) -> None:
        self._client = None
        self.client_instructions_path = Path(settings.CLIENT_INSTRUCTIONS_PATH)
        self.seo_principles_path = Path(settings.SEO_GUIDELINES_PATH)
        self.generate_pautas_prompt_path = Path(settings.GENERATE_PAUTAS_PROMPT_PATH)
        self.generate_article_prompt_path = Path(settings.GENERATE_ARTICLE_PROMPT_PATH)

    def _get_client(self) -> OpenAI:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY nao configurada")
        if self._client is None:
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    def _tools(self):
        if settings.OPENAI_WEBSEARCH_ENABLED:
            return [{"type": "web_search"}]
        return []

    def _extract_json(self, text: str):
        match = re.search(r"\{.*\}|\[.*\]", text, re.S)
        if not match:
            raise ValueError("Resposta do modelo nao trouxe JSON valido")
        return json.loads(match.group(0))

    def _normalize_text(self, value: str) -> str:
        normalized = re.sub(r"\s+", " ", (value or "").strip()).strip().lower()
        return normalized

    def _stringify_field(self, value) -> str:
        if value is None:
            return ""
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, (list, tuple)):
            cleaned = [self._stringify_field(item) for item in value]
            cleaned = [item for item in cleaned if item]
            return "; ".join(cleaned)
        if isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        return str(value).strip()

    def _strip_duplicate_leading_heading(self, html: str, title: str) -> str:
        if not html or not title:
            return html

        pattern = re.compile(r"^\s*<h[1-6][^>]*>(.*?)</h[1-6]>\s*", re.IGNORECASE | re.DOTALL)
        match = pattern.match(html)
        if not match:
            return html

        heading_text = re.sub(r"<[^>]+>", "", match.group(1))
        if self._normalize_text(heading_text) != self._normalize_text(title):
            return html

        return html[match.end():].lstrip()

    def _sanitize_article_payload(self, payload: dict) -> dict:
        title = payload.get("titulo", "")
        if title:
            payload["conteudo_html"] = self._strip_duplicate_leading_heading(payload.get("conteudo_html", ""), title)
            payload["preview_html"] = self._strip_duplicate_leading_heading(payload.get("preview_html", ""), title)
        payload["conteudo_html"] = sanitize_html(payload.get("conteudo_html", ""))
        payload["preview_html"] = sanitize_html(payload.get("preview_html", ""))
        return payload

    def _load_reference(self, path: Path, fallback: str) -> str:
        if path.exists():
            return path.read_text(encoding="utf-8")
        return fallback

    def _render_prompt_template(self, path: Path, fallback: str, variables: dict[str, str]) -> str:
        template = self._load_reference(path, fallback)
        rendered = template
        for key, value in variables.items():
            rendered = rendered.replace(f"[[{key}]]", value)
        return rendered

    def _client_instructions(self) -> str:
        return self._load_reference(
            self.client_instructions_path,
            "Instrucoes do cliente indisponiveis. Nao produza conteudo ate que marca, publico, oferta e tom editorial sejam definidos.",
        )

    def _seo_principles(self) -> str:
        return self._load_reference(
            self.seo_principles_path,
            "Diretrizes de SEO indisponiveis. Priorize keyword principal no titulo, introducao, H2, meta description, slug, links internos e links externos confiaveis.",
        )

    def generate_pautas(self, request: GeneratePautasRequest, existing_pautas: List[SheetPauta], next_id: int) -> List[SheetPauta]:
        client = self._get_client()
        existing_keywords = [p.palavra_chave_principal for p in existing_pautas if p.palavra_chave_principal][:200]
        existing_topics = [p.tema for p in existing_pautas if p.tema][:200]
        client_instructions = self._client_instructions()
        seo_principles = self._seo_principles()
        prompt = self._render_prompt_template(
            self.generate_pautas_prompt_path,
            fallback=(
                "Voce e o editor-chefe SEO do blog descrito nas instrucoes do cliente.\n"
                "Use as instrucoes do cliente e as diretrizes de SEO abaixo como base obrigatoria.\n\n"
                "[[CLIENT_INSTRUCTIONS]]\n\n[[SEO_PRINCIPLES]]\n\n"
                "Crie [[COUNT]] pautas novas sem duplicar [[EXISTING_KEYWORDS]] ou [[EXISTING_TOPICS]].\n"
                "Categoria forcada: [[FORCE_CATEGORY]]\n"
                "Observacoes extras: [[NOTES]]\n"
                "Responda apenas em JSON no formato {{\"pautas\": [...]}}."
            ),
            variables={
                "COUNT": str(request.count),
                "CLIENT_INSTRUCTIONS": client_instructions,
                "SEO_PRINCIPLES": seo_principles,
                "EXISTING_KEYWORDS": json.dumps(existing_keywords, ensure_ascii=False),
                "EXISTING_TOPICS": json.dumps(existing_topics, ensure_ascii=False),
                "FORCE_CATEGORY": request.force_category or "",
                "NOTES": request.notes or "",
            },
        )
        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            tools=self._tools(),
            input=prompt,
        )
        payload = self._extract_json(response.output_text)
        created_at = datetime.now().strftime("%Y-%m-%d")
        pautas = []
        for idx, item in enumerate(payload.get("pautas", []), start=0):
            pautas.append(
                SheetPauta(
                    **{
                        "ID": str(next_id + idx),
                        "Status": "Pendente",
                        "Prioridade": "Alta",
                        "Tema": self._stringify_field(item.get("tema", "")),
                        "Titulo sugerido": self._stringify_field(item.get("titulo_sugerido", "")),
                        "Categoria": self._stringify_field(item.get("categoria", request.force_category or "")),
                        "Palavra-chave principal": self._stringify_field(item.get("palavra_chave_principal", "")),
                        "Palavras-chave secundarias": self._stringify_field(item.get("palavras_chave_secundarias", "")),
                        "Volume de busca": self._stringify_field(item.get("volume_de_busca", "")),
                        "Dificuldade SEO": self._stringify_field(item.get("dificuldade_seo", "")),
                        "Intencao de busca": self._stringify_field(item.get("intencao_de_busca", "")),
                        "Posicao no funil": self._stringify_field(item.get("posicao_no_funil", "")),
                        "CTA sugerido": self._stringify_field(item.get("cta_sugerido", "")),
                        "Produto sugerido": self._stringify_field(item.get("produto_sugerido", "")),
                        "Tamanho recomendado": self._stringify_field(item.get("tamanho_recomendado", "")),
                        "Topicos obrigatorios": self._stringify_field(item.get("topicos_obrigatorios", "")),
                        "Topicos proibidos": self._stringify_field(item.get("topicos_proibidos", "")),
                        "Observacoes editoriais": self._stringify_field(item.get("observacoes_editoriais", "")),
                        "SEO rationale": self._stringify_field(item.get("seo_rationale", "")),
                        "Data criacao": created_at,
                    }
                )
            )
        return pautas

    def generate_article_package(self, pauta: SheetPauta) -> dict:
        client = self._get_client()
        client_instructions = self._client_instructions()
        seo_principles = self._seo_principles()
        prompt = self._render_prompt_template(
            self.generate_article_prompt_path,
            fallback=(
                "Voce e o editor do blog descrito nas instrucoes do cliente.\n"
                "Use as instrucoes do cliente e as diretrizes de SEO abaixo como base obrigatoria.\n\n"
                "[[CLIENT_INSTRUCTIONS]]\n\n[[SEO_PRINCIPLES]]\n\n"
                "Pauta:\n[[PAUTA_CONTEXT]]\n\n"
                "Responda apenas em JSON com slug, titulo, conteudo_html, seo_title, meta_desc, focus_kw, tags, "
                "internal_links, external_links, product_mentions, imagem_prompt, imagem_tema_curto, imagem_alt e preview_html."
            ),
            variables={
                "CLIENT_INSTRUCTIONS": client_instructions,
                "SEO_PRINCIPLES": seo_principles,
                "PAUTA_CONTEXT": "\n".join(
                    [
                        f"- ID: {pauta.id}",
                        f"- Tema: {pauta.tema}",
                        f"- Titulo sugerido: {pauta.titulo_sugerido}",
                        f"- Categoria: {pauta.categoria}",
                        f"- Palavra-chave principal: {pauta.palavra_chave_principal}",
                        f"- Palavras-chave secundarias: {pauta.palavras_chave_secundarias}",
                        f"- Intencao de busca: {pauta.intencao_de_busca}",
                        f"- Funil: {pauta.posicao_no_funil}",
                        f"- CTA sugerido: {pauta.cta_sugerido}",
                        f"- Produto sugerido: {pauta.produto_sugerido}",
                        f"- Tamanho recomendado: {pauta.tamanho_recomendado}",
                        f"- Topicos obrigatorios: {pauta.topicos_obrigatorios}",
                        f"- Topicos proibidos: {pauta.topicos_proibidos}",
                        f"- Observacoes editoriais: {pauta.observacoes_editoriais}",
                        f"- Rationale SEO: {pauta.seo_rationale}",
                    ]
                ),
            },
        )
        response = client.responses.create(
            model=settings.OPENAI_MODEL,
            tools=self._tools(),
            input=prompt,
        )
        return self._sanitize_article_payload(self._extract_json(response.output_text))


openai_editorial_service = OpenAIEditorialService()
