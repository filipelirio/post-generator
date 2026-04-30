import base64
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Optional

from openai import OpenAI

from app.core.config import settings


class OpenAIImageService:
    def __init__(self) -> None:
        self._client: Optional[OpenAI] = None
        self.base_dir = Path(settings.GENERATED_IMAGES_DIR)
        self.backup_dir = Path(settings.IMAGE_BACKUPS_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _get_client(self) -> OpenAI:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY nao configurada")
        if self._client is None:
            self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    def _slugify(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        normalized = re.sub(r"[^a-zA-Z0-9\s-]", "", normalized).strip().lower()
        normalized = re.sub(r"[\s-]+", "-", normalized)
        return normalized or "artigo"

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def generate_cover(self, slug: str, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt de imagem vazio")

        client = self._get_client()
        response = client.images.generate(
            model=settings.OPENAI_IMAGE_MODEL,
            prompt=prompt,
            size=settings.OPENAI_IMAGE_SIZE,
            quality=settings.OPENAI_IMAGE_QUALITY,
            output_format="png",
        )

        if not response.data:
            raise ValueError("A API de imagem nao retornou dados")

        image = response.data[0]
        image_b64 = getattr(image, "b64_json", None)
        if not image_b64:
            raise ValueError("A resposta da imagem nao trouxe b64_json")

        file_path = self.base_dir / f"capa_{self._slugify(slug)}.png"
        file_path.write_bytes(base64.b64decode(image_b64))
        backup_path = self.backup_dir / f"{file_path.stem}_{self._timestamp()}{file_path.suffix}"
        shutil.copy2(file_path, backup_path)
        return str(file_path)


openai_image_service = OpenAIImageService()
