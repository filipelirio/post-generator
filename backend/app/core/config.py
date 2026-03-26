from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Gerador de Artigos AI"
    API_V1_STR: str = "/api/v1"
    
    # ---- BANCO DE DADOS ----
    # SQLite hospedado na pasta /data no projeto
    DATABASE_URL: str = "sqlite:///../../data/app.db"

    # ---- GEMINI API ----
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.1-flash"

    # ---- WORDPRESS ----
    WORDPRESS_URL: str = "https://easymedicina.com"
    WORDPRESS_USERNAME: str = "seu_usuario"
    WORDPRESS_APPLICATION_PASSWORD: str = ""
    DEFAULT_POST_STATUS: str = "draft"

    # ---- OUTROS ----
    LOG_LEVEL: str = "INFO"

    model_config = ConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore" # ignora variáveis extras no .env
    )

# Instância global de configurações
settings = Settings()
