from pathlib import Path
from typing import Literal

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


CONFIG_DIR = Path(__file__).resolve().parent
APP_DIR = CONFIG_DIR.parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
ROOT_ENV_FILE = PROJECT_ROOT / ".env"
BACKEND_ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    PROJECT_NAME: str = "Motor Editorial AI"
    API_V1_STR: str = "/api/v1"

    BASE_DIR: str = str(BACKEND_DIR)

    OPENAI_API_KEY: str | None = None
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

    CLIENT_INSTRUCTIONS_PATH: str = str(PROJECT_ROOT / "references" / "client_instructions.md")
    SEO_GUIDELINES_PATH: str = str(PROJECT_ROOT / "references" / "seo_guidelines.md")
    GENERATE_PAUTAS_PROMPT_PATH: str = str(PROJECT_ROOT / "references" / "prompt_generate_pautas.md")
    GENERATE_ARTICLE_PROMPT_PATH: str = str(PROJECT_ROOT / "references" / "prompt_generate_article.md")

    WORDPRESS_URL: str = ""
    WORDPRESS_USERNAME: str = "seu_usuario"
    WORDPRESS_APPLICATION_PASSWORD: str = ""
    DEFAULT_POST_STATUS: str = "draft"

    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = ",".join(
        f"http://localhost:{port}" for port in range(3000, 3006)
    )
    CRON_ENABLED: bool = False
    CRON_TOKEN: str = ""
    CRON_MODE: Literal["generate_only", "draft", "publish"] = "generate_only"
    CRON_MAX_ITEMS: int = 1
    CRON_SCHEDULE: str = "0 7 * * 1-5"
    CRON_DRY_RUN: bool = True
    CRON_ALLOW_UNREVIEWED_PUBLISH: bool = False

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    model_config = ConfigDict(
        env_file=(str(ROOT_ENV_FILE), str(BACKEND_ENV_FILE)),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
