from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base # Importa de base para garantir que todos os modelos sejam conhecidos
from app.api.v1.api import api_router

# Cria as tabelas no SQLite se não existirem
try:
    print(f"DEBUG: Conectando ao banco em {settings.DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    print("DEBUG: Banco de dados inicializado com sucesso.")
except Exception as e:
    print(f"ERRO CRÍTICO NA INICIALIZAÇÃO DO BANCO: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configurar CORS para o Frontend Next.js
# Em desenvolvimento local, permitimos tudo para evitar "Network Error" (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("DEBUG: CORS configurado com permissões globais [*]")

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Gerador de Artigos AI está rodando!"}

# Incluir Rotas
app.include_router(api_router, prefix=settings.API_V1_STR)
