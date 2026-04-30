import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path

from app.core.config import settings


class ArticlePackageService:
    def __init__(self) -> None:
        self.base_dir = Path(settings.GENERATED_ARTICLES_DIR)
        self.backup_dir = Path(settings.ARTICLE_BACKUPS_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _slugify(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        normalized = re.sub(r"[^a-zA-Z0-9\s-]", "", normalized).strip().lower()
        normalized = re.sub(r"[\s-]+", "-", normalized)
        return normalized or "artigo"

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _snapshot_package(self, slug: str, files: list[Path], image_path: str = "") -> None:
        version_dir = self.backup_dir / slug / self._timestamp()
        version_dir.mkdir(parents=True, exist_ok=True)
        for file_path in files:
            if file_path.exists():
                shutil.copy2(file_path, version_dir / file_path.name)
        if image_path:
            image_file = Path(image_path)
            if image_file.exists():
                shutil.copy2(image_file, version_dir / image_file.name)

    def write_package(self, payload: dict) -> dict:
        slug = self._slugify(payload["slug"])
        article_file = self.base_dir / f"artigo_{slug}.txt"
        seo_file = self.base_dir / f"artigo_{slug}_seo.txt"
        image_file = self.base_dir / f"artigo_{slug}_imagem.txt"
        internal_links = payload.get("internal_links", [])
        external_links = payload.get("external_links", [])
        product_mentions = payload.get("product_mentions", [])

        article_file.write_text(
            "\n".join(
                [
                    f"PAUTA_ID: {payload.get('pauta_id', '')}",
                    f"TITULO: {payload['titulo']}",
                    f"CATEGORIA: {payload.get('categoria', '')}",
                    "CONTEUDO:",
                    payload["conteudo_html"],
                ]
            ),
            encoding="utf-8",
        )
        seo_file.write_text(
            "\n".join(
                [
                    f"PAUTA_ID: {payload.get('pauta_id', '')}",
                    f"SEO_TITLE: {payload['seo_title']}",
                    f"META_DESC: {payload['meta_desc']}",
                    f"FOCUS_KW: {payload['focus_kw']}",
                    f"SLUG: {slug}",
                    f"TAGS: {', '.join(payload.get('tags', []))}",
                    "INTERNAL_LINKS:",
                    *[
                        f"- {item.get('anchor', '').strip()} | {item.get('url', '').strip()}"
                        for item in internal_links
                        if item.get("url")
                    ],
                    "EXTERNAL_LINKS:",
                    *[
                        f"- {item.get('anchor', '').strip()} | {item.get('url', '').strip()}"
                        for item in external_links
                        if item.get("url")
                    ],
                    "PRODUCT_MENTIONS:",
                    *[
                        f"- {item.get('product', '').strip()} | {item.get('url', '').strip()} | {item.get('reason', '').strip()}"
                        for item in product_mentions
                        if item.get("product")
                    ],
                ]
            ),
            encoding="utf-8",
        )
        image_file.write_text(
            "\n".join(
                [
                    f"TIPO: {payload.get('imagem_tipo', 'local')}",
                    f"CAMINHO: {payload.get('imagem_caminho', '')}",
                    f"URL: {payload.get('imagem_url', '')}",
                    f"TEMA_CURTO: {payload.get('imagem_tema_curto', '')}",
                    f"PROMPT: {payload.get('imagem_prompt', '')}",
                    f"ALT: {payload.get('imagem_alt', '')}",
                ]
            ),
            encoding="utf-8",
        )
        self._snapshot_package(
            slug=slug,
            files=[article_file, seo_file, image_file],
            image_path=payload.get("imagem_caminho", ""),
        )
        return {
            "slug": slug,
            "article_file": str(article_file),
            "seo_file": str(seo_file),
            "image_file": str(image_file),
        }


article_package_service = ArticlePackageService()
