from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("DEBUG: CORS configurado com permissoes globais [*]")


@app.on_event("startup")
async def startup_event():
    print("==========================================")
    print(f"STARTUP: {settings.PROJECT_NAME} iniciado")

    print(f"DEBUG: API v1 em {settings.API_V1_STR}")
    print("==========================================")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Gerador de Artigos AI esta rodando!"}


print(f"DEBUG: Carregando rotas da API em {settings.API_V1_STR}...")
app.include_router(api_router, prefix=settings.API_V1_STR)
