import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict

from app.core.config import ROOT_ENV_FILE, settings
from app.integrations.wordpress import wordpress_client
from app.schemas.editorial import EditorialConfigurationResponse, EditorialConfigurationUpdateRequest
from app.services.openai_editorial_service import openai_editorial_service
from app.services.openai_image_service import openai_image_service


class EditorialConfigurationService:
    DOCUMENT_FIELDS = {
        "client_instructions": "CLIENT_INSTRUCTIONS_PATH",
        "seo_guidelines": "SEO_GUIDELINES_PATH",
        "prompt_generate_pautas": "GENERATE_PAUTAS_PROMPT_PATH",
        "prompt_generate_article": "GENERATE_ARTICLE_PROMPT_PATH",
    }

    ENV_FIELDS = {
        "OPENAI_MODEL": "openai_model",
        "OPENAI_IMAGE_MODEL": "openai_image_model",
        "OPENAI_IMAGE_SIZE": "openai_image_size",
        "OPENAI_IMAGE_QUALITY": "openai_image_quality",
        "OPENAI_WEBSEARCH_ENABLED": "openai_websearch_enabled",
        "WORDPRESS_URL": "wordpress_url",
        "WORDPRESS_USERNAME": "wordpress_username",
        "CRON_ENABLED": "cron_enabled",
        "CRON_MODE": "cron_mode",
        "CRON_MAX_ITEMS": "cron_max_items",
        "CRON_SCHEDULE": "cron_schedule",
        "CRON_DRY_RUN": "cron_dry_run",
        "CRON_ALLOW_UNREVIEWED_PUBLISH": "cron_allow_unreviewed_publish",
    }

    def __init__(self, env_path: Path | None = None) -> None:
        self.env_path = env_path or ROOT_ENV_FILE

    def _read_document(self, setting_name: str) -> str:
        path = Path(getattr(settings, setting_name))
        return path.read_text(encoding="utf-8") if path.exists() else ""

    def _backup_document(self, path: Path) -> None:
        if not path.exists():
            return
        backup_dir = Path(settings.BACKUPS_DIR) / "configuration"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        shutil.copy2(path, backup_dir / f"{path.stem}_{timestamp}{path.suffix}")

    def _write_document(self, path: Path, content: str) -> None:
        self._backup_document(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip() + "\n", encoding="utf-8")

    @staticmethod
    def _env_value(value: object) -> str:
        if isinstance(value, bool):
            value = "true" if value else "false"
        text = str(value)
        if "\n" in text or "\r" in text:
            raise ValueError("Valores de configuracao nao podem conter quebra de linha.")
        escaped = text.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    def _write_env_updates(self, updates: Dict[str, object]) -> None:
        existing_lines = self.env_path.read_text(encoding="utf-8").splitlines() if self.env_path.exists() else []
        pending = dict(updates)
        output: list[str] = []
        for line in existing_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in line:
                key = line.split("=", 1)[0].strip()
                if key in pending:
                    output.append(f"{key}={self._env_value(pending.pop(key))}")
                    continue
            output.append(line)
        if pending and output and output[-1].strip():
            output.append("")
        output.extend(f"{key}={self._env_value(value)}" for key, value in pending.items())
        self.env_path.parent.mkdir(parents=True, exist_ok=True)
        self.env_path.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")

    def get_configuration(self) -> EditorialConfigurationResponse:
        return EditorialConfigurationResponse(
            **{field: self._read_document(setting_name) for field, setting_name in self.DOCUMENT_FIELDS.items()},
            openai_api_key_configured=bool(settings.OPENAI_API_KEY),
            openai_model=settings.OPENAI_MODEL,
            openai_image_model=settings.OPENAI_IMAGE_MODEL,
            openai_image_size=settings.OPENAI_IMAGE_SIZE,
            openai_image_quality=settings.OPENAI_IMAGE_QUALITY,
            openai_websearch_enabled=settings.OPENAI_WEBSEARCH_ENABLED,
            wordpress_url=settings.WORDPRESS_URL,
            wordpress_username=settings.WORDPRESS_USERNAME,
            wordpress_application_password_configured=bool(settings.WORDPRESS_APPLICATION_PASSWORD),
            cron_enabled=settings.CRON_ENABLED,
            cron_token_configured=bool(settings.CRON_TOKEN),
            cron_mode=settings.CRON_MODE,
            cron_max_items=settings.CRON_MAX_ITEMS,
            cron_schedule=settings.CRON_SCHEDULE,
            cron_dry_run=settings.CRON_DRY_RUN,
            cron_allow_unreviewed_publish=settings.CRON_ALLOW_UNREVIEWED_PUBLISH,
        )

    def save_configuration(self, payload: EditorialConfigurationUpdateRequest) -> EditorialConfigurationResponse:
        required_placeholders = {
            "prompt_generate_pautas": ["[[CLIENT_INSTRUCTIONS]]", "[[SEO_PRINCIPLES]]", "[[COUNT]]"],
            "prompt_generate_article": ["[[CLIENT_INSTRUCTIONS]]", "[[SEO_PRINCIPLES]]", "[[PAUTA_CONTEXT]]"],
        }
        for field, placeholders in required_placeholders.items():
            missing = [placeholder for placeholder in placeholders if placeholder not in getattr(payload, field)]
            if missing:
                raise ValueError(f"O prompt precisa manter os placeholders: {', '.join(missing)}.")

        for field, setting_name in self.DOCUMENT_FIELDS.items():
            self._write_document(Path(getattr(settings, setting_name)), getattr(payload, field))

        env_updates: Dict[str, object] = {
            env_name: getattr(payload, payload_name) for env_name, payload_name in self.ENV_FIELDS.items()
        }
        if payload.openai_api_key and payload.openai_api_key.strip():
            env_updates["OPENAI_API_KEY"] = payload.openai_api_key.strip()
        if payload.wordpress_application_password and payload.wordpress_application_password.strip():
            env_updates["WORDPRESS_APPLICATION_PASSWORD"] = payload.wordpress_application_password.strip()
        if payload.cron_token and payload.cron_token.strip():
            env_updates["CRON_TOKEN"] = payload.cron_token.strip()
        self._write_env_updates(env_updates)

        for env_name, payload_name in self.ENV_FIELDS.items():
            setattr(settings, env_name, getattr(payload, payload_name))
        if "OPENAI_API_KEY" in env_updates:
            settings.OPENAI_API_KEY = str(env_updates["OPENAI_API_KEY"])
        if "WORDPRESS_APPLICATION_PASSWORD" in env_updates:
            settings.WORDPRESS_APPLICATION_PASSWORD = str(env_updates["WORDPRESS_APPLICATION_PASSWORD"])
        if "CRON_TOKEN" in env_updates:
            settings.CRON_TOKEN = str(env_updates["CRON_TOKEN"])

        wordpress_client.reload_configuration()
        openai_editorial_service._client = None
        openai_image_service._client = None
        return self.get_configuration()


editorial_configuration_service = EditorialConfigurationService()
