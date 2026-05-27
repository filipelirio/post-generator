import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS configurado para %s", settings.cors_origins)


@app.on_event("startup")
async def startup_event():
    logger.info("%s iniciado; API v1 em %s", settings.PROJECT_NAME, settings.API_V1_STR)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Gerador de Artigos AI esta rodando!"}


logger.info("Carregando rotas da API em %s", settings.API_V1_STR)
app.include_router(api_router, prefix=settings.API_V1_STR)
