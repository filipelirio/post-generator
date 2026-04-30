import os
from pathlib import Path
from typing import Optional

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


CONFIG_DIR = Path(__file__).resolve().parent
APP_DIR = CONFIG_DIR.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
ROOT_ENV_FILE = PROJECT_ROOT / ".env"
BACKEND_ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Gerador de Artigos AI"
    API_V1_STR: str = "/api/v1"

    BASE_DIR: str = str(BACKEND_DIR)
    DATABASE_URL: str = f"sqlite:///{BACKEND_DIR / 'data' / 'app.db'}"

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.1-flash"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-5"
    OPENAI_IMAGE_MODEL: str = "gpt-image-1"
    OPENAI_IMAGE_SIZE: str = "1536x1024"
    OPENAI_IMAGE_QUALITY: str = "medium"
    OPENAI_WEBSEARCH_ENABLED: bool = True

    EXCEL_PAUTAS_PATH: str = str(BACKEND_DIR / "data" / "editorial_pautas.xlsx")
    EXCEL_PAUTAS_SHEET_NAME: str = "Pautas"

    GENERATED_ARTICLES_DIR: str = str(BACKEND_DIR / "data" / "generated_articles")
    GENERATED_IMAGES_DIR: str = str(BACKEND_DIR / "data" / "generated_images")
    BACKUPS_DIR: str = str(BACKEND_DIR / "data" / "backups")
    EXCEL_BACKUPS_DIR: str = str(BACKEND_DIR / "data" / "backups" / "excel")
    ARTICLE_BACKUPS_DIR: str = str(BACKEND_DIR / "data" / "backups" / "articles")
    IMAGE_BACKUPS_DIR: str = str(BACKEND_DIR / "data" / "backups" / "images")

    WORDPRESS_URL: str = "https://easymedicina.com"
    WORDPRESS_USERNAME: str = "seu_usuario"
    WORDPRESS_APPLICATION_PASSWORD: str = ""
    DEFAULT_POST_STATUS: str = "draft"

    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(
        env_file=(str(ROOT_ENV_FILE), str(BACKEND_ENV_FILE)),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
