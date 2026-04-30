import json
import re
from datetime import datetime
from pathlib import Path
from typing import List

from openai import OpenAI

from app.core.config import settings
from app.schemas.editorial import GeneratePautasRequest, SheetPauta


class OpenAIEditorialService:
    def __init__(self) -> None:
        self._client = None
        self.references_dir = Path(settings.BASE_DIR).parent / "references"
        self.editorial_manual_path = self.references_dir / "manual_editorial_easy_medicina.md"
        self.seo_principles_path = self.references_dir / "principles-seo.md"
        self.generate_pautas_prompt_path = self.references_dir / "prompt_generate_pautas.md"
        self.generate_article_prompt_path = self.references_dir / "prompt_generate_article.md"

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

    def _editorial_manual(self) -> str:
        return self._load_reference(
            self.editorial_manual_path,
            "Manual editorial indisponivel. Mantenha tom direto, pratico, didatico e orientado a conversao para estudantes de medicina.",
        )

    def _seo_principles(self) -> str:
        return self._load_reference(
            self.seo_principles_path,
            "Principios de SEO indisponiveis. Priorize keyword principal no titulo, introducao, H2, meta description, slug, links internos e links externos confiaveis.",
        )

    def generate_pautas(self, request: GeneratePautasRequest, existing_pautas: List[SheetPauta], next_id: int) -> List[SheetPauta]:
        client = self._get_client()
        existing_keywords = [p.palavra_chave_principal for p in existing_pautas if p.palavra_chave_principal][:200]
        existing_topics = [p.tema for p in existing_pautas if p.tema][:200]
        editorial_manual = self._editorial_manual()
        seo_principles = self._seo_principles()
        prompt = self._render_prompt_template(
            self.generate_pautas_prompt_path,
            fallback=(
                "Voce e o editor-chefe SEO do blog Easy Medicina.\n"
                "Use o manual editorial e os principios de SEO abaixo como base obrigatoria.\n\n"
                "[[EDITORIAL_MANUAL]]\n\n[[SEO_PRINCIPLES]]\n\n"
                "Crie [[COUNT]] pautas novas sem duplicar [[EXISTING_KEYWORDS]] ou [[EXISTING_TOPICS]].\n"
                "Categoria forcada: [[FORCE_CATEGORY]]\n"
                "Observacoes extras: [[NOTES]]\n"
                "Responda apenas em JSON no formato {{\"pautas\": [...]}}."
            ),
            variables={
                "COUNT": str(request.count),
                "EDITORIAL_MANUAL": editorial_manual,
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
                        "Tema": item.get("tema", ""),
                        "Titulo sugerido": item.get("titulo_sugerido", ""),
                        "Categoria": item.get("categoria", request.force_category or ""),
                        "Palavra-chave principal": item.get("palavra_chave_principal", ""),
                        "Palavras-chave secundarias": item.get("palavras_chave_secundarias", ""),
                        "Volume de busca": item.get("volume_de_busca", ""),
                        "Dificuldade SEO": item.get("dificuldade_seo", ""),
                        "Intencao de busca": item.get("intencao_de_busca", ""),
                        "Posicao no funil": item.get("posicao_no_funil", ""),
                        "CTA sugerido": item.get("cta_sugerido", ""),
                        "Produto sugerido": item.get("produto_sugerido", ""),
                        "Tamanho recomendado": item.get("tamanho_recomendado", ""),
                        "Topicos obrigatorios": item.get("topicos_obrigatorios", ""),
                        "Topicos proibidos": item.get("topicos_proibidos", ""),
                        "Observacoes editoriais": item.get("observacoes_editoriais", ""),
                        "SEO rationale": item.get("seo_rationale", ""),
                        "Data criacao": created_at,
                    }
                )
            )
        return pautas

    def generate_article_package(self, pauta: SheetPauta) -> dict:
        client = self._get_client()
        editorial_manual = self._editorial_manual()
        seo_principles = self._seo_principles()
        prompt = self._render_prompt_template(
            self.generate_article_prompt_path,
            fallback=(
                "Voce e o editor do blog Easy Medicina.\n"
                "Use o manual editorial e os principios de SEO abaixo como base obrigatoria.\n\n"
                "[[EDITORIAL_MANUAL]]\n\n[[SEO_PRINCIPLES]]\n\n"
                "Pauta:\n[[PAUTA_CONTEXT]]\n\n"
                "Responda apenas em JSON com slug, titulo, conteudo_html, seo_title, meta_desc, focus_kw, tags, "
                "internal_links, external_links, product_mentions, imagem_prompt, imagem_tema_curto, imagem_alt e preview_html."
            ),
            variables={
                "EDITORIAL_MANUAL": editorial_manual,
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
