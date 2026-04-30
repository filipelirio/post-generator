from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


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

    try:
        print(f"DEBUG: Inicializando tabelas em {settings.DATABASE_URL}...")
        Base.metadata.create_all(bind=engine)
        print("DEBUG: Banco de dados pronto.")
    except Exception as exc:
        print(f"ERRO AO INICIALIZAR BANCO: {exc}")
        print("O servidor continuara rodando, mas chamadas ao banco podem falhar.")

    print(f"DEBUG: API v1 em {settings.API_V1_STR}")
    print(f"DEBUG: DB em {settings.DATABASE_URL}")
    print("==========================================")


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Gerador de Artigos AI esta rodando!"}


print(f"DEBUG: Carregando rotas da API em {settings.API_V1_STR}...")
app.include_router(api_router, prefix=settings.API_V1_STR)
