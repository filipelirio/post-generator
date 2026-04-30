from pathlib import Path
from typing import Dict, List

from app.core.config import settings


class EditorialFileService:
    def __init__(self) -> None:
        self.base_dir = Path(settings.GENERATED_ARTICLES_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _read_text(self, path: Path) -> str:
        if not path.exists():
            raise FileNotFoundError(f"Arquivo nao encontrado: {path}")
        return path.read_text(encoding="utf-8")

    def _parse_key_values(self, text: str) -> Dict[str, str]:
        data: Dict[str, str] = {}
        for line in text.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                data[key.strip().upper()] = value.strip()
        return data

    def _parse_list_section(self, text: str, section_name: str) -> List[str]:
        lines = text.splitlines()
        section_header = f"{section_name.upper()}:"
        items: List[str] = []
        collecting = False
        for raw_line in lines:
            line = raw_line.strip()
            if not collecting and line.upper() == section_header:
                collecting = True
                continue
            if collecting:
                if not line:
                    continue
                if line.endswith(":") and not line.startswith("- "):
                    break
                if line.startswith("- "):
                    items.append(line[2:].strip())
        return items

    def _parse_article(self, text: str) -> Dict[str, str]:
        result: Dict[str, str] = {}
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.upper().startswith("CONTEUDO:"):
                result["CONTEUDO"] = "\n".join(lines[i + 1:]).strip()
                break
            if ":" in line:
                key, _, value = line.partition(":")
                result[key.strip().upper()] = value.strip()
            i += 1
        return result

    def load_package(self, slug: str) -> Dict:
        article_path = self.base_dir / f"artigo_{slug}.txt"
        seo_path = self.base_dir / f"artigo_{slug}_seo.txt"
        image_path = self.base_dir / f"artigo_{slug}_imagem.txt"

        article = self._parse_article(self._read_text(article_path))
        seo_text = self._read_text(seo_path)
        seo = self._parse_key_values(seo_text)
        image = self._parse_key_values(self._read_text(image_path)) if image_path.exists() else {}

        tags = [tag.strip() for tag in seo.get("TAGS", "").split(",") if tag.strip()]
        return {
            "slug": seo.get("SLUG", slug),
            "pauta_id": article.get("PAUTA_ID", "") or seo.get("PAUTA_ID", ""),
            "title": article.get("TITULO", ""),
            "category": article.get("CATEGORIA", ""),
            "content_html": article.get("CONTEUDO", ""),
            "seo_title": seo.get("SEO_TITLE", ""),
            "meta_desc": seo.get("META_DESC", ""),
            "focus_kw": seo.get("FOCUS_KW", ""),
            "tags": tags,
            "internal_links": self._parse_list_section(seo_text, "INTERNAL_LINKS"),
            "external_links": self._parse_list_section(seo_text, "EXTERNAL_LINKS"),
            "product_mentions": self._parse_list_section(seo_text, "PRODUCT_MENTIONS"),
            "image": {
                "type": image.get("TIPO", "").lower(),
                "path": image.get("CAMINHO", ""),
                "url": image.get("URL", ""),
                "alt": image.get("ALT", ""),
                "prompt": image.get("PROMPT", ""),
                "short_theme": image.get("TEMA_CURTO", ""),
            },
        }

    def find_slug_by_pauta_id(self, pauta_id: str) -> str:
        for article_path in self.base_dir.glob("artigo_*.txt"):
            if article_path.name.endswith("_seo.txt") or article_path.name.endswith("_imagem.txt"):
                continue
            article = self._parse_article(self._read_text(article_path))
            current_pauta_id = article.get("PAUTA_ID", "").strip()
            if current_pauta_id == str(pauta_id):
                slug = article_path.stem.replace("artigo_", "", 1)
                return slug
        raise FileNotFoundError(f"Nenhum pacote gerado encontrado para a pauta {pauta_id}")

    def get_image_path(self, pauta_id: str) -> Path:
        slug = self.find_slug_by_pauta_id(pauta_id)
        package = self.load_package(slug)
        image_path = package.get("image", {}).get("path", "").strip()
        if not image_path:
            raise FileNotFoundError(f"Nenhuma imagem encontrada para a pauta {pauta_id}")
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Arquivo de imagem nao encontrado: {path}")
        return path


editorial_file_service = EditorialFileService()
